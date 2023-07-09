import requests
import pyodbc
import shopify
import time

server = 'server-ip-address'
database = 'your database'
username = 'username'
password = 'password'
schema = 'schema, if needed'

#store credentials
SHOP_URL = 'shopname.myshopify.com'
API_VERSION = 'api-version'
PRIVATE_APP_PASSWORD = 'api password'
LOCATION_ID = 'fulfillment location'

# Establish a connection to SQL Server
try:
    conn_string = 'DRIVER={SQL Server};SERVER=' + server + ';DATABASE=' + database + ';UID=' + username + ';PWD=' + password
    conn = pyodbc.connect(conn_string)
    cursor = conn.cursor()
    print('Connected to SQL Server')
except pyodbc.Error as e:
    print('Error connecting to SQL Server:', e)
    exit()

# Activate the Shopify session
try:
    session = shopify.Session(SHOP_URL, API_VERSION, PRIVATE_APP_PASSWORD)
    shopify.ShopifyResource.activate_session(session)
    print('Shopify session activated')
except Exception as e:
    print('Error activating Shopify session:', e)
    exit()

# Fetch products from Shopify using since_id parameter
since_id = 0
while True:
    products = shopify.Product.find(since_id=since_id)
    if not products:
        # No more products, exit the loop
        break

    for product in products:
        for variant in product.variants:
            sku = variant.sku
            print("Found SKU in Shopify:", sku)

            # Fetch the inventory level for the SKU from SQL Server from the required fulfillment locations
            query = """
                    SELECT YOUR_SQL_SKU_COLUMN AS SKU, YOUR_SQL_SKU_INVENTORY_LEVEL AS Stock, YOUR_SQL_STATUS_COLUMN AS Status
                    FROM {}.YOUR_SQL_STATUS_TABLE AS MVT
                    JOIN {}.YOUR_SQL_SKU_TABLE AS ITM ON MVT.YOUR_SQL_STATUS_TABLE = YOUR_SQL_SKU_COLUMN
                    WHERE MVT.YOUR_SQL_COLUMN_LOCATION = 'your location' AND YOUR_SQL_SKU_COLUMN = '{}'
                    """.format(schema, schema, sku)

            try:
                # Execute the SQL query
                cursor.execute(query)

                # Fetch the row of the result
                stock_data = cursor.fetchone()

                # Process the retrieved stock data for the SKU
                if stock_data:
                    sql_sku, stock, status = stock_data
                    if status == 1:
                        stock -= 10
                        stock = max(stock, 0)  # Ensure stock value doesn't go below 0

                    # Convert the stock value to an integer
                    stock = int(stock)

                    # Update the inventory levels for the variant in Shopify
                    inventory_item_id = variant.inventory_item_id
                    endpoint = f"https://{SHOP_URL}/admin/api/{API_VERSION}/inventory_levels/set.json"
                    payload = {
                        "location_id": LOCATION_ID,
                        "inventory_item_id": inventory_item_id,
                        "available": stock
                    }
                    headers = {
                        "Content-Type": "application/json",
                        "X-Shopify-Access-Token": PRIVATE_APP_PASSWORD
                    }
                    response = requests.post(endpoint, json=payload, headers=headers)

                    if response.status_code == 200:
                        print("Updated inventory for SKU {} in Shopify to: {}".format(sku, stock))
                    else:
                        print("Error updating inventory for SKU {} in Shopify: {}".format(sku, response.text))
            except pyodbc.Error as e:
                print('Error executing SQL query:', e)

        # Update the since_id to the last fetched product's ID
        since_id = product.id

        time.sleep(0.5)  # Pause for 0.5 seconds between requests

# Deactivate the Shopify session
shopify.ShopifyResource.clear_session()
print('Shopify session deactivated')

# Close the SQL Server connection
cursor.close()
conn.close()
print('Connection to SQL Server closed')
