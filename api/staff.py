import io
import os

from PIL import Image
from flask import Blueprint, flash, render_template, request, redirect, url_for, current_app, jsonify, \
    send_from_directory
from werkzeug.utils import secure_filename

from . import db
from .models import User, Product, Category, Order, OrderItem, Settings, ProductImage, ProductRating, DeliveryOption

# Use an absolute path relative to the project root
# UPLOAD_FOLDER = os.path.join(current_app.root_path, '..', 'uploads', 'images')
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
staff = Blueprint('staff', __name__)


@staff.route('/uploads/<path:filename>')
def serve_uploaded_file(filename):
    return send_from_directory(os.path.join(current_app.root_path, 'uploads'), filename)


# Dashboard Route
@staff.route('/')
def dashboard():
    return render_template('admin_dashboard.html')


# API Endpoints for Dashboard Data
@staff.route('/dashboard/stats')
def get_dashboard_stats():
    total_users = User.query.count()
    active_users = User.query.filter_by(confirmed=True).count()
    total_products = Product.query.count()
    out_of_stock_products = Product.query.filter(Product.id.notin_(db.session.query(OrderItem.product_id))).count()
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(approved=False).count()
    total_revenue = sum(order.total_amount for order in Order.query.all())  # Simple revenue calc
    avg_order_value = total_revenue / total_orders if total_orders else 0.0

    return jsonify({
        'total_users': total_users,
        'active_users': active_users,
        'total_products': total_products,
        'out_of_stock_products': out_of_stock_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
        'avg_order_value': avg_order_value
    })


@staff.route('/dashboard/recent_users')
def get_recent_users():
    recent_users = User.query.order_by(User.id.desc()).limit(5).all()
    users_data = [{'name': user.full_name, 'email': user.email, 'joined': user.id} for user in recent_users]
    return jsonify(users_data)


@staff.route('/dashboard/top_products')
def get_top_products():
    # Simplified top products based on order items (could be enhanced with actual sales data)
    top_products = db.session.query(Product, db.func.count(OrderItem.product_id).label('sales_count')) \
        .join(OrderItem).group_by(Product.id).order_by(db.func.count(OrderItem.product_id).desc()).limit(3).all()
    top_products_data = [
        {'name': p.name, 'sales': s, 'revenue': f"${p.price * s:.2f}"}
        for p, s in top_products
    ]
    return jsonify(top_products_data)


# Users CRUD
@staff.route('/users')
def manage_users():
    users = User.query.all()
    return render_template('manage_users.html', users=users)


@staff.route('/users/add', methods=['POST'])
def add_user():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    if not name or not email or not password:
        flash('Required fields are missing.', 'error')
        return redirect(url_for('staff.manage_users'))

    user = User(full_name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash('User added successfully!', 'success')
    return redirect(url_for('staff.manage_users'))


@staff.route('/users/edit', methods=['POST'])
def edit_user():
    user_id = request.form.get('user_id')
    name = request.form.get('name')
    email = request.form.get('email')

    user = User.query.get_or_404(user_id)
    user.full_name = name
    user.email = email
    db.session.commit()
    flash('User updated successfully!', 'success')
    return redirect(url_for('staff.manage_users'))


@staff.route('/users/delete/<int:user_id>')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('staff.manage_users'))


# Helper function to calculate average rating
def calculate_average_rating(ratings):
    if not ratings:
        return 0
    total = sum(rating.rating for rating in ratings)
    return total / len(ratings)


# Products CRUD
@staff.route('/products')
def manage_products():
    products = Product.query.all()
    categories = Category.query.all()
    products_with_avg = []
    for product in products:
        avg_rating = calculate_average_rating(product.ratings)
        products_with_avg.append({
            'product': product,
            'avg_rating': avg_rating,
            'num_reviews': len(product.ratings)
        })
    return render_template('manage_products.html', products_with_avg=products_with_avg, categories=categories)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


