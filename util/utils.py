import base64
import io
import os

import qrcode
from PIL import Image

BASE_URL = os.getenv('BASE_URL')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')
TELEGRAM_TOKEN = "7769407638:AAGbEDQUvycuomAjWEuR5ELHnzTllxLT7GQ"  # Replace with your token

def generate_qr_code(url):
    qr = qrcode.make(url)
    img_io = io.BytesIO()
    qr.save(img_io, format='PNG')
    img_io.seek(0)
    return base64.b64encode(img_io.getvalue()).decode()


# Helper function to calculate average rating
def calculate_average_rating(ratings):
    if not ratings:
        return 0
    total = sum(rating.rating for rating in ratings)
    return total / len(ratings)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


def compress_image(image):
    img = Image.open(image)
    img = img.convert('RGB')
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=85)
    output.seek(0)
    return output
