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
    def create_or_get(cls, user_id):
        """Create or get cart for user"""
        try:
            collection = cls.get_collection()
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)

            print(f"DEBUG Cart: Creating or getting cart for user {user_id}")

            # Try to find existing cart
            cart = collection.find_one({'user': user_id})

            if not cart:
                # Create new cart
                cart = {
                    'user': user_id,
                    'items': [],
                    'total': 0,
                    'createdAt': datetime.utcnow(),
                    'updatedAt': datetime.utcnow()
                }
                result = collection.insert_one(cart)
                cart['_id'] = result.inserted_id
                print(f"DEBUG Cart: Created new cart {cart['_id']}")
            else:
                print(f"DEBUG Cart: Found existing cart {cart['_id']} with {len(cart.get('items', []))} items")

            return cart
        except Exception as e:
            print(f"ERROR in Cart.create_or_get: {e}")
            import traceback
            traceback.print_exc()
            raise

    @classmethod
    def find_by_user(cls, user_id):
        """Find cart by user ID"""
        try:
            collection = cls.get_collection()
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)

            print(f"DEBUG Cart: Finding cart for user {user_id}")
            cart = collection.find_one({'user': user_id})

            if not cart:
                print(f"DEBUG Cart: No cart found for user {user_id}")
                return None

            print(f"DEBUG Cart: Found cart with {len(cart.get('items', []))} items")

            # Populate product details
            if cart and cart.get('items'):
                for item in cart['items']:
                    try:
                        product_id = item['product']
                        print(f"DEBUG Cart: Fetching product {product_id}")
                        product = Product.find_by_id(product_id)
                        if product:
                            item['productDetails'] = Product.to_dict(product)
                            print(f"DEBUG Cart: Product found - {product['name']}")
                        else:
                            print(f"WARNING Cart: Product {product_id} not found")
                            # Keep a minimal product reference
                            item['productDetails'] = {
                                '_id': str(product_id),
                                'name': 'Product Not Available',
                                'image': '❓',
                                'price': item.get('price', 0),
                                'stock': 0
                            }
                    except Exception as e:
                        print(f"WARNING Cart: Error fetching product details: {e}")
                        import traceback
                        traceback.print_exc()

            return cart
        except Exception as e:
            print(f"ERROR in Cart.find_by_user: {e}")
            import traceback
            traceback.print_exc()
            return None

    @classmethod
    def add_item(cls, user_id, product_id, quantity=1):
        """Add item to cart"""
        try:
            collection = cls.get_collection()
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            if isinstance(product_id, str):
                product_id = ObjectId(product_id)

            print(f"DEBUG Cart: Adding item - User: {user_id}, Product: {product_id}, Qty: {quantity}")

            # Get product
            product = Product.find_by_id(product_id)
            if not product:
                print(f"ERROR Cart: Product not found - {product_id}")
                raise ValueError('Product not found')

            print(f"DEBUG Cart: Product found - {product['name']}, Stock: {product['stock']}")

            # Check stock
            if product['stock'] < quantity:
                print(f"ERROR Cart: Insufficient stock - Available: {product['stock']}, Requested: {quantity}")
                raise ValueError(f"Only {product['stock']} items available")

            # Get or create cart
            cart = cls.create_or_get(user_id)

            # Check if item already in cart
            item_exists = False
            for item in cart.get('items', []):
                if item['product'] == product_id:
                    old_qty = item['quantity']
                    item['quantity'] += quantity
                    item_exists = True
                    print(f"DEBUG Cart: Updated existing item quantity from {old_qty} to {item['quantity']}")
                    break

            # Add new item if not exists
            if not item_exists:
                new_item = {
                    'product': product_id,
                    'quantity': quantity,
                    'price': product['price']
                }
                if 'items' not in cart:
                    cart['items'] = []
                cart['items'].append(new_item)
                print(f"DEBUG Cart: Added new item to cart")

            # Calculate total
            total = sum(item['price'] * item['quantity'] for item in cart['items'])
            print(f"DEBUG Cart: Calculated total: ${total}")

            # Update cart
            result = collection.update_one(
                {'user': user_id},
                {
                    '$set': {
                        'items': cart['items'],
                        'total': total,
                        'updatedAt': datetime.utcnow()
                    }
                }
            )
            print(f"DEBUG Cart: Updated cart in database - Modified: {result.modified_count}")

            # Get updated cart
            return cls.find_by_user(user_id)

        except ValueError as ve:
            # Re-raise ValueError as-is
            raise ve
        except Exception as e:
            print(f"ERROR in Cart.add_item: {e}")
            import traceback
            traceback.print_exc()
            raise

    @classmethod
    def update_item(cls, user_id, product_id, quantity):
        """Update item quantity in cart"""
        try:
            collection = cls.get_collection()
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            if isinstance(product_id, str):
                product_id = ObjectId(product_id)

            print(f"DEBUG Cart: Updating item - User: {user_id}, Product: {product_id}, New Qty: {quantity}")

            if quantity < 1:
                raise ValueError('Quantity must be at least 1')

            # Get cart
            cart = cls.find_by_user(user_id)
            if not cart:
                raise ValueError('Cart not found')

            # Check product stock
            product = Product.find_by_id(product_id)
            if not product:
                raise ValueError('Product not found')
            if product['stock'] < quantity:
                raise ValueError(f"Only {product['stock']} items available")

            # Update item
            item_found = False
            for item in cart['items']:
                if item['product'] == product_id:
                    old_qty = item['quantity']
                    item['quantity'] = quantity
                    item_found = True
                    print(f"DEBUG Cart: Updated quantity from {old_qty} to {quantity}")
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

        except Exception as e:
            print(f"ERROR in Cart.update_item: {e}")
            import traceback
            traceback.print_exc()
            raise

    @classmethod
    def remove_item(cls, user_id, product_id):
        """Remove item from cart"""
        try:
            collection = cls.get_collection()
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            if isinstance(product_id, str):
                product_id = ObjectId(product_id)

            print(f"DEBUG Cart: Removing item - User: {user_id}, Product: {product_id}")

            # Get cart
            cart = cls.find_by_user(user_id)
            if not cart:
                raise ValueError('Cart not found')

            # Remove item
            original_count = len(cart['items'])
            cart['items'] = [item for item in cart['items'] if item['product'] != product_id]

            if len(cart['items']) == original_count:
                raise ValueError('Item not found in cart')

            print(f"DEBUG Cart: Item removed, {len(cart['items'])} items remaining")

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

        except Exception as e:
            print(f"ERROR in Cart.remove_item: {e}")
            import traceback
            traceback.print_exc()
            raise

    @classmethod
    def clear(cls, user_id):
        """Clear cart"""
        try:
            collection = cls.get_collection()
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)

            print(f"DEBUG Cart: Clearing cart for user {user_id}")

            result = collection.update_one(
                {'user': user_id},
                {
                    '$set': {
                        'items': [],
                        'total': 0,
                        'updatedAt': datetime.utcnow()
                    }
                }
            )

            print(f"DEBUG Cart: Cart cleared - Modified: {result.modified_count}")
            return True

        except Exception as e:
            print(f"ERROR in Cart.clear: {e}")
            import traceback
            traceback.print_exc()
            raise

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
                            'price': item.get('price', 0),
                            'stock': 0
                        }

                item_dict = {
                    'product': item.get('productDetails', {
                        '_id': str(item['product']),
                        'name': 'Unknown Product',
                        'image': '❓',
                        'price': item.get('price', 0)
                    }),
                    'quantity': item.get('quantity', 0),
                    'price': item.get('price', 0)
                }
                items.append(item_dict)
            except Exception as e:
                print(f"WARNING Cart.to_dict: Error processing cart item: {e}")
                continue

        return {
            '_id': str(cart.get('_id', '')),
            'user': str(cart.get('user', '')),
            'items': items,
            'total': cart.get('total', 0),
            'updatedAt': cart.get('updatedAt', datetime.utcnow()).isoformat() if cart.get('updatedAt') else None
        }
