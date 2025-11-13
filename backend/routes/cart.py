from flask import Blueprint, request, jsonify
from models.cart import Cart
from models.product import Product
from middleware.auth import auth_required
from config.socket import emit_stock_update
from bson import ObjectId

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('', methods=['GET'])
@auth_required
def get_cart():
    """Get user's cart"""
    try:
        user_id = request.user_id

        # Get cart
        cart = Cart.find_by_user(user_id)

        if not cart:
            cart = Cart.create_or_get(user_id)

        return jsonify({
            'success': True,
            'cart': Cart.to_dict(cart)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch cart',
            'message': str(e)
        }), 500

@cart_bp.route('/add', methods=['POST'])
@auth_required
def add_to_cart():
    """Add item to cart"""
    try:
        user_id = request.user_id
        data = request.get_json()

        product_id = data.get('productId')
        quantity = data.get('quantity', 1)

        # Validate input
        if not product_id:
            return jsonify({
                'success': False,
                'error': 'Product ID is required'
            }), 400

        if not ObjectId.is_valid(product_id):
            return jsonify({
                'success': False,
                'error': 'Invalid product ID'
            }), 400

        if quantity < 1:
            return jsonify({
                'success': False,
                'error': 'Quantity must be at least 1'
            }), 400

        # Add to cart
        try:
            cart = Cart.add_item(user_id, product_id, quantity)
        except ValueError as e:
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
            'message': 'Item added to cart',
            'cart': Cart.to_dict(cart)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to add item to cart',
            'message': str(e)
        }), 500

@cart_bp.route('/item/<product_id>', methods=['PUT'])
@auth_required
def update_cart_item(product_id):
    """Update cart item quantity"""
    try:
        user_id = request.user_id
        data = request.get_json()

        quantity = data.get('quantity')

        # Validate input
        if not ObjectId.is_valid(product_id):
            return jsonify({
                'success': False,
                'error': 'Invalid product ID'
            }), 400

        if quantity is None or quantity < 0:
            return jsonify({
                'success': False,
                'error': 'Valid quantity is required'
            }), 400

        # Update cart
        try:
            cart = Cart.update_item(user_id, product_id, quantity)
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 409

        # Emit stock update
        product = Product.find_by_id(product_id)
        if product:
            emit_stock_update(product_id, product['stock'])

        return jsonify({
            'success': True,
            'message': 'Cart updated',
            'cart': Cart.to_dict(cart)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to update cart',
            'message': str(e)
        }), 500

@cart_bp.route('/item/<product_id>', methods=['DELETE'])
@auth_required
def remove_from_cart(product_id):
    """Remove item from cart"""
    try:
        user_id = request.user_id

        # Validate input
        if not ObjectId.is_valid(product_id):
            return jsonify({
                'success': False,
                'error': 'Invalid product ID'
            }), 400

        # Remove from cart
        try:
            cart = Cart.remove_item(user_id, product_id)
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 404

        # Emit stock update
        product = Product.find_by_id(product_id)
        if product:
            emit_stock_update(product_id, product['stock'])

        return jsonify({
            'success': True,
            'message': 'Item removed from cart',
            'cart': Cart.to_dict(cart)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to remove item',
            'message': str(e)
        }), 500

@cart_bp.route('', methods=['DELETE'])
@auth_required
def clear_cart():
    """Clear all items from cart"""
    try:
        user_id = request.user_id

        # Clear cart
        Cart.clear(user_id)

        return jsonify({
            'success': True,
            'message': 'Cart cleared'
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to clear cart',
            'message': str(e)
        }), 500
