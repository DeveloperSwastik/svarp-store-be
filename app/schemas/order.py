"""
Request/response schemas for order endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any


class OrderItemCreate(BaseModel):
    product_id: int
    variant_id: Optional[int] = None
    name: str
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)
    image: Optional[str] = None


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    shipping_address: Optional[dict] = None
    payment_id: Optional[str] = None
    payment_order_id: Optional[str] = None
    total_amount: float = Field(..., gt=0)
    currency: str = "INR"
    notes: Optional[str] = None
