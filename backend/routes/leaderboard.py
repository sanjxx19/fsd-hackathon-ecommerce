from flask import Blueprint, request, jsonify
from models.user import User
from models.order import Order
from middleware.auth import optional_auth

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('', methods=['GET'])
@optional_auth
def get_leaderboard():
    """Get leaderboard rankings"""
    try:
        # Get query parameters
        limit = int(request.args.get('limit', 10))
        sort_by = request.args.get('sortBy', 'totalPurchases')

        # Get all users
        db = User.get_collection()

        # Build sort criteria
        if sort_by == 'checkoutTime':
            # Sort by fastest checkout (ascending, nulls last)
            users = list(db.find({
                'fastestCheckout': {'$ne': None}
            }).sort('fastestCheckout', 1).limit(limit))
        else:  # totalPurchases
            users = list(db.find().sort('totalPurchases', -1).limit(limit))

        # Build leaderboard with additional stats
        leaderboard = []
        for rank, user in enumerate(users, 1):
            # Get user's order count
            order_count = Order.get_total_count(user['_id'])

            leaderboard.append({
                'rank': rank,
                'user': {
                    'id': str(user['_id']),
                    'name': user['name']
                },
                'totalPurchases': round(user.get('totalPurchases', 0), 2),
                'fastestCheckout': user.get('fastestCheckout'),
                'totalOrders': order_count
            })

        return jsonify({
            'success': True,
            'leaderboard': leaderboard
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch leaderboard',
            'message': str(e)
        }), 500
