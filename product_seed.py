import colorsys
import os
import random

from PIL import Image, ImageDraw, ImageFont

from api import create_app, db
from api.models import User, Product, Category, ProductImage, DeliveryOption, Analytics

app = create_app()
app.app_context().push()

# Ensure upload folder exists
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Base categories to expand
BASE_CATEGORIES = [
    "Electronics", "Books", "Clothing", "Furniture", "Sports Equipment",
    "Home Appliances", "Toys & Games", "Beauty & Personal Care", "Jewelry", "Automotive"
]


# Shape functions
def draw_shape(draw, shape, x, y, size, color):
    if shape == "circle":
        draw.ellipse([x, y, x + size, y + size], fill=color)
    elif shape == "cube":
        draw.rectangle([x, y, x + size, y + size], fill=color)
    elif shape == "triangle":
        draw.polygon([(x, y), (x + size, y), (x + size // 2, y - size)], fill=color)


# Generate gradient image with product name and shape
def create_product_image(product_name, product_id):
    width, height = 600, 400
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    # Gradient background
    h = random.random()  # Random hue
    for y in range(height):
        s = 1.0  # Saturation
        v = y / height  # Value (lightness)
        r, g, b = [int(255 * x) for x in colorsys.hsv_to_rgb(h, s, v)]
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Product name (try to load a font, fallback to default)
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    text_bbox = draw.textbbox((0, 0), product_name, font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    draw.text(((width - text_width) // 2, (height - text_height) // 2), product_name, font=font, fill="white")

    # Random shape
    shapes = ["circle", "cube", "triangle"]
    shape = random.choice(shapes)
    draw_shape(draw, shape, random.randint(50, width - 150), random.randint(50, height - 150), 100, "white")

    # Save image
    filename = f"product_{product_id}_{shape}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    img.save(filepath, "JPEG")
    return f"/uploads/images/{filename}"


def seed_categories():
    categories = []
    for base in BASE_CATEGORIES:
        for i in range(1, 11):  # 10 variations per base category
            name = f"{base} {i}"
            if not Category.query.filter_by(name=name).first():
                categories.append(Category(name=name))
                print(f'Category "{name}" added.')
    db.session.bulk_save_objects(categories)
    db.session.commit()
    print(f"Seeded {len(categories)} categories.\n")


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


def seed_products():
    categories = {category.name: category.id for category in Category.query.all()}
    adjectives = ["Smart", "Luxury", "Classic", "Modern", "Eco", "Pro", "Ultra", "Vintage"]
    nouns = ["Phone", "Laptop", "Shirt", "Chair", "Bike", "Fridge", "Game", "Cream", "Ring", "Tire"]
    products = []

    for i in range(2000):  # Generate 2000 products
        category_name = random.choice(list(categories.keys()))
        adj = random.choice(adjectives)
        noun = random.choice(nouns)
        name = f"{adj} {noun} {i % 100}"
        price = round(random.uniform(10, 1500), 2)
        product = Product(
            name=name,
            description=f"A {adj.lower()} {noun.lower()} with great features.",
            price=price,
            previous_price=price * random.uniform(1.1, 1.5),
            stock_quantity=random.randint(10, 200),
            sku=f"{adj[:2]}{noun[:2]}-{i:04d}",
            category_id=categories[category_name]
        )
        products.append(product)

    db.session.bulk_save_objects(products)
    db.session.commit()

    # Add images after products are created
    for product in Product.query.all():
        image_url = create_product_image(product.name, product.id)
        product_image = ProductImage(product_id=product.id, image_url=image_url)
        db.session.add(product_image)
        print(f'Image for "{product.name}" created.')

    db.session.commit()
    print(f"Seeded {len(products)} products with images.\n")


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

    for _ in range(5000):  # 5000 dummy events
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


# Add to seed_all()
def seed_all():
    print("⚙️ Seeding Dummy Analytics...")
    seed_dummy_analytics()

    print("⚙️ Seeding Categories...")
    seed_categories()
    print("⚙️ Seeding Users...")
    seed_users()
    print("⚙️ Seeding Products...")
    seed_products()
    print("⚙️ Seeding Delivery Options...")
    seed_delivery_options()


if __name__ == "__main__":
    seed_all()
