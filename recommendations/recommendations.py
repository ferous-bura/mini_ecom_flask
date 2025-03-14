# recommendations/recommendations.py
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from api.models import User, Product, OrderItem

def get_recommendations(user_id, top_n=5):
    """
    Generates product recommendations for a given user using collaborative filtering.
    """
    user = User.query.get(user_id)
    if not user:
        return []

    # Get items purchased by the user
    user_purchases = OrderItem.query.join(Product).filter(OrderItem.user_id == user_id).all()
    purchased_product_ids = [item.product_id for item in user_purchases]

    # Get all products
    all_products = Product.query.all()
    product_ids = [product.id for product in all_products]

    # Create a user-item matrix
    user_item_matrix = pd.DataFrame(0, index=[user_id], columns=product_ids)
    for product_id in purchased_product_ids:
        user_item_matrix.loc[user_id, product_id] = 1

    # Calculate cosine similarity between users (or items)
    # In this simplified example, we're using item similarity
    item_similarity = cosine_similarity(pd.DataFrame([p.id for p in all_products]), pd.DataFrame([p.id for p in all_products]))
    item_similarity_df = pd.DataFrame(item_similarity, index=[p.name for p in all_products], columns=[p.name for p in all_products])

    # Get recommendations
    recommendations = item_similarity_df[all_products[0].name].sort_values(ascending=False)[1:top_n+1]
    recommended_product_ids = recommendations.index.tolist()

    # Return recommended products
    recommended_products = Product.query.filter(Product.id.in_(recommended_product_ids)).all()
    return recommended_products