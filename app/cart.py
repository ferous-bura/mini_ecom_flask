from flask import Blueprint, jsonify, request

from app import db
from app.models import CartItem, Product, ProductImage
from util.helpers import token_required
from util.utils import BASE_URL

cart_routes = Blueprint('cart', __name__)


@cart_routes.route('/', methods=['POST'])
@token_required
def add_to_cart(current_user):
    data = request.get_json()
    print(f'data {data}')

    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    if not product_id:
        return jsonify({"error": "Product ID is required."}), 400

    # Check product exists
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found."}), 404

    # Check if item already in cart, if so update quantity explicitly
    existing_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if existing_item:
        existing_item.quantity += quantity
    else:
        # Explicitly create new item in cart
        new_cart_item = CartItem(
            user_id=current_user.id,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(new_cart_item)

    db.session.commit()

    return jsonify({"message": f"Added {quantity} of {product.name} to your cart."}), 200


@cart_routes.route('/', methods=['GET'])
@token_required
def get_cart_items(current_user):
    # user_id = session.get('user_id')
    print(f'current_user {current_user} getting cart items')
    if not current_user.id:
        print('no user id')
        return jsonify({"error": "Unauthorized access"}), 401

    # Retrieve cart items for authenticated user
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

    items_list = []
    for item in cart_items:
        product = Product.query.get(item.product_id)

        product_images = ProductImage.query.filter_by(product_id=product.id).order_by(ProductImage.order).all()
        image_urls = [
            (BASE_URL + image.image_url) if not image.image_url.startswith("http") else image.image_url
            for image in product_images
        ]

        items_list.append({
            # "image_url": product.image_url,
            "image_urls": image_urls if image_urls else [BASE_URL + "/uploads/default.jpg"],
            "product_id": product.id,
            "name": product.name,
            "quantity": item.quantity,
            "price": product.price,
            "total_price": product.price * item.quantity
        })
    print(f'items_list {items_list}')

    return jsonify(items_list), 200
