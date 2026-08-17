# API Client modules for microservice communication
from app.clients.inventory_client import inventory_client
from app.clients.order_client import order_client
from app.clients.payment_client import payment_client
from app.clients.coupon_client import coupon_client
from app.clients.user_portal_client import user_portal_client

__all__ = [
    "inventory_client",
    "order_client",
    "payment_client",
    "coupon_client",
    "user_portal_client",
]
