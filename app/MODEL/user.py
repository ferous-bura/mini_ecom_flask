import json
import os
from datetime import datetime, timedelta, UTC

import qrcode
import requests
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, create_app
from util.enums import *

app = create_app()


# User Model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    confirmed = db.Column(db.Boolean, default=False)
    token = db.Column(db.String(256), unique=True, index=True)
    addresses = db.relationship('Address', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)
    is_seller = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), default="customer")  # customer, seller, delivery, staff
    permissions = db.Column(db.JSON, default=lambda: {})
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    products = db.relationship('Product', backref='seller', lazy=True)  # For sellers
    sales_as_buyer = db.relationship('Sale', foreign_keys='Sale.buyer_id', backref='buyer', lazy=True)
    sales_as_seller = db.relationship('Sale', foreign_keys='Sale.seller_id', backref='seller', lazy=True)
    ratings = db.relationship('ProductRating', backref='user', lazy=True)
    cart_items = db.relationship('CartItem', backref='user', lazy='dynamic')
    orders = db.relationship('Order', foreign_keys='Order.user_id', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Category Model
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)


# Product Model (Replaces Item)
class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    previous_price = db.Column(db.Float, nullable=True)
    stock_quantity = db.Column(db.Integer, default=0)
    sku = db.Column(db.String(50), unique=True, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('products', lazy=True))
    images = db.relationship('ProductImage', backref='product', lazy=True)
    ratings = db.relationship('ProductRating', backref='product', lazy=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sales = db.relationship('Sale', backref='product', lazy=True)
    inventory = db.relationship('StoreInventory', backref='product', lazy=True)
    cart_items = db.relationship('CartItem', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)


# ProductImage Model
class ProductImage(db.Model):
    __tablename__ = 'product_images'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    edited = db.Column(db.Boolean, default=False)
    text_overlay = db.Column(db.String(255), nullable=True)
    order = db.Column(db.Integer, default=0)


# ProductRating Model
class ProductRating(db.Model):
    __tablename__ = 'product_ratings'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    parent_id = db.Column(db.Integer, db.ForeignKey('product_ratings.id'), nullable=True)
    replies = db.relationship('ProductRating', backref=db.backref('parent', remote_side=[id]), lazy=True)


# CartItem Model
class CartItem(db.Model):
    __tablename__ = 'cart_items'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)


# Order Model
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    approved = db.Column(db.Boolean, default=False)
    total_amount = db.Column(db.Float, nullable=False)
    order_items = db.relationship('OrderItem', backref='order', lazy=True)
    delivery_option_id = db.Column(db.Integer, db.ForeignKey('delivery_options.id'), nullable=True)
    delivery_option = db.relationship('DeliveryOption', backref=db.backref('orders', lazy=True))
    delivery_fee = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING)
    delivery_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    delivery_user = db.relationship('User', foreign_keys=[delivery_user_id], backref='delivery_orders')
    tracking_code = db.Column(db.String(50), nullable=True)

    def rollback(self):
        """Rollback the order and restore stock."""
        for item in self.order_items:
            item.product.stock_quantity += item.quantity
        db.session.delete(self.delivery_option)
        db.session.delete(self.payment)
        db.session.delete(self)
        db.session.commit()


# DeliveryOption Model (Modified from your version)
class DeliveryOption(db.Model):
    __tablename__ = 'delivery_options'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g., "Standard", "Express"
    base_fee = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    delivery_type = db.Column(db.Enum(DeliveryType), nullable=False)
    delivery_status = db.Column(db.Enum(DeliveryStatus), default=DeliveryStatus.PENDING)
    estimated_delivery_date = db.Column(db.Date)

    def set_delivery(self, delivery_type, cost=0.0, estimated_days=3):
        self.delivery_type = delivery_type
        self.base_fee = cost if delivery_type != DeliveryType.FREE else 0.0
        self.estimated_delivery_date = datetime.utcnow().date() + timedelta(days=estimated_days)
        db.session.commit()
        return self


# OrderItem Model
class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)


