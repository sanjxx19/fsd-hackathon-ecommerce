from flask import Blueprint, request, jsonify
from datetime import datetime
from models.order import Order
from models.cart import Cart
from middleware.auth import auth_required
from config.socket import emit_order_success, emit_stock_update, emit_leaderboard_update, emit_product_sold_out
from models.product import Product

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('', methods=['POST'])
@auth_required
def create_order():
    """Create a new order (checkout)"""
    try:
        user_id = request.user_id
        data = request.get_json()

        # Extract payment data
        payment_method = data.get('paymentMethod', 'card')
        checkout_start_str = data.get('checkoutStartTime')

        # Validate checkout start time
        if not checkout_start_str:
            return jsonify({
                'success': False,
                'error': 'Checkout start time is required'
            }), 400

        try:
            checkout_start_time = datetime.fromisoformat(checkout_start_str.replace('Z', '+00:00'))
        except:
            return jsonify({
                'success': False,
                'error': 'Invalid checkout start time format'
            }), 400

        # Get user's cart
        cart = Cart.find_by_user(user_id)

        if not cart or not cart.get('items'):
            return jsonify({
                'success': False,
                'error': 'Cart is empty'
            }), 400

        # Check stock availability for all items
        for item in cart['items']:
            available, message = Product.check_availability(item['product'], item['quantity'])
            if not available:
                return jsonify({
                    'success': False,
                    'error': f"Product unavailable: {message}"
                }), 409

        # Create order
        try:
            order = Order.create(
                user_id,
                cart['items'],
                {'paymentMethod': payment_method},
                checkout_start_time
            )
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 409

        # Clear cart
        Cart.clear(user_id)

        # Emit real-time events
        emit_order_success(user_id, {
            'orderId': order['orderId'],
            'total': order['total'],
            'checkoutTime': order['checkoutTime']
        })

        # Emit stock updates and check for sold out products
        for item in order['items']:
            product = Product.find_by_id(item['product'])
            if product:
                emit_stock_update(item['product'], product['stock'])

                if product['stock'] == 0:
                    emit_product_sold_out(item['product'], product['name'])

        # Emit leaderboard update
        emit_leaderboard_update()

        return jsonify({
            'success': True,
            'message': 'Order placed successfully',
            'order': Order.to_dict(order)
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to create order',
            'message': str(e)
        }), 500

@orders_bp.route('', methods=['GET'])
@auth_required
def get_user_orders():
    """Get user's orders"""
    try:
        user_id = request.user_id

        # Get pagination parameters
        limit = int(request.args.get('limit', 10))
        page = int(request.args.get('page', 1))

        # Get orders
        orders = Order.find_by_user(user_id, limit, page)

        # Convert to dict
        orders_list = [Order.to_dict(o) for o in orders]

        return jsonify({
            'success': True,
            'count': len(orders_list),
            'orders': orders_list
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch orders',
            'message': str(e)
        }), 500

@orders_bp.route('/<order_id>', methods=['GET'])
@auth_required
def get_order(order_id):
    """Get single order by order ID"""
    try:
        user_id = request.user_id

        # Get order
        order = Order.find_by_order_id(order_id)

        if not order:
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404

        # Check if order belongs to user
        if str(order['user']) != user_id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized access to order'
            }), 403

        return jsonify({
            'success': True,
            'order': Order.to_dict(order)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch order',
            'message': str(e)
        }), 500
