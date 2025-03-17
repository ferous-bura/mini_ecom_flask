from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import app

limiter = Limiter(app, key_func=get_remote_address)

# @auth_routes.route('/login', methods=['POST'])
# @limiter.limit("10 per minute")  # 10 attempts per minute
# def login():
#     # Existing login code
