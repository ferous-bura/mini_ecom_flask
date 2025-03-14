# routes.py
from .recommendations.recommendations import get_recommendations

@api_routes.route('/recommendations/<int:user_id>', methods=['GET'])
@token_required
def get_user_recommendations(user_id):
    recommendations = get_recommendations(user_id)
    recommendation_list = []
    for product in recommendations:
        recommendation_list.append({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "image_url": product.imageUrl
        })
    return jsonify(recommendation_list), 200