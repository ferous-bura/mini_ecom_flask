import base64
import io

import qrcode
from flask import url_for, render_template, current_app, send_from_directory, Blueprint

from util.utils import UPLOAD_FOLDER

template_routes = Blueprint('templates', __name__)


@template_routes.route('/uploads/images/<filename>')
def serve_uploaded_file(filename):
    print(f'filename: {filename}')
    print(f'destination {UPLOAD_FOLDER, filename}')
    return send_from_directory(UPLOAD_FOLDER, filename)


@template_routes.route('<filename>')
def serve_uploaded_file2(filename):
    print(f'filename: {filename}')
    print(f'destination {UPLOAD_FOLDER, filename}')
    return send_from_directory(UPLOAD_FOLDER, filename)


def generate_qr_code(url):
    qr = qrcode.make(url)
    img_io = io.BytesIO()
    qr.save(img_io, format='PNG')
    img_io.seek(0)
    return base64.b64encode(img_io.getvalue()).decode()


@template_routes.route('/2', methods=['GET'])
def homepage2():
    home_url = url_for('templates.homepage', _external=True)
    qr_code_data = generate_qr_code(home_url)
    urls = [rule.rule for rule in current_app.url_map.iter_rules()]
    return render_template('index.html', qr_code_data=qr_code_data, urls=urls)


@template_routes.route('/', methods=['GET'])
def homepage():
    # Generate QR code for the homepage URL
    home_url = url_for('templates.homepage', _external=True)
    qr_code_data = generate_qr_code(home_url)

    # Get all registered buyer_routes from the bot_api
    urls = [rule.rule for rule in current_app.url_map.iter_rules()]
    # print(f' urls {urls}' )

    # Render the template
    return render_template('index.html', qr_code_data=qr_code_data, urls=urls)

@customer_routes.route('/cart', methods=['GET'])
@token_required
def view_cart(current_user):
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    delivery_options = DeliveryOption.query.all()
    return render_template('cart.html', cart_items=cart_items, delivery_options=delivery_options)

