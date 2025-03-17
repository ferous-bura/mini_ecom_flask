from flask import request, jsonify, Blueprint

from app import db
from app.models import Address
from util.helpers import token_required

address_routes = Blueprint('address', __name__)


@address_routes.route('/', methods=['POST'])
@token_required
def add_address(current_user):
    data = request.get_json()
    address = data.get('address')

    if not address:
        return jsonify({"success": False, "message": "Address is required!"}), 400

    new_address = Address(address=address, user_id=current_user.id)
    db.session.add(new_address)

    try:
        db.session.commit()
        return jsonify({"success": True, "message": "Address added successfully!"}), 200
    except:
        db.session.rollback()
        return jsonify({"success": False, "message": "Failed to add address."}), 500


@address_routes.route('/', methods=['DELETE'])
@token_required
def remove_address(current_user):
    data = request.get_json()
    address = data.get('address')

    address = Address.query.filter_by(user_id=current_user.id, address=address).first()

    if not address:
        return jsonify({"success": False, "message": "Address not found!"}), 404

    db.session.delete(address)

    try:
        db.session.commit()
        return jsonify({"success": True, "message": "Address removed successfully!"}), 200
    except:
        db.session.rollback()
        return jsonify({"success": False, "message": "Failed to remove address."}), 500


@address_routes.route('/', methods=['GET'])
@token_required
def get_addresses(current_user):
    addresses = Address.query.filter_by(user_id=current_user.id).all()
    addresses_list = [address.address for address in addresses]

    return jsonify({"success": True, "addresses": addresses_list}), 200
