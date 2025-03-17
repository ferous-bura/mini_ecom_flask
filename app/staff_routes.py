from flask import jsonify, request, render_template, redirect, url_for, Blueprint
from app.common.product_crud import get_products, add_product, update_product, delete_product
from app.common.order_crud import get_orders, update_delivery_status
from app.common.category_crud import get_categories, add_category, update_category, delete_category
from app.common.delivery_crud import get_delivery_options, assign_delivery
from app.common.payment_crud import process_payment
from app import db
from app.models import Order, DeliveryOption
from util.helpers import permission_required

staff_routes = Blueprint('staff', __name__)

@staff_routes.route('/products', methods=['GET'])
@permission_required('can_manage_products')
def manage_products(current_user):
    products = get_products(None)
    return render_template('manage_products.html', products=products)

@staff_routes.route('/products/add', methods=['POST'])
@permission_required('can_manage_products')
def add_staff_product():
    data = request.form.to_dict()
    images = request.files.getlist('images')
    result = add_product(None, data, images)
    return redirect(url_for('staff.manage_products'))

@staff_routes.route('/orders', methods=['GET'])
@permission_required('can_manage_orders')
def manage_orders():
    orders = get_orders(None)
    delivery_options = get_delivery_options()
    return render_template('manage_orders.html', orders=orders, delivery_options=delivery_options)

@staff_routes.route('/orders/update_delivery/<int:order_id>', methods=['POST'])
@permission_required('can_manage_deliveries')
def update_delivery_option(order_id):
    delivery_option_id = request.form.get('delivery_option_id')
    result, status = update_delivery_status(None, order_id, delivery_option_id)
    return redirect(url_for('staff.manage_orders'))

@staff_routes.route('/orders/assign_delivery/<int:order_id>', methods=['POST'])
@permission_required('can_manage_deliveries')
def assign_delivery_to_order(order_id):
    delivery_user_id = request.form.get('delivery_user_id')
    result = assign_delivery(order_id, delivery_user_id)
    return jsonify(result), 200

@staff_routes.route('/orders/update_payment/<int:order_id>', methods=['POST'])
@permission_required('can_manage_payment')
def update_payment_status(order_id):
    payment_status = request.form.get('payment_status')
    result = process_payment(order_id, payment_status)
    return redirect(url_for('staff.manage_orders'))

