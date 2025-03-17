# helpers.py
import os
import datetime
from functools import wraps

import jwt
import pyperclip
from flask import request, jsonify

from app.models import User

SECRET_KEY = os.getenv('SECRET_KEY')
# Helper function to generate JWT (reuse in login as well)
def generate_token(user):
    payload = {
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),  # expires in 7 days
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # print(f'request headers {request.headers}')

        token = request.headers.get('Authorization')

        if not token or not token.startswith("Bearer "):
            return jsonify({"message": "Token is missing or invalid!"}), 401

        token = token.replace("Bearer ", "").strip()

        user = User.query.filter_by(token=token).first()
        if not user:
            return jsonify({"message": "Unauthorized access or invalid token!"}), 401

        return f(user, *args, **kwargs)

    return decorated


# Middleware to check if user is a seller
def seller_required(f):
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if not current_user.is_seller:
            return jsonify({"error": "Seller access required"}), 403
        return f(current_user, *args, **kwargs)

    return decorated


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            if current_user.role != "admin" and not current_user.permissions.get(permission, False):
                return jsonify({"error": f"Permission {permission} required"}), 403
            return f(current_user, *args, **kwargs)
        return token_required(decorated_function)
    return decorator

def admin_required(f):
    @wraps(f)
    def decorated_function(current_user, *args, **kwargs):
        if current_user.role != "admin":
            return jsonify({"error": "Admin access required"}), 403
        return f(current_user, *args, **kwargs)
    return token_required(decorated_function)  # Requires token first


def copy_token_to_clipboard(token):
    try:
        pyperclip.copy(token)  # explicitly copies token to user's clipboard
        print("✅ Token copied to clipboard.")
    except Exception as e:
        print(f"⚠️ Unable to copy token to clipboard: {e}")


"""

import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"  # Store in environment variables

def generate_token(user):
    payload = {
        "user_id": user.id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                raise ValueError
        except Exception:
            return jsonify({"error": "Invalid or missing token"}), 401
        return f(current_user, *args, **kwargs)
    return decorated_function

"""