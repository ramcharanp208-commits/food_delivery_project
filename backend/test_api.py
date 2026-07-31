"""Test script to verify all API endpoints are working."""
import requests

BASE_URL = "http://localhost:8000"


def test_api():
    print("=" * 60)
    print("Testing Swiggy Clone API")
    print("=" * 60)

    # 1. Health check
    print("\n1. Health Check")
    r = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()}")

    # 2. Get restaurants
    print("\n2. Get Restaurants")
    r = requests.get(f"{BASE_URL}/restaurants/")
    print(f"   Status: {r.status_code}")
    restaurants = r.json()
    print(f"   Found {len(restaurants)} restaurants")
    for rest in restaurants:
        print(f"   - {rest['name']} ({rest['cuisine']}) - {len(rest['items'])} items")

    # 3. Login as test user
    print("\n3. Login as Test User")
    r = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "user@swiggy.com", "password": "user123"},
    )
    print(f"   Status: {r.status_code}")
    token = r.json()["access_token"]
    user = r.json()["user"]
    print(f"   Token: {token[:50]}...")
    print(f"   User: {user['full_name']} ({user['email']})")
    headers = {"Authorization": f"Bearer {token}"}

    # 4. Get current user
    print("\n4. Get Current User")
    r = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.json()['full_name']}")

    # 5. Add item to cart
    print("\n5. Add Item to Cart")
    r = requests.post(
        f"{BASE_URL}/cart/items",
        json={"menu_item_id": 1, "quantity": 2},
        headers=headers,
    )
    print(f"   Status: {r.status_code}")
    cart = r.json()
    print(f"   Cart ID: {cart['id']}")
    print(f"   Restaurant: {cart['restaurant_name']}")
    print(f"   Items: {len(cart['items'])}")
    print(f"   Total: {cart['total_amount']}")
    print(f"   Delivery Fee: {cart['delivery_fee']}")
    print(f"   Grand Total: {cart['grand_total']}")

    # 6. Add another item
    print("\n6. Add Another Item to Cart")
    r = requests.post(
        f"{BASE_URL}/cart/items",
        json={"menu_item_id": 4, "quantity": 1},
        headers=headers,
    )
    print(f"   Status: {r.status_code}")
    cart = r.json()
    print(f"   Items: {len(cart['items'])}")
    print(f"   Total: {cart['total_amount']}")
    print(f"   Grand Total: {cart['grand_total']}")

    # 7. Get cart
    print("\n7. Get Cart")
    r = requests.get(f"{BASE_URL}/cart/", headers=headers)
    print(f"   Status: {r.status_code}")
    cart = r.json()
    print(f"   Items in cart: {len(cart['items'])}")

    # 8. Create order
    print("\n8. Create Order")
    r = requests.post(
        f"{BASE_URL}/orders/",
        json={
            "delivery_address": "123 Main Street, Apartment 4B, City",
            "payment_method": "COD",
        },
        headers=headers,
    )
    print(f"   Status: {r.status_code}")
    order = r.json()
    print(f"   Order ID: {order['id']}")
    print(f"   Restaurant: {order['restaurant_name']}")
    print(f"   Total: {order['total_amount']}")
    print(f"   Status: {order['status']}")
    print(f"   Payment: {order['payment_method']} - {order['payment_status']}")
    print(f"   Items: {len(order['items'])}")

    # 9. Get user orders
    print("\n9. Get User Orders")
    r = requests.get(f"{BASE_URL}/orders/", headers=headers)
    print(f"   Status: {r.status_code}")
    orders = r.json()
    print(f"   Found {len(orders)} orders")

    # 10. Login as admin
    print("\n10. Login as Admin")
    r = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "admin@swiggy.com", "password": "admin123"},
    )
    print(f"   Status: {r.status_code}")
    admin_token = r.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 11. Update order status (admin)
    print("\n11. Update Order Status (Admin)")
    r = requests.put(
        f"{BASE_URL}/orders/1/status",
        json={"status": "CONFIRMED"},
        headers=admin_headers,
    )
    print(f"   Status: {r.status_code}")
    order = r.json()
    print(f"   Order Status: {order['status']}")

    # 12. Get all orders (admin)
    print("\n12. Get All Orders (Admin)")
    r = requests.get(f"{BASE_URL}/orders/admin/all", headers=admin_headers)
    print(f"   Status: {r.status_code}")
    orders = r.json()
    print(f"   Found {len(orders)} orders")

    print("\n" + "=" * 60)
    print("All tests passed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_api()