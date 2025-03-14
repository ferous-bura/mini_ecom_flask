import base64
import io
import uuid

import qrcode
from flask import jsonify, request, url_for, render_template, current_app, Blueprint

from . import db
from .helpers import token_required, copy_token_to_clipboard
from .models import User, Product, CartItem, OrderItem, Order

api_routes = Blueprint('routes', __name__)


def generate_qr_code(url):
    qr = qrcode.make(url)
    img_io = io.BytesIO()
    qr.save(img_io, format='PNG')
    img_io.seek(0)
    return base64.b64encode(img_io.getvalue()).decode()


@api_routes.route('/', methods=['GET'])
def homepage():
    # Generate QR code for the homepage URL
    home_url = url_for('routes.homepage', _external=True)
    qr_code_data = generate_qr_code(home_url)

    # Get all registered api_routes from the app
    urls = [rule.rule for rule in current_app.url_map.iter_rules()]
    # print(f' urls {urls}' )

    # Render the template
    return render_template('index.html', qr_code_data=qr_code_data, urls=urls)


@api_routes.route('/products', methods=['GET'])
def get_products():
    products = [
        {"quantity": 1, "product_id": 1, "name": "Item 1", "price": 100.0,
         "image_url": url_for('static', filename='images/item1.jpg', _external=True)},
        {"quantity": 1, "product_id": 2, "name": "Item 2", "price": 208.0,
         "image_url": url_for('static', filename='images/item2.jpg', _external=True)},
        {"quantity": 1, "product_id": 3, "name": "Item 3", "price": 6710.0,
         "image_url": url_for('static', filename='images/item1.jpg', _external=True)},
        {"quantity": 1, "product_id": 4, "name": "Item 4", "price": 230.0,
         "image_url": url_for('static', filename='images/item2.jpg', _external=True)},
        {"quantity": 1, "product_id": 5, "name": "Item 5", "price": 160.0,
         "image_url": "https://placehold.co/600x400.png"},
        {"quantity": 1, "product_id": 6, "name": "Item 6", "price": 520.0,
         "image_url": "https://placehold.co/600x400.png"},
    ]
    return jsonify(products)


@api_routes.route('/cart', methods=['POST'])
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


@api_routes.route('/checkout', methods=['POST'])
@token_required
def checkout(current_user):
    # Retrieve cart items for current_user explicitly
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

    if not cart_items:
        return jsonify({"message": "Your cart is empty, please add items before checkout."}), 400

    # Create new Order explicitly
    new_order = Order(user_id=current_user.id, approved=True)
    db.session.add(new_order)
    db.session.flush()  # ensure order id is generated before we proceed

    # Transfer cart items to order clearly and explicitly
    for item in cart_items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.session.add(order_item)
        db.session.delete(item)  # explicitly empty cart after transfer

    db.session.commit()

    return jsonify({
        "message": "Order successfully placed.",
        "order_id": new_order.id
    }), 200


@api_routes.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    print(f'data {data}')

    required_fields = ('full_name', 'email', 'password')
    if not data or not all(key in data for key in required_fields):
        return jsonify({"error": "Please provide full_name, email, and password"}), 400

    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"error": "A user with this email already exists."}), 409

    new_user = User(
        full_name=data['full_name'],
        email=data['email']
    )
    new_user.set_password(data['password'])
    new_user.token = str(uuid.uuid4())  # Simplified token generation

    db.session.add(new_user)
    db.session.commit()
    copy_token_to_clipboard(new_user.token)  # dynamically copy token to clipboard explicitly

    return jsonify({"message": "User registered successfully", "token": new_user.token}), 201


@api_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    print(f'data {data}')

    if not data or not all(key in data for key in ('email', 'password')):
        return jsonify({"error": "Please provide email and password"}), 400

    user = User.query.filter_by(email=data['email']).first()

    if user and user.check_password(data['password']):
        user.token = str(uuid.uuid4())  # Generate fresh login token each time user logs in
        db.session.commit()
        copy_token_to_clipboard(user.token)  # dynamically copy token to clipboard explicitly

        return jsonify({"message": "Login successful", "token": user.token}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401


@api_routes.route('/get-cart', methods=['GET'])
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
        items_list.append({
            "image_url": product.imageUrl,
            "product_id": product.id,
            "name": product.name,
            "quantity": item.quantity,
            "price": product.price,
            "total_price": product.price * item.quantity
        })
    print(f'items_list {items_list}')

    return jsonify(items_list), 200
