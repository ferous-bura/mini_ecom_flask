from api import create_app, db
from api.models import User, Product, Category, ProductImage, ProductRating, DeliveryOption

app = create_app()
app.app_context().push()


def seed_categories():
    categories = [
        "Electronics", "Books", "Clothing", "Furniture", "Sports Equipment",
        "Home Appliances", "Toys & Games", "Beauty & Personal Care", "Jewelry", "Automotive"
    ]

    for name in categories:
        existing_category = Category.query.filter_by(name=name).first()
        if existing_category is None:
            category = Category(name=name)
            db.session.add(category)
            print(f'Category "{name}" added.')
        else:
            print(f'Category "{name}" already exists.')

    db.session.commit()
    print("Categories seeded successfully.\n")


def seed_users():
    users = [
        {"full_name": "John Doe", "email": "john.doe@example.com", "password": "password123", "confirmed": True},
        {"full_name": "Jane Smith", "email": "jane.smith@example.com", "password": "password123", "confirmed": True},
        {"full_name": "Alex Brown", "email": "alex.brown@example.com", "password": "password123", "confirmed": False},
        {"full_name": "Emily Davis", "email": "emily.davis@example.com", "password": "password123", "confirmed": True},
        {"full_name": "Michael Wilson", "email": "michael.wilson@example.com", "password": "password123",
         "confirmed": False},
        {"full_name": "Sarah Johnson", "email": "sarah.johnson@example.com", "password": "password123",
         "confirmed": True},
        {"full_name": "David Lee", "email": "david.lee@example.com", "password": "password123", "confirmed": True},
        {"full_name": "Laura Adams", "email": "laura.adams@example.com", "password": "password123", "confirmed": False},
        {"full_name": "Chris Evans", "email": "chris.evans@example.com", "password": "password123", "confirmed": True},
        {"full_name": "Biruh Alemayehu", "email": "b@b.b", "password": "b", "confirmed": True}
    ]

    for user_data in users:
        existing_user = User.query.filter_by(email=user_data["email"]).first()
        if existing_user is None:
            user = User(full_name=user_data["full_name"], email=user_data["email"], confirmed=user_data["confirmed"])
            user.set_password(user_data["password"])
            db.session.add(user)
            print(f'User "{user_data["full_name"]}" added.')
        else:
            print(f'User "{user_data["full_name"]}" already exists.')

    db.session.commit()
    print("Users seeded successfully.\n")


