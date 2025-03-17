from flask import jsonify, request, Blueprint

from util.helpers import seller_required
from . import db
from .models import Order, OrderItem, Product, Notification

seller_routes = Blueprint('seller', __name__)


# Seller product management
@seller_routes.route('/products', methods=['GET'])
@seller_required
def get_seller_products(current_user):
    products = Product.query.filter_by(seller_id=current_user.id).all()  # Assume seller_id added
    product_list = [{
        "id": p.id,
        "name": p.name,
        "price": p.price,
        "stock_quantity": p.stock_quantity,
        "category": p.category.name if p.category else None
    } for p in products]
    return jsonify(product_list), 200


@seller_routes.route('/products/add', methods=['POST'])
@seller_required
def add_seller_product(current_user):
    data = request.get_json()
    new_product = Product(
        name=data['name'],
        price=data['price'],
        stock_quantity=data['stock_quantity'],
        category_id=data['category_id'],
        seller_id=current_user.id  # Link to seller
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Product added", "product_id": new_product.id}), 201


@seller_routes.route('/products/<int:product_id>', methods=['PUT'])
@seller_required
def edit_seller_product(current_user, product_id):
    product = Product.query.filter_by(id=product_id, seller_id=current_user.id).first()
    if not product:
        return jsonify({"error": "Product not found or not yours"}), 404
    data = request.get_json()
    product.name = data.get('name', product.name)
    product.price = data.get('price', product.price)
    product.stock_quantity = data.get('stock_quantity', product.stock_quantity)
    db.session.commit()
    return jsonify({"message": "Product updated"}), 200


@seller_routes.route('/products/<int:product_id>', methods=['DELETE'])
@seller_required
def delete_seller_product(current_user, product_id):
    product = Product.query.filter_by(id=product_id, seller_id=current_user.id).first()
    if not product:
        return jsonify({"error": "Product not found or not yours"}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"}), 200


# Seller sales tracking
@seller_routes.route('/sales', methods=['GET'])
@seller_required
def get_seller_sales(current_user):
    orders = Order.query.join(OrderItem).join(Product).filter(Product.seller_id == current_user.id).all()
    sales_data = [{
        "order_id": o.id,
        "total_amount": o.total_amount,
        "created_at": o.created_at.isoformat(),
        "items": [{"product_name": oi.product.name, "quantity": oi.quantity} for oi in o.order_items]
    } for o in orders]
    total_revenue = sum(o.total_amount for o in orders)
    return jsonify({"sales": sales_data, "total_revenue": total_revenue}), 200


@seller_routes.route('/products/<int:product_id>/availability', methods=['PATCH'])
@seller_required
def update_product_availability(current_user, product_id):
    product = Product.query.filter_by(id=product_id, seller_id=current_user.id).first()
    if not product:
        return jsonify({"error": "Product not found or not yours"}), 404
    data = request.get_json()

    # Update availability or stock
    if 'stock_quantity' in data:
        product.stock_quantity = data['stock_quantity']
        low_stock_warning = product.stock_quantity < 5
    else:
        low_stock_warning = False

    if 'is_available' in data:
        product.is_available = data['is_available']

    if 'availability_date' in data:
        product.availability_date = data['availability_date']

    db.session.commit()

    # Notify buyers if required
    notification_message = None
    if low_stock_warning:
        notification_message = f"Product '{product.name}' is running low on stock."
    elif not product.is_available:
        notification_message = f"Product '{product.name}' is currently unavailable."

    return jsonify({
        "message": "Product availability updated",
        "product_id": product.id,
        "low_stock_warning": low_stock_warning,
        "notification": notification_message
    }), 200


@seller_routes.route('/orders', methods=['GET'])
@seller_required
def get_seller_orders(current_user):
    orders = Order.query.join(OrderItem).join(Product).filter(Product.seller_id == current_user.id).all()
    order_list = [{
        "id": o.id,
        "total_amount": o.total_amount,
        "delivery_status": o.delivery_option.name if o.delivery_option else "Pending",
        "payment_status": o.payment_status,
        "items": [{"product_name": oi.product.name, "quantity": oi.quantity} for oi in o.order_items]
    } for o in orders]
    return jsonify(order_list), 200


@seller_routes.route('/orders/update_delivery/<int:order_id>', methods=['PUT'])
@seller_required
def update_seller_delivery(current_user, order_id):
    order = Order.query.join(OrderItem).join(Product).filter(Product.seller_id == current_user.id,
                                                             Order.id == order_id).first()
    if not order:
        return jsonify({"error": "Order not found or not yours"}), 404
    data = request.get_json()
    order.delivery_option_id = data.get('delivery_option_id')
    db.session.commit()

    # Notify user
    notification = Notification(
        title="Delivery Update",
        user_id=order.user_id,
        type="delivery_update",
        message=f"Order #{order.id} delivery updated to {data['delivery_status']}",
        data={"order_id": order.id, "delivery_status": data['delivery_status']},
        is_read=False,
        is_sent=False
    )
    db.session.add(notification)
    db.session.commit()
    return jsonify({"message": "Delivery updated"}), 200
