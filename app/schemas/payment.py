"""
Request/response schemas for payment endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, Any


class CreatePaymentRequest(BaseModel):
    amount: int = Field(..., gt=0, description="Amount in paise")
    currency: str = "INR"
    plan_type: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