# Store Model
class Store(db.Model):
    __tablename__ = 'stores'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.Text)
    contact_info = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    inventory = db.relationship('StoreInventory', backref='store', lazy=True)


# Sale Model
class Sale(db.Model):
    __tablename__ = 'sales'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=True)
    sale_type = db.Column(db.Enum(SaleType), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)

    def create_sale(self, product_id, buyer_id, quantity, sale_type, store_id=None):
        product = Product.query.get(product_id)
        if not product or product.stock_quantity < quantity:
            raise ValueError("Product not available or insufficient stock")

        total_amount = product.price * quantity
        self.product_id = product_id
        self.buyer_id = buyer_id
        self.seller_id = product.seller_id
        self.store_id = store_id
        self.sale_type = sale_type
        self.quantity = quantity
        self.total_amount = total_amount
        product.stock_quantity -= quantity
        db.session.add(self)
        db.session.commit()
        return self


# StoreInventory Model
class StoreInventory(db.Model):
    __tablename__ = 'store_inventory'
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    storage_start_date = db.Column(db.Date, nullable=False)
    storage_end_date = db.Column(db.Date, nullable=True)
    charge_type = db.Column(db.Enum(ChargeType), nullable=False)
    charge_rate = db.Column(db.Float, nullable=False)
    total_charge = db.Column(db.Float, default=0.0)

    def calculate_charge(self):
        if self.charge_type == ChargeType.PER_ITEM_SOLD:
            sales = Sale.query.filter_by(store_id=self.store_id, product_id=self.product_id).all()
            self.total_charge = sum(sale.quantity for sale in sales) * self.charge_rate
        elif self.charge_type == ChargeType.PER_ITEM_PER_TIME:
            end_date = self.storage_end_date or datetime.utcnow().date()
            days = (end_date - self.storage_start_date).days
            self.total_charge = self.quantity * self.charge_rate * days
        db.session.commit()
        return self.total_charge


# Payment Model
class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('store_inventory.id'), nullable=True)
    payer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    payer = db.relationship('User', backref='payments')
    payment_method = db.Column(db.Enum(PaymentMethod), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING)
    qr_code_url = db.Column(db.String(256))
    invoice_url = db.Column(db.String(256))

    def generate_qr_code(self):
        payment_data = {
            'payment_id': self.id,
            'amount': self.amount,
            'method': self.payment_method.value,
            'payer_id': self.payer_id
        }
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(json.dumps(payment_data))
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        qr_path = f'static/qr_codes/payment_{self.id}.png'
        img.save(qr_path)
        self.qr_code_url = f"{app.config['BASE_URL']}/{qr_path}"
        db.session.commit()
        return self.qr_code_url

    def confirm_payment(self, api_key, api_endpoint):
        payload = {
            'payment_id': self.id,
            'amount': self.amount,
            'method': self.payment_method.value
        }
        headers = {'Authorization': f'Bearer {api_key}'}
        response = requests.post(api_endpoint, json=payload, headers=headers)

        if response.status_code == 200 and response.json().get('status') == 'success':
            self.payment_status = PaymentStatus.COMPLETED
            self.generate_invoice()
            db.session.commit()
            return True
        else:
            self.payment_status = PaymentStatus.FAILED
            db.session.commit()
            if self.order_id:
                Order.query.get(self.order_id).rollback()
            return False

    def generate_invoice(self):
        invoice_data = {
            'payment_id': self.id,
            'payer_id': self.payer_id,
            'amount': self.amount,
            'method': self.payment_method.value,
            'date': self.payment_date.isoformat()
        }
        invoice_path = f'static/invoices/invoice_{self.id}.json'
        with open(invoice_path, 'w') as f:
            json.dump(invoice_data, f)
        self.invoice_url = f"{app.config['BASE_URL']}/{invoice_path}"
        db.session.commit()
        return self.invoice_url


# Settings Model
class Settings(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(100), nullable=False, default="My Ecommerce Site")
    contact_email = db.Column(db.String(120), nullable=False, default="contact@example.com")


# Address Model
class Address(db.Model):
    __tablename__ = 'addresses'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


