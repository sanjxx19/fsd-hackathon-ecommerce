from datetime import datetime
from bson import ObjectId
import time
from config.db import get_database
from models.user import User
from models.product import Product

class Order:
    collection = None

    @classmethod
    def get_collection(cls):
        if cls.collection is None:
            db = get_database()
            cls.collection = db.orders
        return cls.collection

    @classmethod
    def generate_order_id(cls):
        """Generate unique order ID"""
        timestamp = int(time.time() * 1000)
        return f"ORD{timestamp}"

    @classmethod
    def create(cls, user_id, cart_items, payment_data, checkout_start_time):
        """Create a new order"""
        collection = cls.get_collection()
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        # Calculate checkout time
        checkout_time = (datetime.utcnow() - checkout_start_time).total_seconds()

        # Prepare order items
        order_items = []
        subtotal = 0

        for item in cart_items:
            product = Product.find_by_id(item['product'])
            if not product:
                raise ValueError(f"Product not found: {item['product']}")

            order_items.append({
                'product': item['product'],
                'name': product['name'],
                'quantity': item['quantity'],
                'price': item['price']
            })
            subtotal += item['price'] * item['quantity']

        # Calculate tax (10%)
        tax = round(subtotal * 0.1, 2)
        total = subtotal + tax

        # Create order
        order = {
            'orderId': cls.generate_order_id(),
            'user': user_id,
            'items': order_items,
            'subtotal': subtotal,
            'tax': tax,
            'total': total,
            'paymentMethod': payment_data.get('paymentMethod', 'card'),
            'paymentStatus': 'completed',  # Mock payment always succeeds
            'checkoutTime': round(checkout_time, 2),
            'checkoutStartTime': checkout_start_time,
            'createdAt': datetime.utcnow()
        }

        result = collection.insert_one(order)
        order['_id'] = result.inserted_id

        # Update user purchases
        User.update_purchases(user_id, total, checkout_time)

        # Update product stock
        for item in order_items:
            Product.update_stock(item['product'], item['quantity'], 'decrease')

        return order

    @classmethod
    def find_by_user(cls, user_id, limit=10, page=1):
        """Find orders by user ID"""
        collection = cls.get_collection()
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        skip = (page - 1) * limit

        cursor = collection.find({'user': user_id}).sort('createdAt', -1).skip(skip).limit(limit)
        orders = list(cursor)

        # Populate product details
        for order in orders:
            for item in order.get('items', []):
                product = Product.find_by_id(item['product'])
                if product:
                    item['productDetails'] = Product.to_dict(product)

        return orders

    @classmethod
    def find_by_order_id(cls, order_id):
        """Find order by order ID"""
        collection = cls.get_collection()
        order = collection.find_one({'orderId': order_id})

        if order:
            # Populate user details
            user = User.find_by_id(order['user'])
            if user:
                order['userDetails'] = User.to_dict(user)

            # Populate product details
            for item in order.get('items', []):
                product = Product.find_by_id(item['product'])
                if product:
                    item['productDetails'] = Product.to_dict(product)

        return order

    @classmethod
    def find_all(cls, filters=None, limit=None):
        """Find all orders with optional filters"""
        collection = cls.get_collection()
        query = filters or {}

        cursor = collection.find(query).sort('createdAt', -1)
        if limit:
            cursor = cursor.limit(limit)

        return list(cursor)

    @classmethod
    def get_total_count(cls, user_id=None):
        """Get total order count"""
        collection = cls.get_collection()
        query = {}
        if user_id:
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            query['user'] = user_id

        return collection.count_documents(query)

    @classmethod
    def to_dict(cls, order):
        """Convert order document to dictionary"""
        if not order:
            return None

        items = []
        for item in order.get('items', []):
            item_dict = {
                'product': str(item['product']),
                'name': item.get('name', 'Unknown Product'),
                'quantity': item['quantity'],
                'price': item['price']
            }

            if 'productDetails' in item:
                item_dict['productDetails'] = item['productDetails']

            items.append(item_dict)

        result = {
            'orderId': order['orderId'],
            'user': str(order['user']),
            'items': items,
            'subtotal': order['subtotal'],
            'tax': order['tax'],
            'total': order['total'],
            'paymentMethod': order.get('paymentMethod', 'card'),
            'paymentStatus': order.get('paymentStatus', 'pending'),
            'checkoutTime': order['checkoutTime'],
            'checkoutStartTime': order['checkoutStartTime'].isoformat(),
            'createdAt': order.get('createdAt', datetime.utcnow()).isoformat()
        }

        if 'userDetails' in order:
            result['user'] = order['userDetails']

        return result
