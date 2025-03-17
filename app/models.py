from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from . import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    token = db.Column(db.String(256), unique=True, index=True)
    addresses = db.relationship('Address', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    is_seller = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), default="customer")  # Add role: customer, seller, delivery, staff
    permissions = db.Column(db.JSON,
                            default=lambda: {})  # e.g., {"can_manage_users": true, "can_manage_products": true}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)  # Added for detailed description
    price = db.Column(db.Float, nullable=False)
    previous_price = db.Column(db.Float, nullable=True)
    stock_quantity = db.Column(db.Integer, default=0)  # Added for stock
    sku = db.Column(db.String(50), unique=True, nullable=True)  # Added for SKU
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('products', lazy=True))
    images = db.relationship('ProductImage', backref='product', lazy=True)  # Multiple images
    ratings = db.relationship('ProductRating', backref='product', lazy=True)  # Ratings and comments
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Link to seller
    seller = db.relationship('User', backref=db.backref('products', lazy=True))


class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    edited = db.Column(db.Boolean, default=False)
    text_overlay = db.Column(db.String(255), nullable=True)
    order = db.Column(db.Integer, default=0)  # Add order column


class ProductRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('ratings', lazy=True))
    parent_id = db.Column(db.Integer, db.ForeignKey('product_rating.id'), nullable=True)
    replies = db.relationship('ProductRating', backref=db.backref('parent', remote_side=[id]), lazy=True)


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    user = db.relationship('User', backref=db.backref('cart_items', lazy='dynamic'))
    product = db.relationship('Product')


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved = db.Column(db.Boolean, default=False)
    total_amount = db.Column(db.Float, nullable=False)  # Total including delivery fee
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    order_items = db.relationship('OrderItem', backref='order', lazy=True)
    delivery_option_id = db.Column(db.Integer, db.ForeignKey('delivery_option.id'), nullable=True)
    delivery_option = db.relationship('DeliveryOption', backref=db.backref('orders', lazy=True))
    delivery_fee = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.String(20), default='Pending')  # e.g., "Pending", "Paid", "Failed"
    delivery_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Link to delivery user
    tracking_code = db.Column(db.String(50), nullable=True)  # Tracking code

class DeliveryOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "Standard", "Express"
    base_fee = db.Column(db.Float, nullable=False)  # Base fee for the delivery option
    description = db.Column(db.Text, nullable=True)  # e.g., "3-5 business days"


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    product = db.relationship('Product')


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(100), nullable=False, default="My Ecommerce Site")
    contact_email = db.Column(db.String(120), nullable=False, default="contact@example.com")


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class Analytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(50), nullable=False)
    data = db.Column(db.JSON, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False, default="ecommerce show bot_api")
    type = db.Column(db.String(50), nullable=False)  # e.g., "order_placed", "payment_success", "delivery_update"
    message = db.Column(db.Text, nullable=False)  # Short summary of the notification
    data = db.Column(db.JSON, nullable=True)  # Detailed data (e.g., order details, product list)
    is_read = db.Column(db.Boolean, default=False)  # Whether the user has read it
    is_sent = db.Column(db.Boolean, default=False)  # Whether it has been sent to the frontend
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp of creation

# flask db init
# flask db migrate -m "Add order column to ProductImage"
# flask db upgrade
# python seed.py
#
# flask db init
# flask db migrate -m "add all"
# python seed.py
# flask db upgrade

"""

[Start]
   |
   v
[Seller Lists Item]
   |----------------------------|
   |                            |
   v                            v
[Direct Sale]             [Indirect Sale]
   |                            |
   v                            v
[Buyer Orders]          [Store Inventory]
   |                            |
   v                            v
[Choose Delivery]       [Store Charges Seller]
   |                            |
   |----------------------------|
   v
[Payment]
   |-----------------|
   |                 |
   v                 v
[Buyer Pays]    [Seller Pays Store]
   |                 |
   v                 v
[Delivery]       [Update Inventory]
   |
   v
[End]
"""