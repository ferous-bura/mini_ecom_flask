import base64
import io
import qrcode
from flask import url_for, render_template, current_app, Blueprint
customers_routes = Blueprint('customers', __name__)

def generate_qr_code(url):
    qr = qrcode.make(url)
    img_io = io.BytesIO()
    qr.save(img_io, format='PNG')
    img_io.seek(0)
    return base64.b64encode(img_io.getvalue()).decode()

@customers_routes.route('/', methods=['GET'])
def homepage():
    home_url = url_for('customers.homepage', _external=True)
    qr_code_data = generate_qr_code(home_url)
    urls = [rule.rule for rule in current_app.url_map.iter_rules()]
    return render_template('index.html', qr_code_data=qr_code_data, urls=urls)
