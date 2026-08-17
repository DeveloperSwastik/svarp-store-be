"""
Store BFF (Backend For Frontend) — API Gateway / Orchestrator.
Routes all requests to the appropriate microservice.
Never stores business data locally.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.middleware.logging import LoggingMiddleware
from app.api import auth, products, payments, orders, coupons, admin

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("store-bff")

# Rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Store BFF starting — connecting to microservices")
    yield
    # Cleanup HTTP clients
    from app.clients.inventory_client import inventory_client
    from app.clients.payment_client import payment_client
    from app.clients.order_client import order_client
    from app.clients.coupon_client import coupon_client
    from app.clients.user_portal_client import user_portal_client
    await inventory_client.close()
    await payment_client.close()
    await order_client.close()
    await coupon_client.close()
    await user_portal_client.close()
    logger.info("Store BFF shutdown complete")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    lifespan=lifespan,
)

# ─── Middleware ───
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)

# ─── Rate Limiting ───
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ─── Global Error Handler ───
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc) if settings.DEBUG else "An unexpected error occurred"},
    )

# ─── Routes ───
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(products.router, prefix=settings.API_V1_STR)
app.include_router(payments.router, prefix=settings.API_V1_STR)
app.include_router(orders.router, prefix=settings.API_V1_STR)
app.include_router(coupons.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)



# ─── Dynamic Sitemap XML ───
@app.get("/sitemap.xml", tags=["seo"])
async def get_sitemap(request: Request):
    from fastapi.responses import Response
    from app.clients.inventory_client import inventory_client
    
    req_host = str(request.base_url).rstrip('/')
    base_url = req_host if "localhost" not in req_host else "https://bodywellness.svarp.org"
    static_paths = ["", "/shop", "/about", "/mission", "/contact"]
    
    urls_xml = []
    for path in static_paths:
        urls_xml.append(f"""  <url>
    <loc>{base_url}{path}</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>""")
    
    try:
        products = await inventory_client.get_products()
        for p in products:
            p_id = p.get("id")
            if p_id:
                urls_xml.append(f"""  <url>
    <loc>{base_url}/product/{p_id}</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")
    except Exception as e:
        logger.warning(f"Could not fetch products for sitemap: {e}")

    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{"".join(urls_xml)}
</urlset>"""

    return Response(content=sitemap_content, media_type="application/xml")


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}


@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
