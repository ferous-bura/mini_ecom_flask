import os
import random
from io import BytesIO

import requests
from PIL import Image

from app import db, create_app
from app.models import Product, Category, User, ProductImage
from util.utils import UPLOAD_FOLDER

app = create_app()
app.app_context().push()

# Unsplash API key (replace with your valid key from https://unsplash.com/developers)
UNSPLASH_API_KEY = "nerkeFS_sh2vF1QfqKPgZZ3UBVi8qUuAfL9fhSLGvmQ"
IMAGE_WIDTH, IMAGE_HEIGHT = 600, 400

# Realistic categories
REALISTIC_CATEGORIES = [
    "Smartphones", "Laptops & Tablets", "Audio & Headphones", "Cameras & Photography", "Televisions",
    "Fiction Books", "Non-Fiction Books", "Children’s Books", "Textbooks", "Comics & Graphic Novels",
    "Men’s T-Shirts", "Women’s Dresses", "Footwear", "Jackets & Coats", "Accessories",
    "Sofas & Couches", "Dining Tables", "Beds & Mattresses", "Office Chairs", "Storage Solutions",
    "Fitness Gear", "Cycling Equipment", "Camping Gear", "Sports Apparel", "Yoga Mats",
    "Refrigerators", "Microwaves", "Washing Machines", "Air Conditioners", "Coffee Makers",
    "Board Games", "Action Figures", "Puzzles", "Video Games", "Educational Toys",
    "Skincare Products", "Haircare Products", "Makeup", "Fragrances", "Personal Grooming",
    "Rings", "Necklaces", "Watches", "Earrings", "Bracelets",
    "Car Tires", "Engine Oils", "Car Mats", "Dash Cams", "Car Cleaning Supplies"
]


def seed_categories():
    categories = []
    for name in REALISTIC_CATEGORIES:
        if not Category.query.filter_by(name=name).first():
            categories.append(Category(name=name))
            print(f'Category "{name}" added.')
    db.session.bulk_save_objects(categories)
    db.session.commit()
    print(f"Seeded {len(categories)} categories.\n")


