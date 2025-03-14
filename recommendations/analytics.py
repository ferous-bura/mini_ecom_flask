# analytics/analytics.py
from api.models import Product, User, OrderItem
from datetime import datetime

def track_product_view(user_id, product_id):
    """Tracks a product view event."""
    # Store in a separate analytics table (e.g., ProductView)
    # This is a simplified example; use a proper database table
    print(f"Product view tracked: User {user_id}, Product {product_id} at {datetime.now()}")

def track_purchase(user_id, product_id, quantity):
    """Tracks a purchase event."""
    # Store in a separate analytics table (e.g., Purchase)
    print(f"Purchase tracked: User {user_id}, Product {product_id}, Quantity {quantity} at {datetime.now()}")