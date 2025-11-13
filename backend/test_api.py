"""
Quick API test script to verify endpoints are working
Run this after starting the server to test basic functionality
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"📍 {title}")
    print(f"{'='*60}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_api():
    """Test main API endpoints"""

    print("\n🧪 Starting API Tests...")
    print("="*60)

    # Test 1: Health Check
    print("\n1️⃣  Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print_response("GET /health", response)

    # Test 2: Register User
    print("\n2️⃣  Testing User Registration...")
    register_data = {
        "name": "Test User",
        "email": f"test_{datetime.now().timestamp()}@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    print_response("POST /api/auth/register", response)

    if response.status_code == 201:
        token = response.json().get('token')
        print(f"\n✅ Registration successful! Token: {token[:20]}...")
    else:
        print("\n❌ Registration failed!")
        return

    # Test 3: Login
    print("\n3️⃣  Testing User Login...")
    login_data = {
        "email": "john@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    print_response("POST /api/auth/login", response)

    if response.status_code == 200:
        token = response.json().get('token')
        user = response.json().get('user')
        print(f"\n✅ Login successful! User: {user['name']}")
    else:
        print("\n❌ Login failed! Using registration token...")

    # Headers with authentication
    headers = {"Authorization": f"Bearer {token}"}

    # Test 4: Get Current User
    print("\n4️⃣  Testing Get Current User...")
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    print_response("GET /api/auth/me", response)

    # Test 5: Get All Products
    print("\n5️⃣  Testing Get All Products...")
    response = requests.get(f"{BASE_URL}/api/products")
    print_response("GET /api/products", response)

    if response.status_code == 200:
        products = response.json().get('products', [])
        if products:
            product_id = products[0]['_id']
            print(f"\n✅ Found {len(products)} products")
        else:
            print("\n⚠️  No products found. Please run seed_data.py")
            return
    else:
        print("\n❌ Failed to get products!")
        return

    # Test 6: Get Single Product
    print("\n6️⃣  Testing Get Single Product...")
    response = requests.get(f"{BASE_URL}/api/products/{product_id}")
    print_response(f"GET /api/products/{product_id}", response)

    # Test 7: Get Cart
    print("\n7️⃣  Testing Get User Cart...")
    response = requests.get(f"{BASE_URL}/api/cart", headers=headers)
    print_response("GET /api/cart", response)

    # Test 8: Add to Cart
    print("\n8️⃣  Testing Add to Cart...")
    cart_data = {
        "productId": product_id,
        "quantity": 2
    }
    response = requests.post(f"{BASE_URL}/api/cart/add", json=cart_data, headers=headers)
    print_response("POST /api/cart/add", response)

    # Test 9: Get Leaderboard
    print("\n9️⃣  Testing Get Leaderboard...")
    response = requests.get(f"{BASE_URL}/api/leaderboard")
    print_response("GET /api/leaderboard", response)

    # Test 10: Get Sales Analytics
    print("\n🔟 Testing Get Sales Analytics...")
    response = requests.get(f"{BASE_URL}/api/analytics/sales")
    print_response("GET /api/analytics/sales", response)

    # Summary
    print("\n" + "="*60)
    print("🎉 API Tests Complete!")
    print("="*60)
    print("""
✅ If all tests passed, your API is working correctly!

🔧 Next steps:
1. Test the checkout flow by creating an order
2. Connect your frontend application
3. Test Socket.IO real-time updates
4. Customize the products and configurations

📚 See README.md for complete API documentation
    """)

if __name__ == '__main__':
    try:
        print("""
╔═══════════════════════════════════════════════════════╗
║           🧪 Flash Sale API Test Suite               ║
║                                                       ║
║  Make sure the server is running on localhost:5000   ║
║  Run: python server.py                               ║
╚═══════════════════════════════════════════════════════╝
        """)

        # Check if server is running
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is running!\n")
                test_api()
            else:
                print("❌ Server responded with error. Please check the server.")
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server. Please start the server first:")
            print("   python server.py\n")
        except requests.exceptions.Timeout:
            print("❌ Server connection timeout. Please check if server is running.\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
