from flask import Flask, url_for, current_app
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bot_api.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Replace with your email provider's SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'your_email_password'  # Replace with your email password

db = SQLAlchemy(app)
mail = Mail(app)

# Token generator for confirmation links
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
# serializer = URLSafeTimedSerializer('your-unique-secret-key')


def send_confirmation_email(user):
    token = serializer.dumps(user.email, salt='email-confirm')
    confirm_url = url_for('routes.confirm_email', token=token, _external=True)
    msg = Message('Confirm Email', sender=current_app.config['MAIL_USERNAME'], recipients=[user.email])
    msg.body = f'Hello {user.username}, please confirm your registration by clicking: {confirm_url}'
    mail.send(msg)
