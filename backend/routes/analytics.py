from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from models.order import Order
from models.product import Product
from collections import defaultdict

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/sales', methods=['GET'])
def get_sales_analytics():
    """Get sales analytics (In production, add admin auth)"""
    try:
        # Get date range from query parameters
        start_date_str = request.args.get('startDate')
        end_date_str = request.args.get('endDate')

        # Build date filter
        date_filter = {}
        if start_date_str:
            start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
            date_filter['$gte'] = start_date
        if end_date_str:
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            date_filter['$lte'] = end_date

        query = {}
        if date_filter:
            query['createdAt'] = date_filter

        # Get all orders in range
        orders = Order.find_all(query)

        # Calculate analytics
        total_sales = sum(order['total'] for order in orders)
        total_orders = len(orders)
        average_order_value = total_sales / total_orders if total_orders > 0 else 0
        average_checkout_time = sum(order['checkoutTime'] for order in orders) / total_orders if total_orders > 0 else 0

        # Hourly breakdown
        hourly_data = defaultdict(lambda: {'orders': 0, 'sales': 0})
        for order in orders:
            hour = order['createdAt'].strftime('%H:00')
            hourly_data[hour]['orders'] += 1
            hourly_data[hour]['sales'] += order['total']

        hourly_breakdown = [
            {
                'hour': hour,
                'orders': data['orders'],
                'sales': round(data['sales'], 2)
            }
            for hour, data in sorted(hourly_data.items())
        ]

        # Peak hour
        peak_hour = max(hourly_data.items(), key=lambda x: x[1]['orders'])[0] if hourly_data else None

        # Top products
        product_sales = defaultdict(lambda: {'units': 0, 'revenue': 0, 'name': '', 'category': ''})
        for order in orders:
            for item in order.get('items', []):
                product_id = str(item['product'])
                product = Product.find_by_id(item['product'])
                if product:
                    product_sales[product_id]['name'] = product['name']
                    product_sales[product_id]['category'] = product['category']
                product_sales[product_id]['units'] += item['quantity']
                product_sales[product_id]['revenue'] += item['price'] * item['quantity']

        top_products = [
            {
                'product': {
                    'name': data['name'] or 'Unknown Product',
                    'category': data['category'] or 'Unknown'
                },
                'unitsSold': data['units'],
                'revenue': round(data['revenue'], 2)
            }
            for product_id, data in sorted(product_sales.items(), key=lambda x: x[1]['revenue'], reverse=True)[:5]
        ]

        return jsonify({
            'success': True,
            'analytics': {
                'totalSales': round(total_sales, 2),
                'totalOrders': total_orders,
                'averageOrderValue': round(average_order_value, 2),
                'averageCheckoutTime': round(average_checkout_time, 2),
                'peakHour': peak_hour,
                'hourlyBreakdown': hourly_breakdown,
                'topProducts': top_products
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch analytics',
            'message': str(e)
        }), 500

@analytics_bp.route('/products', methods=['GET'])
def get_product_performance():
    """Get product performance analytics (In production, add admin auth)"""
    try:
        # Get all products
        products = Product.find_all()

        # Get all orders
        orders = Order.find_all()

        # Calculate product performance
        product_stats = {}
        for product in products:
            product_id = str(product['_id'])
            product_stats[product_id] = {
                'product': {
                    '_id': product_id,
                    'name': product['name']
                },
                'sold': product.get('sold', 0),
                'revenue': 0,
                'orderCount': 0
            }

        # Calculate revenue from orders
        for order in orders:
            for item in order.get('items', []):
                product_id = str(item['product'])
                if product_id in product_stats:
                    product_stats[product_id]['revenue'] += item['price'] * item['quantity']
                    product_stats[product_id]['orderCount'] += 1

        # Convert to list and add calculated fields
        performance_list = []
        for stats in product_stats.values():
            stats['revenue'] = round(stats['revenue'], 2)
            stats['averageSelloutSpeed'] = 0  # Mock value
            stats['conversionRate'] = round(stats['orderCount'] / 100, 2) if stats['orderCount'] > 0 else 0
            performance_list.append(stats)

        # Sort by revenue
        performance_list.sort(key=lambda x: x['revenue'], reverse=True)

        return jsonify({
            'success': True,
            'products': performance_list
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch product performance',
            'message': str(e)
        }), 500

@analytics_bp.route('/traffic', methods=['GET'])
def get_traffic_analytics():
    """Get traffic analytics (Mock data - In production, add admin auth)"""
    try:
        # Mock traffic data
        traffic = {
            'totalVisitors': 1250,
            'uniqueVisitors': 890,
            'peakTrafficTime': '14:00',
            'averageSessionDuration': 420,
            'bounceRate': 0.23,
            'conversionRate': 0.14
        }

        return jsonify({
            'success': True,
            'traffic': traffic
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to fetch traffic analytics',
            'message': str(e)
        }), 500
