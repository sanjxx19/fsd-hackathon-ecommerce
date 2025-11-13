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

        print(f"DEBUG - User ID: {user_id}")
        print(f"DEBUG - Request data: {data}")

        product_id = data.get('productId')
        quantity = data.get('quantity', 1)

        # Validate input
        if not product_id:
            print("DEBUG - Missing product ID")
            return jsonify({
                'success': False,
                'error': 'Product ID is required'
            }), 400

        # Check if product_id is valid ObjectId format
        if not ObjectId.is_valid(product_id):
            print(f"DEBUG - Invalid ObjectId format: {product_id}")
            return jsonify({
                'success': False,
                'error': 'Invalid product ID format'
            }), 400

        if quantity < 1:
            print(f"DEBUG - Invalid quantity: {quantity}")
            return jsonify({
                'success': False,
                'error': 'Quantity must be at least 1'
            }), 400

        # Check if product exists first
        product = Product.find_by_id(product_id)
        if not product:
            print(f"DEBUG - Product not found: {product_id}")
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404

        print(f"DEBUG - Found product: {product['name']}, Stock: {product['stock']}")

        # Add to cart
        try:
            cart = Cart.add_item(user_id, product_id, quantity)
            print(f"DEBUG - Successfully added to cart")
        except ValueError as e:
            print(f"DEBUG - ValueError in add_item: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 409
        except Exception as e:
            print(f"DEBUG - Exception in add_item: {str(e)}")
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
        print(f"DEBUG - Outer exception: {str(e)}")
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
        print(f"DEBUG get_cart - User ID: {user_id}")

        # Get cart
        cart = Cart.find_by_user(user_id)
        print(f"DEBUG get_cart - Cart found: {cart is not None}")

        if not cart:
            print(f"DEBUG get_cart - No cart found, creating new one")
            cart = Cart.create_or_get(user_id)

        print(f"DEBUG get_cart - Cart items count: {len(cart.get('items', []))}")

        cart_dict = Cart.to_dict(cart)
        print(f"DEBUG get_cart - Cart dict created successfully")

        return jsonify({
            'success': True,
            'cart': cart_dict
        }), 200

    except Exception as e:
        print(f"DEBUG get_cart - Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to fetch cart',
            'message': str(e)
        }), 500


# Also update the Cart.to_dict() method in backend/models/cart.py
# Replace it with this safer version:

@classmethod
def to_dict(cls, cart):
    """Convert cart document to dictionary"""
    if not cart:
        return {
            '_id': None,
            'user': None,
            'items': [],
            'total': 0,
            'updatedAt': None
        }

    items = []
    for item in cart.get('items', []):
        try:
            # Get product details if not already populated
            if 'productDetails' not in item:
                product = Product.find_by_id(item['product'])
                if product:
                    item['productDetails'] = Product.to_dict(product)
                else:
                    # Product not found, use placeholder
                    item['productDetails'] = {
                        '_id': str(item['product']),
                        'name': 'Product Not Found',
                        'image': '❓',
                        'price': item.get('price', 0)
                    }

            item_dict = {
                'product': item.get('productDetails', {
                    '_id': str(item['product']),
                    'name': 'Unknown Product',
                    'image': '❓'
                }),
                'quantity': item.get('quantity', 0),
                'price': item.get('price', 0)
            }
            items.append(item_dict)
        except Exception as e:
            print(f"Warning: Error processing cart item: {e}")
            continue

    return {
        '_id': str(cart.get('_id', '')),
        'user': str(cart.get('user', '')),
        'items': items,
        'total': cart.get('total', 0),
        'updatedAt': cart.get('updatedAt', datetime.utcnow()).isoformat() if cart.get('updatedAt') else None
    }
