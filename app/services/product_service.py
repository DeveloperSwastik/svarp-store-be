"""
Product service — fetches and aggregates product data from the inventory portal.
Includes in-memory caching to reduce downstream load.
"""
from typing import Optional
from cachetools import TTLCache
from app.clients.inventory_client import inventory_client

# Cache products with 5s TTL to ensure real-time inventory stock synchronization
_product_cache = TTLCache(maxsize=500, ttl=5)


class ProductService:
    def _transform_product(self, product: dict) -> dict:
        """Enrich and normalize product data for frontend compatibility."""
        if not product:
            return product

        if "variants" in product and "real_variants" not in product:
            product["real_variants"] = product["variants"]

        from app.core.config import settings
        base_url = settings.INVENTORY_SERVICE_URL.replace("/api/v1", "").rstrip("/")

        if "images" in product and isinstance(product["images"], list):
            new_images = []
            for img in product["images"]:
                if img and img.startswith("/uploads/"):
                    new_images.append(f"{base_url}{img}")
                else:
                    new_images.append(img)
            product["images"] = new_images

        # Also copy first image to 'image' field if not present
        if "image" not in product and product.get("images"):
            product["image"] = product["images"][0]

        # Normalize variants images as well if they exist
        if "real_variants" in product and isinstance(product["real_variants"], list):
            for v in product["real_variants"]:
                if "images" in v and isinstance(v["images"], list):
                    new_v_images = []
                    for img in v["images"]:
                        if img and img.startswith("/uploads/"):
                            new_v_images.append(f"{base_url}{img}")
                        else:
                            new_v_images.append(img)
                    v["images"] = new_v_images
                if "image" not in v and v.get("images"):
                    v["image"] = v["images"][0]

        return product

    async def get_products(self, limit: int = 50, offset: int = 0) -> dict:
        """Fetch paginated products from inventory portal (with cache)."""
        cache_key = f"products:{limit}:{offset}"
        if cache_key in _product_cache:
            return _product_cache[cache_key]

        data = await inventory_client.get_products(limit=limit, offset=offset)
        
        # Transform each product
        if data and "items" in data:
            data["items"] = [self._transform_product(p) for p in data["items"]]

        _product_cache[cache_key] = data
        return data

    async def get_product(self, product_id: str) -> dict:
        """Fetch single product with stock info."""
        cache_key = f"product:{product_id}"
        if cache_key in _product_cache:
            return _product_cache[cache_key]

        product = await inventory_client.get_product(product_id)

        # Enrich with stock data
        try:
            stock = await inventory_client.get_stock(product_id)
            product["stock_quantity"] = stock.get("quantity", 0)
        except Exception:
            product["stock_quantity"] = None

        # Transform product
        product = self._transform_product(product)

        _product_cache[cache_key] = product
        return product

    async def search_products(self, query: str, limit: int = 50) -> list:
        """Search products by name/description (client-side filter for now)."""
        data = await self.get_products(limit=100, offset=0)
        items = data.get("items", [])
        q = query.lower()
        return [
            p for p in items
            if q in p.get("name", "").lower()
            or q in p.get("description", "").lower()
            or q in p.get("sku", "").lower()
        ]


product_service = ProductService()