@staff.route('/products/add', methods=['POST'])
def add_product():
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    stock_quantity = request.form.get('stock_quantity')
    sku = request.form.get('sku')
    category_id = request.form.get('category_id')
    images = request.files.getlist('images')

    if not name or not price or not category_id or not stock_quantity:
        flash('Required fields are missing.', 'error')
        return redirect(url_for('staff.manage_products'))

    product = Product(
        name=name,
        description=description,
        price=float(price),
        stock_quantity=int(stock_quantity),
        sku=sku,
        category_id=int(category_id)
    )
    db.session.add(product)
    db.session.flush()

    for image in images:
        if image and image.filename:
            if not allowed_file(image.filename):
                flash('Invalid image format. Allowed formats: PNG, JPG, JPEG, GIF.', 'error')
                return redirect(url_for('staff.manage_products'))
            filename = secure_filename(image.filename)
            image_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
            image.save(image_path)
            image_url = url_for('staff.serve_uploaded_file', filename=f'images/{filename}', _external=True)
            product_image = ProductImage(product_id=product.id, image_url=image_url)
            db.session.add(product_image)

    db.session.commit()
    flash('Product added successfully!', 'success')
    return redirect(url_for('staff.manage_products'))


@staff.route('/products/edit', methods=['POST'])
def edit_product():
    product_id = request.form.get('product_id')
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    stock_quantity = request.form.get('stock_quantity')
    sku = request.form.get('sku')
    category_id = request.form.get('category_id')
    images = request.files.getlist('images')

    product = Product.query.get_or_404(product_id)
    product.name = name
    product.description = description
    product.price = float(price)
    product.stock_quantity = int(stock_quantity)
    product.sku = sku
    product.category_id = int(category_id)

    for image in images:
        if image and image.filename:
            filename = secure_filename(image.filename)
            image_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
            image.save(image_path)
            image_url = url_for('staff.serve_uploaded_file', filename=f'images/{filename}', _external=True)
            print(f'image url: {image_url}')
            product_image = ProductImage(product_id=product.id, image_url=image_url)
            db.session.add(product_image)

    db.session.commit()
    flash('Product updated successfully!', 'success')
    return redirect(url_for('staff.manage_products'))


def compress_image(image):
    img = Image.open(image)
    img = img.convert('RGB')
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=85)
    output.seek(0)
    return output


@staff.route('/products/delete/<int:product_id>')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    # Delete associated image files from disk
    for image in product.images:
        filename = image.image_url.split('/')[-1]
        image_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
        if os.path.exists(image_path):
            os.remove(image_path)
    # Delete the product (images will be deleted automatically due to CASCADE)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('staff.manage_products'))


@staff.route('/products/<int:product_id>')
def product_details(product_id):
    product = Product.query.get_or_404(product_id)
    product.images = sorted(product.images, key=lambda x: x.order)  # Sort images by order
    categories = Category.query.all()
    avg_rating = calculate_average_rating(product.ratings)
    return render_template('product_details.html', product=product, categories=categories, avg_rating=avg_rating,
                           num_reviews=len(product.ratings))


@staff.route('/images/edit', methods=['POST'])
def edit_image():
    image_id = request.form.get('image_id')
    image_file = request.files.get('image')
    text_overlay = request.form.get('text_overlay')

    product_image = ProductImage.query.get_or_404(image_id)
    if image_file and image_file.filename:
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
        image_file.save(image_path)
        product_image.image_url = url_for('staff.serve_uploaded_file', filename=f'images/{filename}', _external=True)
    product_image.text_overlay = text_overlay
    product_image.edited = True
    db.session.commit()
    return jsonify({'status': 'success'})


# Categories CRUD
@staff.route('/categories')
def manage_categories():
    categories = Category.query.all()
    return render_template('manage_categories.html', categories=categories)


@staff.route('/categories/add', methods=['POST'])
def add_category():
    name = request.form.get('category')
    if not name:
        flash('Category name is required.', 'error')
        return redirect(url_for('staff.manage_categories'))
    category = Category(name=name)
    db.session.add(category)
    db.session.commit()
    flash('Category added successfully!', 'success')
    return redirect(url_for('staff.manage_categories'))


