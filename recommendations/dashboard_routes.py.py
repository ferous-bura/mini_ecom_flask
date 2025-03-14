# dashboard/routes.py
from flask import render_template
from . import dashboard
from api.models import Order, Product, User
from datetime import datetime

@dashboard.route('/dashboard')
def dashboard_index():
    total_orders = Order.query.count()
    total_users = User.query.count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()

    # Example: Get top 5 most viewed products (requires analytics data)
    # top_products = get_top_viewed_products(5)

    return render_template('admin_dashboard.html', total_orders=total_orders, total_users=total_users, recent_orders=recent_orders)