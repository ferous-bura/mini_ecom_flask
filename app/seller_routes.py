from flask import jsonify, request, Blueprint
from util.helpers import seller_required
from app.common.product_crud import get_products, add_product, update_product, delete_product
from app.common.order_crud import get_orders, update_delivery_status
from app import db

seller_routes = Blueprint('seller', __name__)

@seller_routes.route('/products', methods=['GET'])
@seller_required
def get_seller_products(current_user):
    products = get_products(current_user.id, is_seller=True)
    return jsonify(products), 200

@seller_routes.route('/products/add', methods=['POST'])
@seller_required
def add_seller_product(current_user):
    data = request.get_json()
    result = add_product(current_user.id, data, is_seller=True)
    return jsonify(result), 201

@seller_routes.route('/products/<int:product_id>', methods=['PUT'])
@seller_required
def edit_seller_product(current_user, product_id):
    data = request.get_json()
    result, status = update_product(current_user.id, product_id, data, is_seller=True)
    return jsonify(result), status

@seller_routes.route('/products/<int:product_id>', methods=['DELETE'])
@seller_required
def delete_seller_product(current_user, product_id):
    result, status = delete_product(current_user.id, product_id, is_seller=True)
    return jsonify(result), status

@seller_routes.route('/orders', methods=['GET'])
@seller_required
def get_seller_orders(current_user):
    orders = get_orders(current_user.id, is_seller=True)
    return jsonify(orders), 200

@seller_routes.route('/orders/update_delivery/<int:order_id>', methods=['PUT'])
@seller_required
def update_seller_delivery(current_user, order_id):
    data = request.get_json()
    result, status = update_delivery_status(current_user.id, order_id, data['delivery_option_id'], is_seller=True)
    return jsonify(result), status