"""
Reset Database Script
This will clear all data and reseed the database
"""

from config.db import db
from seed_data import seed_database

def reset_database():
    """Reset the entire database"""

    print("=" * 60)
    print("DATABASE RESET SCRIPT")
    print("=" * 60)
    print()
    print("⚠️  WARNING: This will delete ALL data from the database!")
    print()

    confirmation = input("Type 'RESET' to confirm: ")

    if confirmation != 'RESET':
        print("\n❌ Reset cancelled")
        return

    print("\n🔧 Connecting to database...")
    database = db.connect()

    print("🗑️  Dropping all collections...")
    try:
        # Drop all collections
        collections = ['users', 'products', 'carts', 'orders']
        for collection_name in collections:
            database[collection_name].drop()
            print(f"  ✅ Dropped {collection_name}")
    except Exception as e:
        print(f"  ⚠️  Error dropping collections: {e}")

    print("\n🌱 Reseeding database...")
    try:
        seed_database()
        print("\n✅ Database reset complete!")
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("RESET COMPLETE")
    print("=" * 60)
    print("\n📝 Sample credentials:")
    print("  Email: john@example.com")
    print("  Password: password123")
    print("\n🚀 Start server with: python server.py")
    print()

if __name__ == '__main__':
    try:
        reset_database()
    except KeyboardInterrupt:
        print("\n\n⚠️  Reset interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
