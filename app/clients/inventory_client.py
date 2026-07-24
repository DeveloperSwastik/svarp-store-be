"""
Client for the Inventory Portal microservice.
Fetches products, stock levels, and inventory data for the storefront.
"""
from typing import Optional
from app.clients.base import BaseClient
from app.core.config import settings


class InventoryClient(BaseClient):
    def __init__(self):
        super().__init__(
            base_url=settings.INVENTORY_SERVICE_URL,
            api_key=settings.INVENTORY_SERVICE_API_KEY,
            api_secret=settings.INVENTORY_SERVICE_API_SECRET,
            service_name="InventoryPortal",
        )

    async def get_products(self, limit: int = 50, offset: int = 0) -> dict:
        """Fetch paginated product list."""
        return await self.get(
            "/api/v1/products/",
            params={"limit": limit, "offset": offset},
        )

    async def get_product(self, product_id: str) -> dict:
        """Fetch a single product by ID."""
        return await self.get(f"/api/v1/products/{product_id}")

    async def get_stock(self, product_id: str, variant_id: Optional[str] = None) -> dict:
        """Check stock level for a product."""
        params = {}
        if variant_id:
            params["variant_id"] = variant_id
        return await self.get(
            f"/api/v1/inventory/{product_id}",
            params=params,
        )

    async def create_product(self, product_data: dict) -> dict:
        """Create a new product in the inventory microservice."""
        return await self.post("/api/v1/products/", json=product_data)

    async def update_product(self, product_id: str, product_data: dict) -> dict:
        """Update an existing product in the inventory microservice."""
        return await self.put(f"/api/v1/products/{product_id}", json=product_data)


inventory_client = InventoryClient()

