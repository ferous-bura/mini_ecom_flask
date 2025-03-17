import uuid
from flask import request, jsonify, Blueprint
from app import db
from app.forms import RegisterSchema
from app.models import User
from util.helpers import copy_token_to_clipboard, generate_token, token_required

auth_routes = Blueprint('auth', __name__)

"""
{
    "full_name": "John Doe",
    "email": "john@example.com",
    "password": "password123",
    "role": "seller"
}

curl -X POST http://localhost:5000/auth/register \
-H "Content-Type: application/json" \
-d '{"full_name": "Jane Seller", \
"email": "jane@example.com", "password": "pass123", "role": "seller"}'

{
    "message": "Seller registered successfully",
    "token": "uuid-string-here",
    "userId": 1,
    "role": "seller"
}

curl -X POST http://localhost:5000/auth/register \
-H "Content-Type: application/json" \
-d '{"full_name": "Bob", "email": "bob@example.com", "password": "pass123"}'

{
    "message": "Staff login successful",
    "userId": 3,
    "token": "uuid-string-here",
    "role": "staff"
}


{
    "error": "Please provide full_name, email, and password"
}

"""

# Reusable registration logic
def register_user(data, default_role="customer"):
    required_fields = ('full_name', 'email', 'password')
    if not data or not all(key in data for key in required_fields):
        return {"error": "Please provide full_name, email, and password"}, 400

    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return {"error": "A user with this email already exists."}, 409

    # Determine role (default to customer if not provided or invalid)
    role = data.get('role', default_role).lower()
    valid_roles = {"customer", "seller", "delivery"}
    if role not in valid_roles:
        role = "customer"  # Fallback to default if invalid role provided

    new_user = User(
        full_name=data['full_name'],
        email=data['email'],
        role=role,  # Assign the role
        is_seller=(role == "seller")  # Set is_seller based on role
    )
    new_user.set_password(data['password'])
    new_user.token = str(uuid.uuid4())  # Simplified token generation

    db.session.add(new_user)
    db.session.commit()
    copy_token_to_clipboard(new_user.token)  # Copy token to clipboard

    return {
        "message": f"{role.capitalize()} registered successfully",
        "token": new_user.token,
        "userId": new_user.id,
        "role": new_user.role
    }, 201


# @auth_routes.route('/register', methods=['POST'])
# def register():
#     data = request.get_json()
#     print(f'data {data}')
#
#     result, status = register_user(data)  # Reuse registration logic
#     return jsonify(result), status


@auth_routes.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    schema = RegisterSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({"error": errors}), 400
    result, status = register_user(data)
    return jsonify(result), status

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
        copy_token_to_clipboard(user.token)  # Copy token to clipboard
        print(f'role {user.role}, is_seller {user.is_seller}')
        return jsonify({
            "message": "Login successful",
            "userId": user.id,
            "token": user.token,
            "role": user.role,
            "isSeller": user.is_seller
        }), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401


@auth_routes.route('/staff/login', methods=['POST'])
def staff_login():
    data = request.get_json()
    print(f'data {data}')

    if not data or not all(key in data for key in ('email', 'password')):
        return jsonify({"error": "Please provide email and password"}), 400

    user = User.query.filter_by(email=data['email'], role="staff").first()

    if user and user.check_password(data['password']):
        user.token = generate_token(user)
        db.session.commit()
        copy_token_to_clipboard(user.token)  # Copy token to clipboard
        print(f'staff login successful for {user.email}')
        return jsonify({
            "message": "Staff login successful",
            "userId": user.id,
            "token": user.token,
            "role": user.role
        }), 200
    else:
        return jsonify({"error": "Invalid staff email or password"}), 401


@auth_routes.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')

    if not current_password or not new_password:
        return jsonify({"success": False, "message": "Missing current or new password."}), 400

    if not current_user.check_password(current_password):
        return jsonify({"success": False, "message": "Current password is incorrect."}), 400

    current_user.set_password(new_password)

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


# Add a protected endpoint that only works if no admin exists:
@auth_routes.route('/setup-admin', methods=['POST'])
def setup_admin():
    if User.query.filter_by(role="admin").first():
        return jsonify({"error": "Admin already exists"}), 403

    data = request.get_json()
    result, status = register_user(data, default_role="admin")
    return jsonify(result), status
