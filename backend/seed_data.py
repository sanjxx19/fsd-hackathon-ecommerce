"""
Seed script to populate the database with sample data
Run this script after starting the MongoDB server
"""

from datetime import datetime, timedelta
from models.user import User
from models.product import Product
from config.db import db

def seed_database():
    """Seed the database with sample data"""

    print("🌱 Starting database seeding...")

    # Connect to database
    database = db.connect()

    # Clear existing data (optional - comment out to keep existing data)
    print("🗑️  Clearing existing data...")
    database.users.delete_many({})
    database.products.delete_many({})
    database.carts.delete_many({})
    database.orders.delete_many({})

    # Create sample users
    print("👥 Creating sample users...")
    sample_users = [
        {
            'name': 'John Doe',
            'email': 'john@example.com',
            'password': 'password123'
        },
        {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'password': 'password123'
        },
        {
            'name': 'Bob Wilson',
            'email': 'bob@example.com',
            'password': 'password123'
        }
    ]

    created_users = []
    for user_data in sample_users:
        try:
            user = User.create(
                user_data['name'],
                user_data['email'],
                user_data['password']
            )
            created_users.append(user)
            print(f"  ✅ Created user: {user_data['email']}")
        except ValueError as e:
            print(f"  ⚠️  User already exists: {user_data['email']}")

    # Create sample products
    print("🛍️  Creating sample products...")

    # Sale times (current time to 8 hours from now)
    sale_start = datetime.utcnow()
    sale_end = sale_start + timedelta(hours=8)

    sample_products = [
        {
            'name': 'Premium Headphones',
            'description': 'High-quality wireless headphones with noise cancellation',
            'price': 199.99,
            'originalPrice': 299.99,
            'category': 'Electronics',
            'image': '🎧',
            'stock': 50,
            'saleStartTime': sale_start,
            'saleEndTime': sale_end
        },
        {
            'name': 'Smart Watch Pro',
            'description': 'Advanced fitness tracker with heart rate monitoring',
            'price': 249.99,
            'originalPrice': 399.99,
            'category': 'Electronics',
            'image': '⌚',
            'stock': 30,
            'saleStartTime': sale_start,
            'saleEndTime': sale_end
        },
        {
            'name': 'Laptop Backpack',
            'description': 'Durable backpack with padded laptop compartment',
            'price': 49.99,
            'originalPrice': 79.99,
            'category': 'Accessories',
            'image': '🎒',
            'stock': 100,
            'saleStartTime': sale_start,
            'saleEndTime': sale_end
        },
        {
            'name': 'Wireless Mouse',
            'description': 'Ergonomic wireless mouse with precision tracking',
            'price': 29.99,
            'originalPrice': 49.99,
            'category': 'Electronics',
            'image': '🖱️',
            'stock': 75,
            'saleStartTime': sale_start,
            'saleEndTime': sale_end
        },
        {
            'name': 'USB-C Hub',
            'description': 'Multi-port USB-C hub with HDMI and card reader',
            'price': 39.99,
            'originalPrice': 69.99,
            'category': 'Accessories',
            'image': '🔌',
            'stock': 60,
            'saleStartTime': sale_start,
            'saleEndTime': sale_end
        },
        {
            'name': 'Portable SSD 1TB',
            'description': 'Fast portable SSD with 1TB storage capacity',
            'price': 89.99,
            'originalPrice': 149.99,
            'category': 'Storage',
            'image': '💾',
            'stock': 40,
            'saleStartTime': sale_start,
            'saleEndTime': sale_end
        },
        {
            'name': 'Mechanical Keyboard',
            'description': 'RGB mechanical keyboard with Cherry MX switches',
            'price': 129.99,
            'originalPrice': 199.99,
            'category': 'Electronics',
            'image': '⌨️',
            'stock': 25,
            'saleStartTime': sale_start,
            'saleEndTime': sale_end
        },
        {
            'name': 'Webcam 1080p',
            'description': 'Full HD webcam with auto-focus and built-in mic',
            'price': 59.99,
            'originalPrice': 99.99,
            'category': 'Electronics',
            'image': '📹',
            'stock': 45,
            'saleStartTime': sale_start,
            'saleEndTime': sale_end
        }
    ]

    created_products = []
    for product_data in sample_products:
        product = Product.create(product_data)
        created_products.append(product)
        discount = round((1 - product_data['price'] / product_data['originalPrice']) * 100)
        print(f"  ✅ Created product: {product_data['name']} ({discount}% off)")

    print(f"\n✨ Database seeded successfully!")
    print(f"  👥 Users created: {len(created_users)}")
    print(f"  🛍️  Products created: {len(created_products)}")
    print(f"\n📝 Sample credentials:")
    print(f"  Email: john@example.com")
    print(f"  Password: password123")
    print(f"\n🚀 You can now start the server with: python server.py")

if __name__ == '__main__':
    try:
        seed_database()
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