def seed_products():
    categories = {category.name: category.id for category in Category.query.all()}
    users = User.query.all()

    products = [
        {"name": "Smartphone", "description": "Latest model with 128GB storage and 5G support.", "price": 599.99,
         "previous_price": 699.99, "category": "Electronics", "stock_quantity": 50, "sku": "SM-001",
         "images": ["https://images.unsplash.com/photo-1511707171634-5f897ff02aa9",
                    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c"]},
        {"name": "Wireless Headphones",
         "description": "Noise-cancelling over-ear headphones with 20-hour battery life.", "price": 199.99,
         "previous_price": 249.99, "category": "Electronics", "stock_quantity": 100, "sku": "WH-001",
         "images": ["https://images.unsplash.com/photo-1613040809024-b4ef37405558"]},
        {"name": "Running Shoes", "description": "Lightweight running shoes with breathable mesh.", "price": 129.99,
         "previous_price": 149.99, "category": "Clothing", "stock_quantity": 75, "sku": "RS-001",
         "images": ["https://images.unsplash.com/photo-1600585154340-be6161a56a0c"]},
        {"name": "Mountain Bike", "description": "21-speed mountain bike with disc brakes.", "price": 999.99,
         "previous_price": 1199.99, "category": "Sports Equipment", "stock_quantity": 20, "sku": "MB-001",
         "images": ["https://images.unsplash.com/photo-1532298229144-0ec0c57515c7"]},
        {"name": "Science Fiction Novel", "description": "A gripping sci-fi thriller by a renowned author.",
         "price": 19.99, "previous_price": 24.99, "category": "Books", "stock_quantity": 200, "sku": "SFN-001",
         "images": ["https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c"]},
        {"name": "Gaming Laptop", "description": "High-performance laptop with RTX 3080 GPU.", "price": 1299.99,
         "previous_price": 1499.99, "category": "Electronics", "stock_quantity": 30, "sku": "GL-001",
         "images": ["https://images.unsplash.com/photo-1496181133206-80ce9b88a0a6"]},
        {"name": "Leather Jacket", "description": "Genuine leather jacket with a modern fit.", "price": 89.99,
         "previous_price": 109.99, "category": "Clothing", "stock_quantity": 60, "sku": "LJ-001",
         "images": ["https://images.unsplash.com/photo-1551488831-00ddcb6c0a3a"]},
        {"name": "Wooden Bookshelf", "description": "Sturdy wooden bookshelf with 5 shelves.", "price": 299.99,
         "previous_price": 349.99, "category": "Furniture", "stock_quantity": 15, "sku": "WB-001",
         "images": ["https://images.unsplash.com/photo-1600585154340-be6161a56a0c"]},
        {"name": "Air Fryer", "description": "5-quart air fryer with digital controls.", "price": 89.99,
         "previous_price": 99.99, "category": "Home Appliances", "stock_quantity": 40, "sku": "AF-001",
         "images": ["https://images.unsplash.com/photo-1600585154340-be6161a56a0c"]},
        {"name": "Board Game", "description": "Family-friendly strategy board game.", "price": 29.99,
         "previous_price": 34.99, "category": "Toys & Games", "stock_quantity": 150, "sku": "BG-001",
         "images": ["https://images.unsplash.com/photo-1600585154340-be6161a56a0c"]},
        {"name": "Perfume Set", "description": "Luxury perfume set with 3 scents.", "price": 49.99,
         "previous_price": 59.99, "category": "Beauty & Personal Care", "stock_quantity": 80, "sku": "PS-001",
         "images": ["https://images.unsplash.com/photo-1600585154340-be6161a56a0c"]},
        {"name": "Diamond Necklace", "description": "Elegant diamond necklace with 18k gold chain.", "price": 499.99,
         "previous_price": 599.99, "category": "Jewelry", "stock_quantity": 10, "sku": "DN-001",
         "images": ["https://images.unsplash.com/photo-1600585154340-be6161a56a0c"]},
        {"name": "Car Cleaning Kit", "description": "Complete car cleaning kit with wax and polish.", "price": 39.99,
         "previous_price": 49.99, "category": "Automotive", "stock_quantity": 90, "sku": "CCK-001",
         "images": ["https://images.unsplash.com/photo-1600585154340-be6161a56a0c"]}
    ]

    for item in products:
        existing_product = Product.query.filter_by(name=item["name"]).first()
        if existing_product is None:
            product = Product(
                name=item["name"],
                description=item["description"],
                price=item["price"],
                previous_price=item["previous_price"],
                stock_quantity=item["stock_quantity"],
                sku=item["sku"],
                category_id=categories[item["category"]]
            )
            db.session.add(product)
            db.session.flush()

            for image_url in item["images"]:
                product_image = ProductImage(product_id=product.id, image_url=image_url)
                db.session.add(product_image)

            # Add some ratings and comments
            for user in users[:3]:  # First 3 users rate each product
                rating = ProductRating(
                    product_id=product.id,
                    user_id=user.id,
                    rating=(hash(user.email + item["name"]) % 5) + 1,  # Random rating 1-5
                    comment=f"Great {item['name'].lower()}! Very satisfied with the quality."
                )
                db.session.add(rating)

            print(f'Product "{item["name"]}" added.')
        else:
            print(f'Product "{item["name"]}" already exists.')

    db.session.commit()
    print("Products seeded successfully.\n")


def seed_delivery_options():
    delivery_options = [
        {"name": "Standard Delivery", "base_fee": 5.0, "description": "3-5 business days"},
        {"name": "Express Delivery", "base_fee": 15.0, "description": "1-2 business days"},
    ]
    for option in delivery_options:
        existing_option = DeliveryOption.query.filter_by(name=option["name"]).first()
        if not existing_option:
            delivery_option = DeliveryOption(
                name=option["name"],
                base_fee=option["base_fee"],
                description=option["description"]
            )
            db.session.add(delivery_option)
    db.session.commit()
    print("Delivery options seeded successfully.\n")


def seed_all():
    print("⚙️ Seeding Categories...")
    seed_categories()

    print("⚙️ Seeding Users...")
    seed_users()

    print("⚙️ Seeding Products...")
    seed_products()

    print('seeding delivery options...')
    seed_delivery_options()


if __name__ == "__main__":
    seed_all()