@staff.route('/categories/edit', methods=['POST'])
def edit_category():
    category_id = request.form.get('category_id')
    name = request.form.get('category')
    category = Category.query.get_or_404(category_id)
    category.name = name
    db.session.commit()
    flash('Category updated successfully!', 'success')
    return redirect(url_for('staff.manage_categories'))


@staff.route('/categories/delete/<int:category_id>')
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('staff.manage_categories'))


# Orders CRUD with Delivery and Payment
@staff.route('/orders')
def manage_orders():
    orders = Order.query.all()
    delivery_options = DeliveryOption.query.all()
    return render_template('manage_orders.html', orders=orders, delivery_options=delivery_options)


@staff.route('/orders/approve/<int:order_id>')
def approve_order(order_id):
    order = Order.query.get_or_404(order_id)
    order.approved = True
    db.session.commit()
    flash('Order approved successfully!', 'success')
    return redirect(url_for('staff.manage_orders'))


@staff.route('/orders/delete/<int:order_id>')
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    flash('Order deleted successfully!', 'success')
    return redirect(url_for('staff.manage_orders'))


@staff.route('/orders/update_payment/<int:order_id>', methods=['POST'])
def update_payment_status(order_id):
    order = Order.query.get_or_404(order_id)
    payment_status = request.form.get('payment_status')
    if payment_status in ['Pending', 'Paid', 'Failed']:
        order.payment_status = payment_status
        db.session.commit()
        flash(f'Payment status updated to {payment_status}.', 'success')
    else:
        flash('Invalid payment status.', 'error')
    return redirect(url_for('staff.manage_orders'))


@staff.route('/orders/update_delivery/<int:order_id>', methods=['POST'])
def update_delivery_option(order_id):
    order = Order.query.get_or_404(order_id)
    delivery_option_id = request.form.get('delivery_option_id')
    if delivery_option_id:
        delivery_option = DeliveryOption.query.get_or_404(delivery_option_id)
        order.delivery_option_id = delivery_option_id
        order.delivery_fee = delivery_option.base_fee  # Simple fee assignment (can be enhanced)
        order.total_amount = sum(item.quantity * item.product.price for item in order.order_items) + order.delivery_fee
        db.session.commit()
        flash('Delivery option updated successfully!', 'success')
    else:
        flash('Please select a delivery option.', 'error')
    return redirect(url_for('staff.manage_orders'))


# Delivery Options Management
@staff.route('/delivery_options')
def manage_delivery_options():
    delivery_options = DeliveryOption.query.all()
    return render_template('manage_delivery_options.html', delivery_options=delivery_options)


@staff.route('/delivery_options/add', methods=['POST'])
def add_delivery_option():
    name = request.form.get('name')
    base_fee = request.form.get('base_fee')
    description = request.form.get('description')
    if not name or not base_fee:
        flash('Name and base fee are required.', 'error')
        return redirect(url_for('staff.manage_delivery_options'))
    delivery_option = DeliveryOption(name=name, base_fee=float(base_fee), description=description)
    db.session.add(delivery_option)
    db.session.commit()
    flash('Delivery option added successfully!', 'success')
    return redirect(url_for('staff.manage_delivery_options'))


@staff.route('/delivery_options/edit', methods=['POST'])
def edit_delivery_option():
    delivery_id = request.form.get('delivery_id')
    name = request.form.get('name')
    base_fee = request.form.get('base_fee')
    description = request.form.get('description')
    delivery_option = DeliveryOption.query.get_or_404(delivery_id)
    delivery_option.name = name
    delivery_option.base_fee = float(base_fee)
    delivery_option.description = description
    db.session.commit()
    flash('Delivery option updated successfully!', 'success')
    return redirect(url_for('staff.manage_delivery_options'))


@staff.route('/delivery_options/delete/<int:delivery_id>')
def delete_delivery_option(delivery_id):
    delivery_option = DeliveryOption.query.get_or_404(delivery_id)
    db.session.delete(delivery_option)
    db.session.commit()
    flash('Delivery option deleted successfully!', 'success')
    return redirect(url_for('staff.manage_delivery_options'))


