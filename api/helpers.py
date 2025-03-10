# helpers.py
from functools import wraps
from flask import request, jsonify

import pyperclip
from .models import User
from api import db


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token or not token.startswith("Bearer "):
            return jsonify({"message": "Token is missing or invalid!"}), 401

        token = token.replace("Bearer ", "").strip()

        user = User.query.filter_by(token=token).first()
        if not user:
            return jsonify({"message": "Unauthorized access or invalid token!"}), 401

        return f(user, *args, **kwargs)

    return decorated



def copy_token_to_clipboard(token):
    try:
        pyperclip.copy(token)  # explicitly copies token to user's clipboard
        print("✅ Token copied to clipboard.")
    except Exception as e:
        print(f"⚠️ Unable to copy token to clipboard: {e}")
