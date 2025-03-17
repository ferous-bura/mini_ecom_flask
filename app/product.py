import os

from flask import url_for, request, jsonify, Blueprint

from util.utils import BASE_URL
from .models import Product, ProductImage

product_routes = Blueprint('buyer', __name__)


@product_routes.route('/', methods=['GET'])
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)  # Limit results (default to 5)

    products = Product.query.limit(per_page).offset((page - 1) * per_page).all()

    product_list = []
    for product in products:
        product_images = ProductImage.query.filter_by(product_id=product.id).order_by(ProductImage.order).all()
        image_urls = [
            (BASE_URL + image.image_url) if not image.image_url.startswith("http") else image.image_url
            for image in product_images
        ]

        product_list.append({
            "quantity": 1,
            "product_id": product.id,
            "name": product.name,
            "price": product.price,
            "previous_price": product.previous_price,
            "stock_quantity": product.stock_quantity,
            "sku": product.sku,
            "category": product.category.name if product.category else None,
            "image_urls": image_urls if image_urls else [BASE_URL + "/uploads/default.jpg"],
            "ratings": [{"rating": r.rating, "comment": r.comment} for r in product.ratings]
        })

    return jsonify(product_list)
