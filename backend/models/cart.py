from datetime import datetime
from bson import ObjectId
from config.db import get_database
from models.product import Product

class Cart:
    collection = None

    @classmethod
    def get_collection(cls):
        if cls.collection is None:
            db = get_database()
            cls.collection = db.carts
        return cls.collection

    @classmethod
    def find_by_user(cls, user_id):
        """Find cart by user ID"""
        collection = cls.get_collection()
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        cart = collection.find_one({'user': user_id})

        # Populate product details
        if cart and cart.get('items'):
            for item in cart['items']:
                product = Product.find_by_id(item['product'])
                if product:
                    item['productDetails'] = Product.to_dict(product)

        return cart

    @classmethod
    def create_or_get(cls, user_id):
        """Create cart if doesn't exist or return existing"""
        collection = cls.get_collection()
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        cart = collection.find_one({'user': user_id})

        if not cart:
            cart = {
                'user': user_id,
                'items': [],
                'total': 0,
                'updatedAt': datetime.utcnow()
            }
            result = collection.insert_one(cart)
            cart['_id'] = result.inserted_id

        return cart

    @classmethod
    def add_item(cls, user_id, product_id, quantity=1):
        """Add item to cart"""
        collection = cls.get_collection()
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        if isinstance(product_id, str):
            product_id = ObjectId(product_id)

        # Get product
        product = Product.find_by_id(product_id)
        if not product:
            raise ValueError('Product not found')

        # Check stock
        available, message = Product.check_availability(product_id, quantity)
        if not available:
            raise ValueError(message)

        # Get or create cart
        cart = cls.create_or_get(user_id)

        # Check if item already in cart
        item_found = False
        for item in cart['items']:
            if item['product'] == product_id:
                item['quantity'] += quantity
                item_found = True
                break

        # Add new item if not found
        if not item_found:
            cart['items'].append({
                'product': product_id,
                'quantity': quantity,
                'price': product['price']
            })

        # Calculate total
        total = sum(item['price'] * item['quantity'] for item in cart['items'])

        # Update cart
        collection.update_one(
            {'user': user_id},
            {
                '$set': {
                    'items': cart['items'],
                    'total': total,
                    'updatedAt': datetime.utcnow()
                }
            }
        )

        return cls.find_by_user(user_id)

    @classmethod
    def update_item(cls, user_id, product_id, quantity):
        """Update item quantity in cart"""
        collection = cls.get_collection()
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        if isinstance(product_id, str):
            product_id = ObjectId(product_id)

        if quantity <= 0:
            return cls.remove_item(user_id, product_id)

        # Check stock
        available, message = Product.check_availability(product_id, quantity)
        if not available:
            raise ValueError(message)

        cart = cls.find_by_user(user_id)
        if not cart:
            raise ValueError('Cart not found')

        # Update item quantity
        item_found = False
        for item in cart['items']:
            if item['product'] == product_id:
                item['quantity'] = quantity
                item_found = True
                break

        if not item_found:
            raise ValueError('Item not found in cart')

        # Calculate total
        total = sum(item['price'] * item['quantity'] for item in cart['items'])

        # Update cart
        collection.update_one(
            {'user': user_id},
            {
                '$set': {
                    'items': cart['items'],
                    'total': total,
                    'updatedAt': datetime.utcnow()
                }
            }
        )

        return cls.find_by_user(user_id)

    @classmethod
    def remove_item(cls, user_id, product_id):
        """Remove item from cart"""
        collection = cls.get_collection()
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        if isinstance(product_id, str):
            product_id = ObjectId(product_id)

        cart = cls.find_by_user(user_id)
        if not cart:
            raise ValueError('Cart not found')

        # Remove item
        cart['items'] = [item for item in cart['items'] if item['product'] != product_id]

        # Calculate total
        total = sum(item['price'] * item['quantity'] for item in cart['items'])

        # Update cart
        collection.update_one(
            {'user': user_id},
            {
                '$set': {
                    'items': cart['items'],
                    'total': total,
                    'updatedAt': datetime.utcnow()
                }
            }
        )

        return cls.find_by_user(user_id)

    @classmethod
    def clear(cls, user_id):
        """Clear all items from cart"""
        collection = cls.get_collection()
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        collection.update_one(
            {'user': user_id},
            {
                '$set': {
                    'items': [],
                    'total': 0,
                    'updatedAt': datetime.utcnow()
                }
            }
        )

        return cls.find_by_user(user_id)

    @classmethod
    def to_dict(cls, cart):
        """Convert cart document to dictionary"""
        if not cart:
            return None

        items = []
        for item in cart.get('items', []):
            item_dict = {
                'product': item.get('productDetails', {
                    '_id': str(item['product']),
                    'name': 'Unknown Product'
                }),
                'quantity': item['quantity'],
                'price': item['price']
            }
            items.append(item_dict)

        return {
            '_id': str(cart['_id']),
            'user': str(cart['user']),
            'items': items,
            'total': cart.get('total', 0),
            'updatedAt': cart.get('updatedAt', datetime.utcnow()).isoformat()
        }
