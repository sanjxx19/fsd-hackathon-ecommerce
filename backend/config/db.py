from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance

    def connect(self):
        """Connect to MongoDB"""
        try:
            mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/flash_sale')
            self._client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)

            # Extract database name from URI or use default
            if '/' in mongodb_uri.split('://')[-1]:
                db_name = mongodb_uri.split('/')[-1].split('?')[0]
            else:
                db_name = 'flash_sale'

            self._db = self._client[db_name]

            # Test connection
            self._client.admin.command('ping')
            print(f"✅ Connected to MongoDB: {db_name}")

            # Create indexes
            self.create_indexes()

            return self._db
        except ConnectionFailure as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise

    def create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # User indexes
            self._db.users.create_index([("email", ASCENDING)], unique=True)
            self._db.users.create_index([("totalPurchases", DESCENDING)])

            # Product indexes
            self._db.products.create_index([("category", ASCENDING)])
            self._db.products.create_index([("stock", ASCENDING)])
            self._db.products.create_index([("sold", DESCENDING)])
            self._db.products.create_index([("saleEndTime", ASCENDING)])

            # Order indexes
            self._db.orders.create_index([("user", ASCENDING), ("createdAt", DESCENDING)])
            self._db.orders.create_index([("orderId", ASCENDING)], unique=True)
            self._db.orders.create_index([("checkoutTime", ASCENDING)])

            # Cart indexes
            self._db.carts.create_index([("user", ASCENDING)], unique=True)

            print("✅ Database indexes created successfully")
        except Exception as e:
            print(f"⚠️  Warning: Could not create indexes: {e}")

    def get_db(self):
        """Get database instance"""
        if self._db is None:
            self.connect()
        return self._db

    def close(self):
        """Close database connection"""
        if self._client:
            self._client.close()
            print("🔒 MongoDB connection closed")

# Singleton instance
db = Database()

def get_database():
    """Helper function to get database instance"""
    return db.get_db()
