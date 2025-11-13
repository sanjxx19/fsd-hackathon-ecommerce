from flask import Blueprint, request, jsonify
from models.cart import Cart
from models.product import Product
from middleware.auth import auth_required
from config.socket import emit_stock_update
from bson import ObjectId

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/add', methods=['POST'])
@auth_required
def add_to_cart():
    """Add item to cart"""
    try:
        user_id = request.user_id
        data = request.get_json()

        product_id = data.get('productId')
        quantity = data.get('quantity', 1)

        print(f"DEBUG: Add to cart request - User: {user_id}, Product: {product_id}, Qty: {quantity}")

        # Validate input
        if not product_id:
            return jsonify({
                'success': False,
                'error': 'Product ID is required'
            }), 400

        # Check if product_id is valid ObjectId format
        if not ObjectId.is_valid(product_id):
            print(f"DEBUG: Invalid ObjectId format: {product_id}")
            return jsonify({
                'success': False,
                'error': 'Invalid product ID format'
            }), 400

        if quantity < 1:
            return jsonify({
                'success': False,
                'error': 'Quantity must be at least 1'
            }), 400

        # Check if product exists first
        product = Product.find_by_id(product_id)
        if not product:
            print(f"DEBUG: Product not found: {product_id}")
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404

        # Check stock availability
        if product['stock'] < quantity:
            print(f"DEBUG: Insufficient stock. Available: {product['stock']}, Requested: {quantity}")
            return jsonify({
                'success': False,
                'error': f"Only {product['stock']} items available"
            }), 409

        # Add to cart
        try:
            cart = Cart.add_item(user_id, product_id, quantity)
            print(f"DEBUG: Successfully added to cart")
        except ValueError as e:
            print(f"DEBUG: ValueError in add_item: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 409
        except Exception as e:
            print(f"DEBUG: Exception in add_item: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'Failed to add item: {str(e)}'
            }), 500

        # Get updated product stock
        product = Product.find_by_id(product_id)
        if product:
            emit_stock_update(product_id, product['stock'])

        return jsonify({
            'success': True,
            'message': 'Item added to cart',
            'cart': Cart.to_dict(cart)
        }), 200

    except Exception as e:
        print(f"DEBUG: Outer exception in add_to_cart: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to add item to cart',
            'message': str(e)
        }), 500

@cart_bp.route('', methods=['GET'])
@auth_required
def get_cart():
    """Get user's cart"""
    try:
        user_id = request.user_id
        print(f"DEBUG: Getting cart for user: {user_id}")

        # Get cart
        cart = Cart.find_by_user(user_id)

        if not cart:
            # Create new cart if doesn't exist
            print(f"DEBUG: Creating new cart for user")
            cart = Cart.create_or_get(user_id)

        cart_dict = Cart.to_dict(cart)
        print(f"DEBUG: Cart retrieved with {len(cart_dict.get('items', []))} items")

        return jsonify({
            'success': True,
            'cart': cart_dict
        }), 200

    except Exception as e:
        print(f"DEBUG: Exception in get_cart: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to fetch cart',
            'message': str(e)
        }), 500

@cart_bp.route('/item/<product_id>', methods=['PUT'])
@auth_required
def update_cart_item(product_id):
    """Update item quantity in cart"""
    try:
        user_id = request.user_id
        data = request.get_json()

        quantity = data.get('quantity')
        print(f"DEBUG: Updating cart item - Product: {product_id}, New Qty: {quantity}")

        if quantity is None or quantity < 1:
            return jsonify({
                'success': False,
                'error': 'Valid quantity is required'
            }), 400

        # Update cart
        try:
            cart = Cart.update_item(user_id, product_id, quantity)
            print(f"DEBUG: Cart item updated successfully")
        except ValueError as e:
            print(f"DEBUG: ValueError in update_item: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 409

        # Get updated product stock
        product = Product.find_by_id(product_id)
        if product:
            emit_stock_update(product_id, product['stock'])

        return jsonify({
            'success': True,
            'message': 'Cart updated',
            'cart': Cart.to_dict(cart)
        }), 200

    except Exception as e:
        print(f"DEBUG: Exception in update_cart_item: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to update cart',
            'message': str(e)
        }), 500

@cart_bp.route('/item/<product_id>', methods=['DELETE'])
@auth_required
def remove_cart_item(product_id):
    """Remove item from cart"""
    try:
        user_id = request.user_id
        print(f"DEBUG: Removing item from cart - Product: {product_id}")

        # Remove item
        try:
            cart = Cart.remove_item(user_id, product_id)
            print(f"DEBUG: Item removed successfully")
        except ValueError as e:
            print(f"DEBUG: ValueError in remove_item: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 404

        return jsonify({
            'success': True,
            'message': 'Item removed from cart',
            'cart': Cart.to_dict(cart)
        }), 200

    except Exception as e:
        print(f"DEBUG: Exception in remove_cart_item: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to remove item',
            'message': str(e)
        }), 500

@cart_bp.route('/clear', methods=['DELETE'])
@auth_required
def clear_cart():
    """Clear entire cart"""
    try:
        user_id = request.user_id
        print(f"DEBUG: Clearing cart for user: {user_id}")

        Cart.clear(user_id)

        return jsonify({
            'success': True,
            'message': 'Cart cleared'
        }), 200

    except Exception as e:
        print(f"DEBUG: Exception in clear_cart: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to clear cart',
            'message': str(e)
        }), 500
