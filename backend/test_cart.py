"""
Complete Cart Functionality Test
Tests: Add to Cart -> View Cart -> Update Quantity -> Remove Item
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_full_cart_flow():
    print("\n" + "="*70)
    print("COMPLETE CART FLOW TEST")
    print("="*70)

    # Step 1: Login
    print("\n📝 Step 1: Login")
    login_response = requests.post(f"{BASE_URL}/api/auth/login", json={
        "email": "john@example.com",
        "password": "password123"
    })
    
    if not login_response.ok:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    login_data = login_response.json()
    token = login_data.get('token')
    user = login_data.get('user', {})
    print(f"✅ Logged in as: {user.get('name')}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Step 2: Get products
    print("\n📦 Step 2: Fetch Products")
    products_response = requests.get(f"{BASE_URL}/api/products")
    
    if not products_response.ok:
        print(f"❌ Failed to fetch products")
        return
    
    products = products_response.json().get('products', [])
    print(f"✅ Found {len(products)} products")
    
    if len(products) < 2:
        print("❌ Need at least 2 products for testing")
        return
    
    product1 = products[0]
    product2 = products[1]
    print(f"   Test Product 1: {product1['name']} (${product1['price']})")
    print(f"   Test Product 2: {product2['name']} (${product2['price']})")

    # Step 3: View empty cart
    print("\n🛒 Step 3: View Initial Cart")
    cart_response = requests.get(f"{BASE_URL}/api/cart", headers=headers)
    print(f"   Status: {cart_response.status_code}")
    
    if cart_response.ok:
        cart_data = cart_response.json()
        print(f"✅ Cart retrieved: {len(cart_data.get('cart', {}).get('items', []))} items")
    else:
        print(f"❌ Failed to view cart: {cart_response.status_code}")
        print(f"   Response: {cart_response.text}")

    # Step 4: Add first product
    print(f"\n➕ Step 4: Add Product 1 to Cart")
    add_response1 = requests.post(
        f"{BASE_URL}/api/cart/add",
        json={"productId": product1['_id'], "quantity": 2},
        headers=headers
    )
    
    if add_response1.ok:
        print(f"✅ Added {product1['name']} x2")
        cart_data = add_response1.json().get('cart', {})
        print(f"   Cart Total: ${cart_data.get('total', 0)}")
    else:
        print(f"❌ Failed to add product 1: {add_response1.status_code}")
        print(f"   Response: {add_response1.text}")

    # Step 5: Add second product
    print(f"\n➕ Step 5: Add Product 2 to Cart")
    add_response2 = requests.post(
        f"{BASE_URL}/api/cart/add",
        json={"productId": product2['_id'], "quantity": 1},
        headers=headers
    )
    
    if add_response2.ok:
        print(f"✅ Added {product2['name']} x1")
        cart_data = add_response2.json().get('cart', {})
        print(f"   Cart Total: ${cart_data.get('total', 0)}")
    else:
        print(f"❌ Failed to add product 2: {add_response2.status_code}")

    # Step 6: View full cart
    print("\n🛒 Step 6: View Full Cart")
    cart_response = requests.get(f"{BASE_URL}/api/cart", headers=headers)
    
    if cart_response.ok:
        cart_data = cart_response.json().get('cart', {})
        items = cart_data.get('items', [])
        print(f"✅ Cart has {len(items)} items:")
        for item in items:
            product = item.get('product', {})
            print(f"   - {product.get('name')}: {item.get('quantity')} x ${item.get('price')} = ${item.get('quantity') * item.get('price')}")
        print(f"   Total: ${cart_data.get('total', 0):.2f}")
    else:
        print(f"❌ Failed to view cart: {cart_response.status_code}")
        print(f"   Response: {cart_response.text}")
        return

    # Step 7: Update quantity
    print(f"\n✏️  Step 7: Update Product 1 Quantity")
    update_response = requests.put(
        f"{BASE_URL}/api/cart/item/{product1['_id']}",
        json={"quantity": 3},
        headers=headers
    )
    
    if update_response.ok:
        print(f"✅ Updated quantity to 3")
        cart_data = update_response.json().get('cart', {})
        print(f"   New Total: ${cart_data.get('total', 0):.2f}")
    else:
        print(f"❌ Failed to update quantity: {update_response.status_code}")

    # Step 8: Remove item
    print(f"\n🗑️  Step 8: Remove Product 2 from Cart")
    remove_response = requests.delete(
        f"{BASE_URL}/api/cart/item/{product2['_id']}",
        headers=headers
    )
    
    if remove_response.ok:
        print(f"✅ Removed {product2['name']}")
        cart_data = remove_response.json().get('cart', {})
        print(f"   Remaining items: {len(cart_data.get('items', []))}")
        print(f"   New Total: ${cart_data.get('total', 0):.2f}")
    else:
        print(f"❌ Failed to remove item: {remove_response.status_code}")

    # Step 9: Final cart view
    print("\n🛒 Step 9: Final Cart View")
    cart_response = requests.get(f"{BASE_URL}/api/cart", headers=headers)
    
    if cart_response.ok:
        cart_data = cart_response.json().get('cart', {})
        items = cart_data.get('items', [])
        print(f"✅ Final cart:")
        for item in items:
            product = item.get('product', {})
            print(f"   - {product.get('name')}: {item.get('quantity')} x ${item.get('price')}")
        print(f"   Total: ${cart_data.get('total', 0):.2f}")
    else:
        print(f"❌ Failed to view final cart: {cart_response.status_code}")

    print("\n" + "="*70)
    print("✨ TEST COMPLETE!")
    print("="*70)

if __name__ == '__main__':
    try:
        # Check if server is running
        health = requests.get(f"{BASE_URL}/health", timeout=2)
        if health.ok:
            test_full_cart_flow()
        else:
            print("❌ Server not healthy")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server!")
        print("Start server with: python backend/server.py")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
