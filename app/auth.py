import uuid

from flask import request, jsonify, Blueprint

from app import db
from app.models import User
from util.helpers import copy_token_to_clipboard, generate_token, token_required

auth_routes = Blueprint('auth', __name__)


@auth_routes.route('/register', methods=['POST'])
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


@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    print(f'data {data}')

    if not data or not all(key in data for key in ('email', 'password')):
        return jsonify({"error": "Please provide email and password"}), 400

    user = User.query.filter_by(email=data['email']).first()

    if user and user.check_password(data['password']):
        user.token = generate_token(user)
        db.session.commit()
        copy_token_to_clipboard(user.token)  # dynamically copy token to clipboard explicitly
        print(f'is seller {user.is_seller}')
        return jsonify(
            {"message": "Login successful", 'userId': user.id, "token": user.token, "isSeller": user.is_seller}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401


@auth_routes.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not current_password or not new_password:
        return jsonify({"success": False, "message": "Missing current or new password."}), 400

    if not current_user.check_password(current_password):  # <-- Correct method usage
        return jsonify({"success": False, "message": "Current password is incorrect."}), 400

    current_user.set_password(new_password)  # Use set_password

    try:
        db.session.commit()
        token = generate_token(current_user)

        return jsonify({
            "success": True,
            "token": token,
            "message": "Password changed successfully and token refreshed."
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Failed to update password."}), 500
