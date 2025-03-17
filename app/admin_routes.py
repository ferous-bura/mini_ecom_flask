from flask import Blueprint, request, jsonify
from app import db
from app.models import User
from util.helpers import admin_required

admin_routes = Blueprint('admin', __name__)

"""
curl -X POST http://localhost:5000/auth/login \
-H "Content-Type: application/json" \
-d '{"email": "admin@example.com", "password": "admin123"}'



{
    "message": "Login successful",
    "userId": 1,
    "token": "some-uuid-token",
    "role": "admin",
    "isSeller": false
}



curl -X PUT http://localhost:5000/admin/users/2/role \
-H "Content-Type: application/json" \
-H "Authorization: Bearer some-uuid-token" \
-d '{"role": "staff"}'



{
    "message": "User role updated to staff",
    "user": {
        "id": 2,
        "full_name": "John Doe",
        "email": "john@example.com",
    }
}


{
    "message": "User role updated to staff",
    "user": {"id": 2, "email": "user@example.com", "role": "staff"}
}

curl -X PUT http://localhost:5000/admin/users/2/permissions \
-H "Content-Type: application/json" \
-H "Authorization: Bearer some-uuid-token" \
-d '{"permissions": {"can_manage_products": true, "can_manage_orders": false}}'


{
    "message": "User permissions updated",
    "user": {
        "id": 2,
        "email": "user@example.com",
        "permissions": {"can_manage_products": true, "can_manage_orders": false}
    }
}


curl -X GET http://localhost:5000/admin/users \
-H "Authorization: Bearer some-uuid-token"


{
    "users": [
        {"id": 1, "full_name": "Admin User", "email": "admin@example.com", "role": "admin", "permissions": {}},
        {"id": 2, "full_name": "User", "email": "user@example.com", "role": "staff", "permissions": {"can_manage_products": true, "can_manage_orders": false}}
    ]
}


"""

@admin_routes.route('/users/<int:user_id>/role', methods=['PUT'])
@admin_required
def update_user_role(current_user, user_id):
    target_user = User.query.get_or_404(user_id)
    data = request.get_json()

    new_role = data.get('role')
    valid_roles = {"customer", "seller", "staff", "delivery", "admin"}

    if not new_role or new_role not in valid_roles:
        return jsonify({"error": "Invalid or missing role"}), 400

    if target_user.role == "admin" and new_role != "admin":
        # Prevent demoting the last admin unless another exists
        if User.query.filter_by(role="admin").count() <= 1:
            return jsonify({"error": "Cannot demote the last admin"}), 403

    target_user.role = new_role
    target_user.is_seller = (new_role == "seller")  # Sync is_seller with role

    db.session.commit()
    return jsonify({
        "message": f"User role updated to {new_role}",
        "user": {"id": target_user.id, "email": target_user.email, "role": target_user.role}
    }), 200


@admin_routes.route('/users/<int:user_id>/permissions', methods=['PUT'])
@admin_required
def update_user_permissions(current_user, user_id):
    target_user = User.query.get_or_404(user_id)
    data = request.get_json()

    if "permissions" not in data or not isinstance(data["permissions"], dict):
        return jsonify({"error": "Invalid or missing permissions"}), 400

    # Example permissions: can_manage_users, can_manage_products, can_manage_orders
    valid_permissions = {"can_manage_users", "can_manage_products", "can_manage_orders", "can_manage_deliveries", "can_manage_payment"}
    new_permissions = {k: bool(v) for k, v in data["permissions"].items() if k in valid_permissions}

    target_user.permissions = new_permissions
    db.session.commit()
    return jsonify({
        "message": "User permissions updated",
        "user": {"id": target_user.id, "email": target_user.email, "permissions": target_user.permissions}
    }), 200


@admin_routes.route('/users', methods=['GET'])
@admin_required
def list_users(current_user):
    users = User.query.all()
    user_list = [{
        "id": u.id,
        "full_name": u.full_name,
        "email": u.email,
        "role": u.role,
        "permissions": u.permissions
    } for u in users]
    return jsonify({"users": user_list}), 200
