import qrcode
import io
import base64
from flask import Blueprint, jsonify, request, url_for, send_file, render_template, current_app
import uuid

routes = Blueprint('routes', __name__)

# Function to generate QR Code
def generate_qr_code(url):
    qr = qrcode.make(url)
    img_io = io.BytesIO()
    qr.save(img_io, format='PNG')
    img_io.seek(0)
    return base64.b64encode(img_io.getvalue()).decode()

@routes.route('/', methods=['GET'])
def homepage():
    # Generate QR code for the homepage URL
    home_url = url_for('routes.homepage', _external=True)
    qr_code_data = generate_qr_code(home_url)

    # Get all registered routes from the app
    urls = [rule.rule for rule in current_app.url_map.iter_rules()]

    # Render the template
    return render_template('index.html', qr_code_data=qr_code_data, urls=urls)

@routes.route('/api/products', methods=['GET'])
def get_products():
    products = [
        {"id": 1, "name": "Item 1", "price": 10.0, "imageUrl": url_for('static', filename='images/item1.jpg', _external=True)},
        {"id": 2, "name": "Item 2", "price": 20.0, "imageUrl": url_for('static', filename='images/item2.jpg', _external=True)},
        {"id": 1, "name": "Item 1", "price": 10.0, "imageUrl": url_for('static', filename='images/item1.jpg', _external=True)},
        {"id": 2, "name": "Item 2", "price": 20.0, "imageUrl": url_for('static', filename='images/item2.jpg', _external=True)},
        {"id": 1, "name": "Item 1", "price": 10.0, "imageUrl": "https://placehold.co/600x400.png"},
        {"id": 2, "name": "Item 2", "price": 20.0, "imageUrl": "https://placehold.co/600x400.png"},
    ]
    return jsonify(products)

@routes.route('/api/cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    # For MVP, just log it or store in memory
    print(f"Added to cart: {data}")
    return jsonify({"message": "Added to cart"}), 200

@routes.route('/api/checkout', methods=['POST'])
def checkout():
    data = request.get_json()
    # Mock payment and save order
    print(f"Checkout: {data}")
    return jsonify({"message": "Order placed"}), 200


@routes.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    # Dummy validation
    if not data or not all(key in data for key in ('username', 'password')):
        return jsonify({"error": "Please provide both username and password"}), 400

    # Generate a random token
    token = str(uuid.uuid4())

    return jsonify({"message": "User registered successfully", "token": token}), 201


@routes.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()

    # Dummy validation
    if not data or not all(key in data for key in ('username', 'password')):
        return jsonify({"error": "Invalid username or password"}), 400

    # Generate a random token
    token = str(uuid.uuid4())

    return jsonify({"message": "Login successful", "token": token}), 200


