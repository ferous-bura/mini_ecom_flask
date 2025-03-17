# app/__init__.py
import os

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


# Option 1: Define inside a function with bot_api context
def init_upload_folder():
    global UPLOAD_FOLDER

    BASE_DIR_STEP_UP = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # this one takes one step up
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # this one takes its own location as the base

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'images')
    # UPLOAD_FOLDER = os.path.join('/home/bura/Desktop/dev/doing/ecommerce/mini_ecom_flask/uploads/images')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    print("UPLOAD_FOLDER path:", UPLOAD_FOLDER)
    return BASE_DIR, UPLOAD_FOLDER


def create_app():
    app = Flask(__name__, static_folder='../static', template_folder='../templates')
    base_dir, upload_folder = init_upload_folder()

    # Configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'replace-this-with-a-secure-random-secret')
    app.config['BASE_URL'] = os.getenv('BASE_URL', 'http://192.168.1.104:5000')
    app.config['BASE_DIR'] = os.getenv('base_dir', base_dir)
    app.config['UPLOAD_FOLDER'] = os.getenv('upload_folder', upload_folder)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)  # Ensure this is called after db.init_app


    # Import models to ensure they are registered with SQLAlchemy
    from .models import User, Product, Order, Category, ProductImage, ProductRating, CartItem, OrderItem, Settings

    from app.cart import cart_routes
    from app.checkout import checkout_routes
    from app.seller import seller_routes
    from app.staff import staff_routes
    from app.templates import template_routes
    from app.notification import notification_routes
    from app.order import order_routes
    from app.product import product_routes
    from app.address import address_routes
    from app.auth import auth_routes

    # Register blueprints
    app.register_blueprint(template_routes, url_prefix='/')
    app.register_blueprint(cart_routes, url_prefix='/cart')
    app.register_blueprint(checkout_routes, url_prefix='/checkout')
    app.register_blueprint(staff_routes, url_prefix='/staff')
    app.register_blueprint(seller_routes, url_prefix='/seller')
    app.register_blueprint(address_routes, url_prefix='/address')
    app.register_blueprint(product_routes, url_prefix='/product')
    app.register_blueprint(auth_routes, url_prefix='/auth')
    app.register_blueprint(notification_routes, url_prefix='/notification')
    app.register_blueprint(order_routes, url_prefix='/order')

    return app
