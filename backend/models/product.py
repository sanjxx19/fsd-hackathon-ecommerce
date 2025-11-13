from datetime import datetime
from bson import ObjectId
from config.db import get_database

class Product:
    collection = None

    @classmethod
    def get_collection(cls):
        if cls.collection is None:
            db = get_database()
            cls.collection = db.products
        return cls.collection

    @classmethod
    def create(cls, product_data):
        """Create a new product"""
        collection = cls.get_collection()

        product = {
            'name': product_data['name'],
            'description': product_data['description'],
            'price': float(product_data['price']),
            'originalPrice': float(product_data['originalPrice']),
            'category': product_data['category'],
            'image': product_data['image'],
            'stock': int(product_data.get('stock', 0)),
            'sold': 0,
            'isActive': product_data.get('isActive', True),
            'saleStartTime': product_data['saleStartTime'],
            'saleEndTime': product_data['saleEndTime'],
            'createdAt': datetime.utcnow()
        }

        result = collection.insert_one(product)
        product['_id'] = result.inserted_id

        return product

    @classmethod
    def find_all(cls, filters=None, sort_by=None):
        """Find all products with optional filters"""
        collection = cls.get_collection()
        query = filters or {}

        # Build sort criteria
        sort_criteria = []
        if sort_by == 'price':
            sort_criteria.append(('price', 1))
        elif sort_by == 'sold':
            sort_criteria.append(('sold', -1))
        elif sort_by == 'stock':
            sort_criteria.append(('stock', -1))
        else:
            sort_criteria.append(('createdAt', -1))

        cursor = collection.find(query)
        if sort_criteria:
            cursor = cursor.sort(sort_criteria)

        return list(cursor)

    @classmethod
    def find_by_id(cls, product_id):
        """Find product by ID"""
        collection = cls.get_collection()
        if isinstance(product_id, str):
            product_id = ObjectId(product_id)
        return collection.find_one({'_id': product_id})

    @classmethod
    def update_stock(cls, product_id, quantity, operation='decrease'):
        """Update product stock"""
        collection = cls.get_collection()
        if isinstance(product_id, str):
            product_id = ObjectId(product_id)

        product = cls.find_by_id(product_id)
        if not product:
            raise ValueError('Product not found')

        if operation == 'decrease':
            if product['stock'] < quantity:
                raise ValueError('Insufficient stock')
            new_stock = product['stock'] - quantity
            update = {
                '$inc': {
                    'stock': -quantity,
                    'sold': quantity
                }
            }
        else:  # increase
            new_stock = product['stock'] + quantity
            update = {
                '$inc': {'stock': quantity}
            }

        result = collection.update_one({'_id': product_id}, update)

        return new_stock if result.modified_count > 0 else product['stock']

    @classmethod
    def update(cls, product_id, update_data):
        """Update product data"""
        collection = cls.get_collection()
        if isinstance(product_id, str):
            product_id = ObjectId(product_id)

        result = collection.update_one(
            {'_id': product_id},
            {'$set': update_data}
        )
        return result.modified_count > 0

    @classmethod
    def to_dict(cls, product):
        """Convert product document to dictionary"""
        if not product:
            return None

        discount_percent = round((1 - product['price'] / product['originalPrice']) * 100)

        return {
            '_id': str(product['_id']),
            'name': product['name'],
            'description': product['description'],
            'price': product['price'],
            'originalPrice': product['originalPrice'],
            'discountPercent': discount_percent,
            'category': product['category'],
            'image': product['image'],
            'stock': product['stock'],
            'sold': product.get('sold', 0),
            'isActive': product.get('isActive', True),
            'saleStartTime': product['saleStartTime'].isoformat() if isinstance(product['saleStartTime'], datetime) else product['saleStartTime'],
            'saleEndTime': product['saleEndTime'].isoformat() if isinstance(product['saleEndTime'], datetime) else product['saleEndTime'],
            'createdAt': product.get('createdAt', datetime.utcnow()).isoformat()
        }

    @classmethod
    def check_availability(cls, product_id, quantity):
        """Check if product has enough stock"""
        product = cls.find_by_id(product_id)
        if not product:
            return False, 'Product not found'

        if not product.get('isActive', True):
            return False, 'Product is not available'

        if product['stock'] < quantity:
            return False, f"Only {product['stock']} items available"

        return True, 'Available'
