from flask import Flask

app = Flask(__name__)

# Configuration settings can be added here
# app.config['SECRET_KEY'] = 'your_secret_key'

# Initialize any extensions or blueprints here

# Import routes to register them
from .main import *  # Import routes from main.py to register them with the app