def seed_products():
    categories = {category.name: category.id for category in Category.query.all()}
    if not categories:
        print("No categories found. Please seed categories first.")
        return

    seller = User.query.filter_by(email='s@s.s').first()
    if not seller:
        print("Seller 's@s.s' not found. Please create the seller first.")
        return

    products = []

    # Product generation with category-specific logic
    for i in range(200):  # Generate 200 products
        category_name = random.choice(list(categories.keys()))

        # Define realistic product details based on category
        if "Smartphones" in category_name:
            name = f"{random.choice(['iPhone', 'Galaxy', 'Pixel', 'OnePlus'])} {random.randint(10, 15)} Pro"
            price = round(random.uniform(300, 1200), 2)
            description = f"A high-performance smartphone with {random.choice(['5G', 'AMOLED display', '128GB storage'])}."
        elif "Laptops" in category_name:
            name = f"{random.choice(['Dell XPS', 'MacBook', 'Lenovo ThinkPad', 'HP Spectre'])} {random.randint(13, 17)}\""
            price = round(random.uniform(800, 2500), 2)
            description = f"A powerful laptop for {random.choice(['gaming', 'work', 'creativity'])} with {random.randint(8, 32)}GB RAM."
        elif "Men’s" in category_name or "Women’s" in category_name:
            name = f"{random.choice(['Casual', 'Formal', 'Athletic'])} {category_name.split()[0]} {random.choice(['2023', 'Slim Fit', 'Classic'])}"
            price = round(random.uniform(20, 150), 2)
            description = f"A stylish {category_name.split()[0].lower()} made from {random.choice(['cotton', 'polyester', 'wool'])}."
        elif "Furniture" in category_name.lower():
            name = f"{random.choice(['Modern', 'Rustic', 'Minimalist'])} {category_name.split()[0]}"
            price = round(random.uniform(100, 1000), 2)
            description = f"A durable {category_name.split()[0].lower()} crafted from {random.choice(['wood', 'metal', 'glass'])}."
        elif "Fitness" in category_name or "Cycling" in category_name:
            name = f"{random.choice(['Pro', 'Elite', 'Core'])} {category_name.split()[0]} {random.choice(['Set', 'Gear', 'Kit'])}"
            price = round(random.uniform(50, 300), 2)
            description = f"Top-quality {category_name.split()[0].lower()} for {random.choice(['beginners', 'pros', 'enthusiasts'])}."
        elif "Refrigerators" in category_name or "Appliances" in category_name:
            name = f"{random.choice(['Samsung', 'LG', 'Whirlpool'])} {category_name.split()[0]} {random.choice(['Smart', 'Compact'])}"
            price = round(random.uniform(200, 1500), 2)
            description = f"An energy-efficient {category_name.split()[0].lower()} with {random.choice(['frost-free', 'inverter tech', 'large capacity'])}."
        elif "Games" in category_name:
            name = f"{random.choice(['Monopoly', 'Cyberpunk', 'LEGO', 'Puzzle'])} {random.choice(['Deluxe', '2023', 'Family'])}"
            price = round(random.uniform(15, 80), 2)
            description = f"A fun {category_name.split()[0].lower()} for {random.choice(['kids', 'adults', 'families'])}."
        elif "Skincare" in category_name or "Makeup" in category_name:
            name = f"{random.choice(['Glow', 'Hydra', 'Pure'])} {category_name.split()[0]} {random.choice(['Cream', 'Serum', 'Palette'])}"
            price = round(random.uniform(10, 100), 2)
            description = f"A premium {category_name.split()[0].lower()} for {random.choice(['daily use', 'sensitive skin', 'long-lasting wear'])}."
        elif "Jewelry" in category_name.lower():
            name = f"{random.choice(['Sterling', 'Gold', 'Diamond'])} {category_name.split()[0]}"
            price = round(random.uniform(30, 500), 2)
            description = f"An elegant {category_name.split()[0].lower()} made with {random.choice(['silver', 'gold', 'gemstones'])}."
        elif "Car" in category_name or "Automotive" in category_name:
            name = f"{random.choice(['Michelin', 'Bosch', 'Generic'])} {category_name.split()[0]} {random.choice(['Premium', 'Heavy Duty'])}"
            price = round(random.uniform(20, 200), 2)
            description = f"A reliable {category_name.split()[0].lower()} for {random.choice(['all vehicles', 'trucks', 'sedans'])}."
        else:
            name = f"{random.choice(['Smart', 'Luxury'])} {category_name.split()[0]}"
            price = round(random.uniform(10, 500), 2)
            description = f"A versatile {category_name.split()[0].lower()} with great features."

        product = Product(
            name=name,
            description=description,
            price=price,
            previous_price=price * random.uniform(1.1, 1.5),
            stock_quantity=random.randint(5, 100),  # More realistic stock range
            sku=f"{name[:2].upper()}{random.randint(1000, 9999)}",  # Unique SKU
            category_id=categories[category_name],
            seller_id=seller.id
        )
        products.append(product)

    # Check for existing SKUs to avoid duplicates
    existing_skus = {p.sku for p in Product.query.all()}
    unique_products = [p for p in products if p.sku not in existing_skus]

    if not unique_products:
        print("No new unique products to seed.")
        return

    db.session.bulk_save_objects(unique_products)
    db.session.commit()

    # Add images after products are created
    for product in Product.query.filter(
            Product.id.notin_([p.id for p in Product.query.filter(Product.images.any()).all()])).all():
        image_url = download_realistic_product_image(product.name, product.id)
        product_image = ProductImage(product_id=product.id, image_url=image_url)
        db.session.add(product_image)
        print(f'Image for "{product.name}" downloaded and linked.')

    db.session.commit()
    print(f"Seeded {len(unique_products)} products with realistic images.\n")


def download_realistic_product_image(product_name, product_id):
    query = product_name.replace(" ", "+")
    url = f"https://api.unsplash.com/search/photos?query={query}&per_page=1&orientation=landscape&client_id={UNSPLASH_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["results"]:
            image_url = data["results"][0]["urls"]["regular"]
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            img = Image.open(BytesIO(image_response.content))
            img = img.resize((IMAGE_WIDTH, IMAGE_HEIGHT), Image.Resampling.LANCZOS)
            filename = f"product_{product_id}_{random.randint(1000, 9999)}.jpg"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            img.save(filepath, "JPEG")
            return f"/uploads/images/{filename}"
        else:
            print(f"No image found for {product_name}, using default.")
            return fallback_image(product_name, product_id)
    except Exception as e:
        print(f"Error fetching image for {product_name}: {e}")
        return fallback_image(product_name, product_id)


def fallback_image(product_name, product_id):
    img = Image.new('RGB', (IMAGE_WIDTH, IMAGE_HEIGHT), color="gray")
    filename = f"product_{product_id}_fallback.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    img.save(filepath, "JPEG")
    return f"/uploads/images/{filename}"
