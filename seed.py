import os
import random
import uuid
from datetime import datetime, timedelta

from app import create_app, db
from app.models import User, Product, DeliveryOption, Analytics, CartItem, Order, OrderItem, \
    Notification
from util.download import seed_categories, seed_products
from util.utils import UPLOAD_FOLDER

app = create_app()
app.app_context().push()


def seed_users():
    users = [
        {"full_name": "John Doe", "email": "john.doe@example.com", "password": "password123", "confirmed": True},
        {"full_name": "Jane Smith", "email": "jane.smith@example.com", "password": "password123", "confirmed": True},
        {"full_name": "Biruh Alemayehu", "email": "b@b.b", "password": "b", "confirmed": True}
    ]
    for user_data in users:
        if not User.query.filter_by(email=user_data["email"]).first():
            user = User(full_name=user_data["full_name"], email=user_data["email"], confirmed=user_data["confirmed"])
            user.set_password(user_data["password"])
            db.session.add(user)
            print(f'User "{user_data["full_name"]}" added.')
    db.session.commit()
    print("Users seeded successfully.\n")


def seed_seller():
    seller_user = User(full_name='Alice Seller', email='s@s.s', is_seller=True)
    seller_user.set_password('s')

    db.session.add(seller_user)
    db.session.commit()
    print('Seeded seller users successfully.')


def seed_delivery_options():
    delivery_options = [
        {"name": "Standard Delivery", "base_fee": 5.0, "description": "3-5 business days"},
        {"name": "Express Delivery", "base_fee": 15.0, "description": "1-2 business days"},
    ]
    for option in delivery_options:
        if not DeliveryOption.query.filter_by(name=option["name"]).first():
            db.session.add(DeliveryOption(**option))
    db.session.commit()
    print("Delivery options seeded successfully.\n")


def seed_dummy_analytics():
    users = User.query.all()
    products = Product.query.all()
    events = ["view", "add_to_cart", "purchase"]
    analytics = []

    for _ in range(500):  # 5000 dummy events
        user = random.choice(users)
        product = random.choice(products)
        event = random.choice(events)
        analytics.append(Analytics(
            event=event,
            data={"product_id": product.id},
            user_id=user.id
        ))
    db.session.bulk_save_objects(analytics)
    db.session.commit()
    print("Dummy analytics seeded successfully.\n")


def seed_cart_items():
    users = User.query.all()
    products = Product.query.all()
    cart_items = []

    for user in users:
        # Each user gets 1-5 random items in their cart
        num_items = random.randint(1, 5)
        selected_products = random.sample(products, num_items)

        for product in selected_products:
            quantity = random.randint(1, min(5, product.stock_quantity))  # Limit to available stock
            cart_item = CartItem(
                user_id=user.id,
                product_id=product.id,
                quantity=quantity
            )
            cart_items.append(cart_item)

            # Create a notification for adding to cart
            notification = Notification(
                user_id=user.id,
                type="cart_updated",
                title="order_placed",
                message=f"Added {quantity} of {product.name} to your cart!",
                data={
                    "product_id": product.id,
                    "name": product.name,
                    "quantity": quantity,
                    "price": product.price,
                    "total": product.price * quantity,
                    "timestamp": datetime.utcnow().isoformat()
                },
                is_read=False,
                is_sent=False
            )
            db.session.add(notification)
            print(f'Cart item "{product.name}" added for user "{user.full_name}" with notification.')

    db.session.bulk_save_objects(cart_items)
    db.session.commit()
    print(f"Seeded {len(cart_items)} cart items with notifications.\n")


def seed_orders():
    users = User.query.all()
    products = Product.query.all()
    delivery_options = DeliveryOption.query.all()
    orders = []
    order_items = []
    notifications = []

    for user in users:
        # Each user gets 1-3 orders
        num_orders = random.randint(1, 3)
        for _ in range(num_orders):
            # Randomly select 1-4 products for the order
            num_products = random.randint(1, 4)
            selected_products = random.sample(products, num_products)
            total_amount = 0
            order_items_data = []

            # Create order
            delivery_option = random.choice(delivery_options)
            order = Order(
                user_id=user.id,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),  # Orders from past 30 days
                approved=random.choice([True, False]),
                total_amount=0,  # Will update after items are added
                delivery_option_id=delivery_option.id,
                delivery_fee=delivery_option.base_fee,
                payment_status=random.choice(["Pending", "Paid", "Failed"])
            )
            orders.append(order)
            db.session.add(order)
            db.session.flush()  # Get order ID

            # Add order items
            for product in selected_products:
                quantity = random.randint(1, min(3, product.stock_quantity))
                total_amount += quantity * product.price
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity
                )
                order_items.append(order_item)
                order_items_data.append({
                    "product_id": product.id,
                    "name": product.name,
                    "quantity": quantity,
                    "price": product.price,
                    "total": quantity * product.price
                })

            # Update total amount with delivery fee
            order.total_amount = total_amount + order.delivery_fee

            # Create notification for order placement
            notification = Notification(
                user_id=user.id,
                type="order_placed",
                title="order_placed",
                message=f"Order #{order.id} placed successfully!",
                data={
                    "order_id": order.id,
                    "products": order_items_data,
                    "address": f"Sample Address for {user.full_name}",  # Placeholder address
                    "delivery_option": delivery_option.name,
                    "delivery_fee": delivery_option.base_fee,
                    "payment_status": order.payment_status,
                    "total_amount": order.total_amount,
                    "created_at": order.created_at.isoformat()
                },
                is_read=False,
                is_sent=False
            )
            notifications.append(notification)
            print(f'Order #{order.id} created for user "{user.full_name}" with notification.')

    db.session.bulk_save_objects(order_items)
    db.session.bulk_save_objects(notifications)
    db.session.commit()
    print(f"Seeded {len(orders)} orders with {len(order_items)} items and {len(notifications)} notifications.\n")


def seed_admin():
    # Check if an admin already exists
    if not User.query.filter_by(role="admin").first():
        admin = User(
            full_name="Admin User",
            email="a@a.a",
            role="admin",
            is_seller=False
        )
        admin.set_password("a")
        admin.token = str(uuid.uuid4())
        db.session.add(admin)
        db.session.commit()
        print("Admin user created with email: admin@example.com and password: admin123")
    else:
        print("Admin user already exists.")


def seed_all():
    print("⚙️ Seeding Users...")
    seed_users()
    print("⚙️ Seeding Seller...")
    seed_seller()
    print("⚙️ Seeding Categories...")
    seed_categories()
    print("⚙️ Seeding Products...")
    seed_products()
    print("⚙️ Seeding Delivery Options...")
    seed_delivery_options()
    print("⚙️ Seeding Cart Items...")
    seed_cart_items()
    print("⚙️ Seeding Orders...")
    seed_orders()
    print("⚙️ Seeding Dummy Analytics...")
    seed_dummy_analytics()
    print('seeding admin user')
    seed_admin()
    print(' seed_all() completed.')


# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if __name__ == "__main__":
    seed_all()
    print("UPLOAD_FOLDER path:", UPLOAD_FOLDER)