# Analytics Model
class Analytics(db.Model):
    __tablename__ = 'analytics'
    id = db.Column(db.Integer, primary_key=True)
    event = db.Column(db.String(50), nullable=False)
    data = db.Column(db.JSON, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# Notification Model
class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False, default="ecommerce show bot_api")
    type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    data = db.Column(db.JSON, nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    is_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))


# Create tables
# with app.app_context():
#     db.create_all()
#

# Example Route for Creating an Order with Payment
@app.route('/create_order', methods=['POST'])
def create_order():
    data = request.get_json()
    user_id = data['user_id']
    product_ids = data['product_ids']  # List of product IDs
    quantities = data['quantities']  # Corresponding quantities
    delivery_type = DeliveryType(data['delivery_type'])
    delivery_cost = data.get('delivery_cost', 0.0)
    payment_method = PaymentMethod(data['payment_method'])

    try:
        order = Order(user_id=user_id, total_amount=0.0)
        total_amount = 0.0
        for pid, qty in zip(product_ids, quantities):
            product = Product.query.get(pid)
            if not product or product.stock_quantity < qty:
                raise ValueError(f"Product {pid} not available or insufficient stock")
            order_item = OrderItem(order=order, product_id=pid, quantity=qty)
            total_amount += product.price * qty
            product.stock_quantity -= qty
            db.session.add(order_item)

        order.total_amount = total_amount + delivery_cost
        delivery = DeliveryOption(name=delivery_type.value, base_fee=delivery_cost,
                                  description=f"{delivery_type.value} delivery")
        delivery.set_delivery(delivery_type, delivery_cost)
        order.delivery_option = delivery

        payment = Payment(
            order_id=order.id,
            payer_id=user_id,
            payment_method=payment_method,
            amount=order.total_amount
        )
        db.session.add_all([order, payment])
        db.session.commit()

        qr_url = payment.generate_qr_code()
        api_key = os.getenv('PAYMENT_API_KEY')
        api_endpoint = {
            PaymentMethod.TELEBIRR: 'https://api.telebirr.com/confirm',
            PaymentMethod.MPESA: 'https://api.mpesa.com/confirm',
            PaymentMethod.BANK_TRANSFER: 'https://api.bank.com/confirm'
        }[payment_method]

        if payment.confirm_payment(api_key, api_endpoint):
            return jsonify({
                'message': 'Order created and payment confirmed',
                'order_id': order.id,
                'qr_code_url': qr_url,
                'invoice_url': payment.invoice_url
            }), 201
        else:
            return jsonify({'error': 'Payment failed, order rolled back'}), 400
    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# Route to Calculate Store Charge
@app.route('/calculate_store_charge/<int:inventory_id>', methods=['GET'])
def calculate_store_charge(inventory_id):
    inventory = StoreInventory.query.get_or_404(inventory_id)
    charge = inventory.calculate_charge()
    payment = Payment(
        inventory_id=inventory_id,
        payer_id=inventory.seller_id,
        payment_method=PaymentMethod.BANK_TRANSFER,
        amount=charge
    )
    db.session.add(payment)
    db.session.commit()
    qr_url = payment.generate_qr_code()
    return jsonify({'total_charge': charge, 'qr_code_url': qr_url, 'payment_id': payment.id})


"""
curl -X POST http://localhost:5000/create_order \
-H "Content-Type: application/json" \
-d '{
    "user_id": 1,
    "product_ids": [1, 2],
    "quantities": [2, 1],
    "delivery_type": "express",
    "delivery_cost": 5.0,
    "payment_method": "telebirr"
}'


{
    "message": "Order created and payment confirmed",
    "order_id": 1,
    "qr_code_url": "http://localhost:5000/static/qr_codes/payment_1.png",
    "invoice_url": "http://localhost:5000/static/invoices/invoice_1.json"
}

curl http://localhost:5000/calculate_store_charge/1

{
    "total_charge": 50.0,
    "qr_code_url": "http://localhost:5000/static/qr_codes/payment_2.png",
    "payment_id": 2
}
"""