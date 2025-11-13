"""
Complete Checkout Flow Test with Debugging
Tests: Login -> Add to Cart -> View Cart -> Checkout
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_response(response):
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        return data
    except:
        print(f"Response: {response.text}")
        return None

def test_checkout_flow():
    print_section("COMPLETE CHECKOUT FLOW TEST")

    # Step 1: Login
    print_section("Step 1: Login")
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "john@example.com",
        "password": "password123"
    })

    if not login_response.ok:
        print(f"❌ Login failed")
        print_response(login_response)
        return

    login_data = login_response.json()
    token = login_data.get('token')
    user = login_data.get('user', {})
    print(f"✅ Logged in as: {user.get('name')}")
    print(f"   User ID: {user.get('id')}")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Step 2: Get products
    print_section("Step 2: Fetch Products")
    products_response = requests.get(f"{BASE_URL}/api/products")

    if not products_response.ok:
        print(f"❌ Failed to fetch products")
        return

    products = products_response.json().get('products', [])
    print(f"✅ Found {len(products)} products")

    if len(products) < 1:
        print("❌ Need at least 1 product for testing")
        return

    product = products[0]
    print(f"   Test Product: {product['name']}")
    print(f"   Price: ${product['price']}")
    print(f"   Stock: {product['stock']}")
    print(f"   Product ID: {product['_id']}")

    # Step 3: Clear cart first
    print_section("Step 3: Clear Cart (if exists)")
    clear_response = requests.delete(f"{BASE_URL}/api/cart/clear", headers=headers)
    print_response(clear_response)

    # Step 4: View empty cart
    print_section("Step 4: View Empty Cart")
    cart_response = requests.get(f"{BASE_URL}/api/cart", headers=headers)
    cart_data = print_response(cart_response)

    if cart_response.ok:
        items = cart_data.get('cart', {}).get('items', [])
        print(f"✅ Cart has {len(items)} items")

    # Step 5: Add product to cart
    print_section("Step 5: Add Product to Cart")
    add_payload = {
        "productId": product['_id'],
        "quantity": 2
    }
    print(f"Sending payload: {json.dumps(add_payload, indent=2)}")

    add_response = requests.post(
        f"{BASE_URL}/api/cart/add",
        json=add_payload,
        headers=headers
    )

    add_data = print_response(add_response)

    if add_response.ok:
        print(f"✅ Added {product['name']} x2 to cart")
        cart_data = add_data.get('cart', {})
        print(f"   Cart Total: ${cart_data.get('total', 0)}")
    else:
        print(f"❌ Failed to add to cart")
        return

    # Step 6: View cart with items
    print_section("Step 6: View Cart with Items")
    cart_response = requests.get(f"{BASE_URL}/api/cart", headers=headers)
    cart_data = print_response(cart_response)

    if cart_response.ok:
        cart = cart_data.get('cart', {})
        items = cart.get('items', [])
        print(f"✅ Cart has {len(items)} items:")
        for item in items:
            product_info = item.get('product', {})
            print(f"   - {product_info.get('name')}: {item.get('quantity')} x ${item.get('price')}")
        print(f"   Total: ${cart.get('total', 0):.2f}")

        if len(items) == 0:
            print("❌ Cart is empty - cannot proceed with checkout")
            return
    else:
        print(f"❌ Failed to fetch cart")
        return

    # Step 7: Attempt checkout
    print_section("Step 7: Checkout")

    # Record checkout start time
    checkout_start = datetime.utcnow().isoformat() + 'Z'
    print(f"Checkout start time: {checkout_start}")

    checkout_payload = {
        "checkoutStartTime": checkout_start,
        "paymentMethod": "card"
    }
    print(f"Sending payload: {json.dumps(checkout_payload, indent=2)}")

    checkout_response = requests.post(
        f"{BASE_URL}/api/orders",
        json=checkout_payload,
        headers=headers
    )

    checkout_data = print_response(checkout_response)

    if checkout_response.ok:
        order = checkout_data.get('order', {})
        print(f"✅ ORDER SUCCESSFUL!")
        print(f"   Order ID: {order.get('orderId')}")
        print(f"   Total: ${order.get('total')}")
        print(f"   Checkout Time: {order.get('checkoutTime')}s")
        print(f"   Items: {len(order.get('items', []))}")

        # Verify cart is empty
        print_section("Step 8: Verify Cart is Empty")
        cart_response = requests.get(f"{BASE_URL}/api/cart", headers=headers)
        cart_data = print_response(cart_response)

        if cart_response.ok:
            items = cart_data.get('cart', {}).get('items', [])
            if len(items) == 0:
                print("✅ Cart is empty after checkout")
            else:
                print(f"⚠️  Cart still has {len(items)} items")
    else:
        print(f"❌ CHECKOUT FAILED")
        error = checkout_data.get('error') if checkout_data else 'Unknown error'
        message = checkout_data.get('message') if checkout_data else ''
        details = checkout_data.get('details') if checkout_data else []

        print(f"   Error: {error}")
        if message:
            print(f"   Message: {message}")
        if details:
            print(f"   Details:")
            for detail in details:
                print(f"     - {detail}")

    print_section("TEST COMPLETE")

if __name__ == '__main__':
    try:
        # Check if server is running
        health = requests.get(f"{BASE_URL}/health", timeout=2)
        if health.ok:
            print("✅ Server is running")
            test_checkout_flow()
        else:
            print("❌ Server not healthy")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server!")
        print("Start server with: python backend/server.py")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
