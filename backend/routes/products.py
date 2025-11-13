from flask import Blueprint, request, jsonify
from models.product import Product
from middleware.auth import optional_auth
from bson import ObjectId

products_bp = Blueprint('products', __name__)

@products_bp.route('', methods=['GET'])
@optional_auth
def get_all_products():
    """Get all products with optional filters"""
    try:
        # Get query parameters
        category = request.args.get('category')
        in_stock = request.args.get('inStock')
        sort_by = request.args.get('sortBy')

        # Build filters
        filters = {}
        if category:
            filters['category'] = category
        if in_stock == 'true':
            filters['stock'] = {'$gt': 0}

        # Get products
        products = Product.find_all(filters, sort_by)

        # Convert to dict
        products_list = [Product.to_dict(p) for p in products]

        return jsonify({
            'success': True,
            'count': len(products_list),
            'products': products_list
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch products',
            'message': str(e)
        }), 500

@products_bp.route('/<product_id>', methods=['GET'])
@optional_auth
def get_product(product_id):
    """Get single product by ID"""
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(product_id):
            return jsonify({
                'success': False,
                'error': 'Invalid product ID'
            }), 400

        # Get product
        product = Product.find_by_id(product_id)

        if not product:
            return jsonify({
                'success': False,
                'error': 'Product not found'
            }), 404

        return jsonify({
            'success': True,
            'product': Product.to_dict(product)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch product',
            'message': str(e)
        }), 500

@products_bp.route('/<product_id>/stock', methods=['PATCH'])
def update_product_stock(product_id):
    """Update product stock (Admin endpoint - in production, add admin auth)"""
    try:
        # Validate ObjectId
        if not ObjectId.is_valid(product_id):
            return jsonify({
                'success': False,
                'error': 'Invalid product ID'
            }), 400

        data = request.get_json()
        new_stock = data.get('stock')

        if new_stock is None or new_stock < 0:
            return jsonify({
                'success': False,
                'error': 'Valid stock value is required'
            }), 400

        # Update stock
        success = Product.update(product_id, {'stock': int(new_stock)})

        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to update stock'
            }), 500

        # Get updated product
        product = Product.find_by_id(product_id)

        return jsonify({
            'success': True,
            'message': 'Stock updated successfully',
            'product': {
                '_id': str(product['_id']),
                'stock': product['stock']
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to update stock',
            'message': str(e)
        }), 500
