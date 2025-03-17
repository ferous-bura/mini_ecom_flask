import os

from flask import url_for
from werkzeug.utils import secure_filename

from util.utils import UPLOAD_FOLDER
from app import db
from app.models import Product, ProductImage


def get_products(user_id, is_seller=False):
    query = Product.query.filter_by(seller_id=user_id) if is_seller else Product.query
    products = query.all()
    return [{
        "id": p.id,
        "name": p.name,
        "price": p.price,
        "stock_quantity": p.stock_quantity,
        "category": p.category.name if p.category else None
    } for p in products]


def add_product(user_id, data, images=None, is_seller=False):
    new_product = Product(
        name=data['name'],
        price=data['price'],
        stock_quantity=data['stock_quantity'],
        category_id=data['category_id'],
        seller_id=user_id if is_seller else None
    )
    db.session.add(new_product)
    db.session.flush()

    if images:
        for image in images:
            filename = secure_filename(image.filename)
            image.save(os.path.join(UPLOAD_FOLDER, filename))
            image_url = url_for('staff.serve_uploaded_file', filename=filename, _external=True)
            product_image = ProductImage(product_id=new_product.id, image_url=image_url)
            db.session.add(product_image)

    db.session.commit()
    return {"message": "Product added", "product_id": new_product.id}


def update_product(user_id, product_id, data, is_seller=False):
    query = Product.query.filter_by(id=product_id, seller_id=user_id) if is_seller else Product.query.filter_by(
        id=product_id)
    product = query.first()
    if not product:
        return {"error": "Product not found or not yours"}, 404
    product.name = data.get('name', product.name)
    product.price = data.get('price', product.price)
    product.stock_quantity = data.get('stock_quantity', product.stock_quantity)
    db.session.commit()
    return {"message": "Product updated"}


def delete_product(user_id, product_id, is_seller=False):
    query = Product.query.filter_by(id=product_id, seller_id=user_id) if is_seller else Product.query.filter_by(
        id=product_id)
    product = query.first()
    if not product:
        return {"error": "Product not found or not yours"}, 404
    db.session.delete(product)
    db.session.commit()
    return {"message": "Product deleted"}
