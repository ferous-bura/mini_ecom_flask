# api/__init__.py
import os

from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


# Option 1: Define inside a function with app context
# def init_upload_folder(app):
#     global UPLOAD_FOLDER
#     UPLOAD_FOLDER = os.path.join(app.root_path, '..', 'uploads', 'images')
#     os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def create_app():
    app = Flask(__name__, static_folder='../static', template_folder='../templates')
    # init_upload_folder(app)
    # Configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'replace-this-with-a-secure-random-secret')

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)  # Ensure this is called after db.init_app

    # Import models to ensure they are registered with SQLAlchemy
    from .models import User, Product, Order, Category, ProductImage, ProductRating, CartItem, OrderItem, Settings

    # Register blueprints
    from .templates import customers_routes
    app.register_blueprint(customers_routes, url_prefix='/')

    from .routes import api_routes
    app.register_blueprint(api_routes, url_prefix='/api')

    from .staff import staff
    app.register_blueprint(staff, url_prefix='/staff')

    return app
