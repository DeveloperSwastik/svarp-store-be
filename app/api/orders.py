"""
Order API routes — creates orders and fetches order history through the OMS portal.
All order routes require authentication.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.order import OrderCreate
from app.services.order_service import order_service
from app.middleware.auth import get_current_user
from app.clients.base import ServiceError

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/")
async def create_order(
    request: OrderCreate,
    user: dict = Depends(get_current_user),
):
    """Create a new order via the OMS portal."""
    try:
        customer_name = user.get("full_name") or user.get("email") or "Customer"
        first_product_name = request.items[0].name if request.items else "Unknown Product"
        total_quantity = sum(item.quantity for item in request.items)
        
        formatted_items = []
        for item in request.items:
            formatted_items.append({
                "product_id": str(item.product_id),
                "variant_id": str(item.variant_id) if item.variant_id is not None else None,
                "variant_name": None,
                "product_name": item.name,
                "quantity": item.quantity,
                "unit_price": float(item.price),
                "image": item.image
            })
            
        order_data = {
            "user_id": user.get("sub"),
            "customer_name": customer_name,
            "product_name": first_product_name,
            "quantity": total_quantity,
            "total_amount": float(request.total_amount),
            "currency": request.currency,
            "items": formatted_items,
        }
        return await order_service.create_order(user.get("sub"), order_data)
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/")
async def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, gt=0, le=100),
    user: dict = Depends(get_current_user),
):
    """Fetch user's order history from OMS portal."""
    try:
        return await order_service.get_orders(user.get("sub"), skip=skip, limit=limit)
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get("/{order_id}")
async def get_order(
    order_id: str,
    user: dict = Depends(get_current_user),
):
    """Fetch single order detail."""
    try:
        return await order_service.get_order(order_id)
    except ServiceError as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
