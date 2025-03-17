# migrate_images_to_cloudinary.py
import os

import cloudinary.uploader

from app import create_app, db
from app.models import ProductImage

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

app = create_app()
with app.app_context():
    images = ProductImage.query.all()
    for image in images:
        # Extract the filename from the current image_url
        filename = image.image_url.split('/')[-1]
        local_path = os.path.join(app.root_path, 'uploads', 'images', filename)

        if os.path.exists(local_path):
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(local_path, folder="ecommerce/products")
            new_image_url = upload_result['secure_url']

            # Update the image_url in the database
            image.image_url = new_image_url
            db.session.commit()
            print(f"Uploaded image for product {image.product_id}: {new_image_url}")
        else:
            print(f"Local file not found for product {image.product_id}: {local_path}")
