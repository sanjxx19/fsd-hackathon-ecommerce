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
    try:
        collection = cls.get_collection()
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)

        print(f"DEBUG Cart.find_by_user - Looking for cart with user_id: {user_id}")
        cart = collection.find_one({'user': user_id})

        if not cart:
            print(f"DEBUG Cart.find_by_user - No cart found")
            return None

        print(f"DEBUG Cart.find_by_user - Cart found with {len(cart.get('items', []))} items")

        # Populate product details
        if cart and cart.get('items'):
            for item in cart['items']:
                try:
                    product = Product.find_by_id(item['product'])
                    if product:
                        item['productDetails'] = Product.to_dict(product)
                    else:
                        print(f"Warning: Product {item['product']} not found")
                except Exception as e:
                    print(f"Warning: Error fetching product details: {e}")

        return cart
    except Exception as e:
        print(f"ERROR in Cart.find_by_user: {e}")
        import traceback
        traceback.print_exc()
        return None
