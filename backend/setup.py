"""
Project setup script to create all necessary directories and __init__.py files
Run this once to set up the project structure
"""

import os

def create_directory_structure():
    """Create all necessary directories for the project"""

    directories = [
        'config',
        'models',
        'routes',
        'middleware',
        'logs',
        'uploads',
    ]

    print("🏗️  Creating project directory structure...")

    for directory in directories:
        os.makedirs(directory, exist_ok=True)

        # Create __init__.py for Python packages
        init_file = os.path.join(directory, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write(f'"""\n{directory.capitalize()} package\n"""\n')

        print(f"  ✅ Created: {directory}/")

    print("\n✅ Directory structure created successfully!")
    print("\n📁 Project structure:")
    print("""
flash-sale-backend/
├── server.py
├── seed_data.py
├── test_api.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
├── config/
│   ├── __init__.py
│   ├── db.py
│   └── socket.py
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── product.py
│   ├── cart.py
│   └── order.py
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   ├── products.py
│   ├── cart.py
│   ├── orders.py
│   ├── leaderboard.py
│   ├── analytics.py
│   └── payment.py
├── middleware/
│   ├── __init__.py
│   ├── auth.py
│   └── error_handler.py
└── logs/
    """)

def create_env_file():
    """Create .env file if it doesn't exist"""

    if os.path.exists('.env'):
        print("\n✅ .env file already exists")
        return

    print("\n📝 Creating .env file...")

    env_content = """PORT=5000
MONGODB_URI=mongodb://localhost:27017/flash_sale
JWT_SECRET=your_super_secret_jwt_key_change_this_in_production
NODE_ENV=development
GEMINI_API_KEY=your_gemini_api_key_here
"""

    with open('.env', 'w') as f:
        f.write(env_content)

    print("  ✅ Created .env file")
    print("  ⚠️  Remember to update JWT_SECRET and GEMINI_API_KEY!")

def main():
    """Main setup function"""

    print("""
╔═══════════════════════════════════════════════════════╗
║       🚀 Flash Sale Backend - Project Setup          ║
║                                                       ║
║  This script will create the necessary directories   ║
║  and files for the project                           ║
╚═══════════════════════════════════════════════════════╝
    """)

    try:
        create_directory_structure()
        create_env_file()

        print("""
✨ Setup complete! Next steps:

1. Install dependencies:
   pip install -r requirements.txt

2. Make sure MongoDB is running:
   mongod

3. Seed the database:
   python seed_data.py

4. Start the server:
   python server.py

5. Test the API:
   python test_api.py

📚 For more information, see README.md
        """)

    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
