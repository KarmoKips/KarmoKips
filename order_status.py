import requests
import json

SHOP_DOMAIN = 'your shop name'
API_KEY = 'your api key'
API_PASSWORD = 'your api password'
API_VERSION = '2023-01'  # Replace with your desired API version

# Prepare the endpoint URL to retrieve orders
orders_endpoint = f"https://{SHOP_DOMAIN}/admin/api/2021-07/orders.json"

# Prepare the request parameters for pagination
params = {
    "limit": 250,  # Number of orders per page
    "status": "any",  # Fetch orders with any status
    "fulfillment_status": "unfulfilled"  # Fetch only unfulfilled orders
}

order_ids = []

# Retrieve all orders using pagination
while True:
    # Make the API request to retrieve orders
    orders_response = requests.get(
        orders_endpoint,
        auth=(API_KEY, API_PASSWORD),
        headers={"Content-Type": "application/json"},
        params=params
    )

    # Check the response and extract order IDs
    if orders_response.status_code == 200:
        orders_data = orders_response.json()
        orders = orders_data['orders']
        order_ids.extend([order['id'] for order in orders])

        # Check if there are more pages
        if 'next_page_info' in orders_data:
            params['page_info'] = orders_data['next_page_info']
        else:
            break  # Exit the loop if no more pages
    else:
        print(f"Failed to retrieve orders. Error: {orders_response.text}")
        exit()

print(f"Total unfulfilled orders found: {len(order_ids)}")

# Prepare the fulfillment payload
fulfillment_data = {
    "fulfillment": {
        "location_id": "19630817376",  # Replace with your location ID
        "tracking_number": "ABC123",  # Replace with the tracking number
        "tracking_urls": ["https://example.com/tracking"],  # Replace with the tracking URL
        "notify_customer": False  # Do not notify the customer
    }
}

# Loop through each order and fulfill it
for order_id in order_ids:
    # Prepare the endpoint URL for each order
    endpoint = f"https://{SHOP_DOMAIN}/admin/api/2021-07/orders/{order_id}/fulfillments.json"

    # Make the API request to fulfill the order
    response = requests.post(
        endpoint,
        auth=(API_KEY, API_PASSWORD),
        headers={"Content-Type": "application/json"},
        data=json.dumps(fulfillment_data)
    )

    # Check the response for each order
    if response.status_code == 201:
        print(f"Order {order_id} fulfilled successfully!")
    else:
        print(f"Failed to fulfill order {order_id}. Error: {response.text}")