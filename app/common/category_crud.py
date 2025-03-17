from flask import jsonify
from app import db
from app.models import Category

def get_categories():
    return [{"id": c.id, "name": c.name} for c in Category.query.all()]

def add_category(name):
    category = Category(name=name)
    db.session.add(category)
    db.session.commit()
    return {"message": "Category added", "category_id": category.id}

def update_category(category_id, name):
    category = Category.query.get_or_404(category_id)
    category.name = name
    db.session.commit()
    return {"message": "Category updated"}

def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return {"message": "Category deleted"}