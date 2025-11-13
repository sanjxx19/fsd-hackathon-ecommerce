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

        print(f"DEBUG: Creating order for user: {user_id}")
        print(f"DEBUG: Request data: {data}")

        # Extract payment data
        payment_method = data.get('paymentMethod', 'card')
        checkout_start_str = data.get('checkoutStartTime')

        # Validate checkout start time
        if not checkout_start_str:
            print("DEBUG: Missing checkout start time")
            return jsonify({
                'success': False,
                'error': 'Checkout start time is required'
            }), 400

        try:
            # Handle different datetime formats - remove timezone info to make it naive
            if checkout_start_str.endswith('Z'):
                # Parse ISO format with Z
                checkout_start_time = datetime.strptime(
                    checkout_start_str.replace('Z', ''),
                    '%Y-%m-%dT%H:%M:%S.%f'
                )
            else:
                # Try parsing with fromisoformat and remove timezone
                checkout_start_time = datetime.fromisoformat(checkout_start_str.replace('Z', '+00:00'))
                if checkout_start_time.tzinfo is not None:
                    checkout_start_time = checkout_start_time.replace(tzinfo=None)

            print(f"DEBUG: Checkout start time (naive): {checkout_start_time}")
        except Exception as e:
            print(f"DEBUG: Error parsing datetime: {e}")
            return jsonify({
                'success': False,
                'error': f'Invalid checkout start time format: {str(e)}'
            }), 400

        # Get user's cart
        cart = Cart.find_by_user(user_id)
        print(f"DEBUG: Cart found: {cart is not None}")

        if not cart or not cart.get('items'):
            print("DEBUG: Cart is empty")
            return jsonify({
                'success': False,
                'error': 'Cart is empty'
            }), 400

        print(f"DEBUG: Cart has {len(cart['items'])} items")

        # Check stock availability for all items
        stock_issues = []
        for item in cart['items']:
            product_id = item['product']
            quantity = item['quantity']

            print(f"DEBUG: Checking stock for product {product_id}, quantity {quantity}")

            available, message = Product.check_availability(product_id, quantity)
            if not available:
                product = Product.find_by_id(product_id)
                product_name = product['name'] if product else str(product_id)
                stock_issues.append(f"{product_name}: {message}")
                print(f"DEBUG: Stock issue - {product_name}: {message}")

        if stock_issues:
            return jsonify({
                'success': False,
                'error': 'Some items are unavailable',
                'details': stock_issues
            }), 409

        # Create order
        try:
            print("DEBUG: Creating order...")
            order = Order.create(
                user_id,
                cart['items'],
                {'paymentMethod': payment_method},
                checkout_start_time
            )
            print(f"DEBUG: Order created successfully - Order ID: {order['orderId']}")
        except ValueError as e:
            print(f"DEBUG: ValueError creating order: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 409
        except Exception as e:
            print(f"DEBUG: Exception creating order: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'Failed to create order: {str(e)}'
            }), 500

        # Clear cart
        print("DEBUG: Clearing cart...")
        Cart.clear(user_id)

        # Emit real-time events
        print("DEBUG: Emitting real-time events...")
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

        print(f"DEBUG: Order completed successfully - {order['orderId']}")
        return jsonify({
            'success': True,
            'message': 'Order placed successfully',
            'order': Order.to_dict(order)
        }), 201

    except Exception as e:
        print(f"DEBUG: Outer exception in create_order: {str(e)}")
        import traceback
        traceback.print_exc()
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

        print(f"DEBUG: Fetching orders for user {user_id} - Page {page}, Limit {limit}")

        # Get orders
        orders = Order.find_by_user(user_id, limit, page)

        # Convert to dict
        orders_list = [Order.to_dict(o) for o in orders]

        print(f"DEBUG: Found {len(orders_list)} orders")

        return jsonify({
            'success': True,
            'count': len(orders_list),
            'orders': orders_list
        }), 200

    except Exception as e:
        print(f"DEBUG: Exception in get_user_orders: {str(e)}")
        import traceback
        traceback.print_exc()
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

        print(f"DEBUG: Fetching order {order_id} for user {user_id}")

        # Get order
        order = Order.find_by_order_id(order_id)

        if not order:
            print(f"DEBUG: Order not found: {order_id}")
            return jsonify({
                'success': False,
                'error': 'Order not found'
            }), 404

        # Check if order belongs to user
        if str(order['user']) != user_id:
            print(f"DEBUG: Unauthorized access attempt to order {order_id}")
            return jsonify({
                'success': False,
                'error': 'Unauthorized access to order'
            }), 403

        return jsonify({
            'success': True,
            'order': Order.to_dict(order)
        }), 200

    except Exception as e:
        print(f"DEBUG: Exception in get_order: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to fetch order',
            'message': str(e)
        }), 500
