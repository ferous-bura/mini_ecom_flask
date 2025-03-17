#chatgpt

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_seller = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), default="customer")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    storage_fee_per_item = db.Column(db.Float, default=0.0)
    storage_fee_per_day = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    owner = db.relationship('User', backref=db.backref('stores', lazy=True))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=True)  # Link to store for indirect sales
    seller = db.relationship('User', backref=db.backref('products', lazy=True))
    store = db.relationship('Store', backref=db.backref('products', lazy=True))

class DeliveryOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    base_fee = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # e.g., Telebirr, M-Pesa, Bank Transfer
    status = db.Column(db.String(20), default='Pending')  # e.g., Pending, Completed, Failed
    transaction_id = db.Column(db.String(100), unique=True, nullable=True)
    qr_code_url = db.Column(db.String(255), nullable=True)
    confirmation_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    order = db.relationship('Order', backref=db.backref('payments', lazy=True))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    delivery_option_id = db.Column(db.Integer, db.ForeignKey('delivery_option.id'), nullable=True)
    delivery_fee = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    delivery_option = db.relationship('DeliveryOption', backref=db.backref('orders', lazy=True))

    def calculate_delivery_fee(self, delivery_type):
        if delivery_type == "Free":
            self.delivery_fee = 0.0
        elif delivery_type == "Paid":
            self.delivery_fee = self.delivery_option.base_fee
        elif delivery_type == "Express":
            self.delivery_fee = self.delivery_option.base_fee * 1.5

    def process_order(self):
        for item in self.order_items:
            if item.product.store:
                item.product.store.owner.storage_fee_per_item += item.quantity * item.product.store.storage_fee_per_item
            item.product.stock_quantity -= item.quantity

    def rollback_order(self):
        for item in self.order_items:
            item.product.stock_quantity += item.quantity

    def generate_invoice_link(self, base_url):
        return f"{base_url}/invoice/{self.id}"

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    product = db.relationship('Product')