# Settings CRUD
@staff.route('/settings', methods=['GET', 'POST'])
def manage_settings():
    settings = Settings.query.first()
    if not settings:
        settings = Settings(site_name="My Ecommerce Site", contact_email="contact@example.com")
        db.session.add(settings)
        db.session.commit()
    if request.method == 'POST':
        settings.site_name = request.form.get('site_name')
        settings.contact_email = request.form.get('contact_email')
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('staff.manage_settings'))
    return render_template('manage_settings.html', settings=settings)


@staff.route('/settings/update', methods=['POST'])
def update_settings():
    settings = Settings.query.first()
    if not settings:
        settings = Settings(site_name="My Ecommerce Site", contact_email="contact@example.com")
        db.session.add(settings)

    site_name = request.form.get('site_name')
    contact_email = request.form.get('contact_email')

    if not site_name or not contact_email:
        flash('Site name and contact email are required.', 'error')
        return redirect(url_for('staff.manage_settings'))

    settings.site_name = site_name
    settings.contact_email = contact_email
    try:
        db.session.commit()
        flash('Settings updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating settings: {str(e)}', 'error')
    return redirect(url_for('staff.manage_settings'))


@staff.route('/products/<int:product_id>/reorder_images', methods=['POST'])
def reorder_images(product_id):
    product = Product.query.get_or_404(product_id)
    image_order = request.json.get('image_order', [])

    # Update the order of images (you might need to add an order column to ProductImage)
    for index, image_id in enumerate(image_order):
        image = ProductImage.query.get_or_404(image_id)
        if image.product_id == product.id:
            image.order = index  # Assuming you add an order column to ProductImage

    db.session.commit()
    return jsonify({'status': 'success'})


@staff.route('/ratings/<int:rating_id>/reply', methods=['POST'])
def add_reply(rating_id):
    parent_rating = ProductRating.query.get_or_404(rating_id)
    comment = request.form.get('comment')
    if not comment:
        flash('Reply cannot be empty.', 'error')
        return redirect(url_for('staff.product_details', product_id=parent_rating.product_id))

    # For simplicity, assume the reply is from a logged-in admin user (user_id=1)
    reply = ProductRating(
        product_id=parent_rating.product_id,
        user_id=1,  # Replace with actual logged-in user ID in a real application
        rating=0,  # Replies don't need a rating
        comment=comment,
        parent_id=rating_id
    )
    db.session.add(reply)
    db.session.commit()
    flash('Reply added successfully!', 'success')
    return redirect(url_for('staff.product_details', product_id=parent_rating.product_id))


@staff.route('/ratings/<int:rating_id>/delete')
def delete_rating(rating_id):
    rating = ProductRating.query.get_or_404(rating_id)
    product_id = rating.product_id
    db.session.delete(rating)
    db.session.commit()
    flash('Comment deleted successfully!', 'success')
    return redirect(url_for('staff.product_details', product_id=product_id))


@staff.route('/images/<int:image_id>/delete')
def delete_image(image_id):
    image = ProductImage.query.get_or_404(image_id)
    product_id = image.product_id
    filename = image.image_url.split('/')[-1]
    image_path = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
    if os.path.exists(image_path):
        os.remove(image_path)
    db.session.delete(image)
    db.session.commit()
    flash('Image deleted successfully!', 'success')
    return redirect(url_for('staff.product_details', product_id=product_id))


@staff.route('/products/<int:product_id>/duplicate')
def duplicate_product(product_id):
    product = Product.query.get_or_404(product_id)
    new_product = Product(
        name=f"{product.name} (Copy)",
        description=product.description,
        price=product.price,
        stock_quantity=product.stock_quantity,
        sku=f"{product.sku}-COPY" if product.sku else None,
        category_id=product.category_id
    )
    db.session.add(new_product)
    db.session.flush()

    # Duplicate images
    for image in product.images:
        new_image = ProductImage(
            product_id=new_product.id,
            image_url=image.image_url,
            edited=image.edited,
            text_overlay=image.text_overlay,
            order=image.order
        )
        db.session.add(new_image)

    db.session.commit()
    flash('Product duplicated successfully!', 'success')
    return redirect(url_for('staff.manage_products'))
