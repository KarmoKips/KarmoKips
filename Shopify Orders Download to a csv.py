#________________________________________________________________
#                   --- Import the libraries ---
#----------------------------------------------------------------

import shopify
import pytz
from datetime import datetime, timedelta
import pandas as pd

#________________________________________________________________

#________________________________________________________________
#                   --- Login to Shopify---
#----------------------------------------------------------------
shop_url = 'your-shop-url.myshopify.com'
api_version = 'api version'
private_app_password = 'your api password'
#________________________________________________________________

#________________________________________________________________
#                   --- get time & format it ---
#----------------------------------------------------------------
def get_time():
    get_today_date=datetime.now(pytz.timezone('Europe/London'))
    get_yetserday_date = get_today_date - timedelta(days= 8)
    format_yesterday_date=datetime.strftime(get_yetserday_date,'%Y-%m-%dT%H:%M:%S%z')
    yesterday=format_yesterday_date
    return yesterday

start_date = get_time()
def get_time_changed_at():
    get_today_date=datetime.now(pytz.timezone('Europe/London'))
    get_yetserday_date = get_today_date - timedelta(hours= 10)
    format_yesterday_date=datetime.strftime(get_yetserday_date,'%Y-%m-%dT%H:%M:%S%z')
    hours=format_yesterday_date
    return hours

changed_at = get_time_changed_at()


#________________________________________________________________
#                   --- Create Shopify Session: ---
#----------------------------------------------------------------

session = shopify.Session(shop_url, api_version, private_app_password)
shopify.ShopifyResource.activate_session(session)

#________________________________________________________________________________________________________________________________
#                   --- Create function to iterate through Orders with pagination: ---
#--------------------------------------------------------------------------------------------------------------------------------
 
def iter_all_orders(status='unshipped', limit=250, financial_status='paid'): 
    orders = shopify.Order.find(since_id=0,status=status, limit=limit, created_at_min = start_date,financial_status=financial_status,updated_at_min = changed_at)    
#yield orders & pagination:
    for order in orders:
        yield order
    
    while orders.has_next_page():
        orders = orders.next_page()
        for order in orders:
            yield order
#Create an empty list for pandas.
order_list=[]

#define values for Shopify Orders

for order in iter_all_orders(): 
            line_items = order.line_items
            
            for i in range(len(line_items)):        #to retreive all line_items row by row set line_items to be in a list.
                line_item = line_items[i]
                sku = line_item.sku
                quantity = line_item.quantity
                name = order.name
                id = order.checkout_id
                order_number = order.order_number
                number = order.number
                email = order.email
                phone = order.shipping_address.phone
                company = order.shipping_address.company
                customer_name=order.shipping_address.name
                address1=order.shipping_address.address1
                address2=order.shipping_address.address2
                city=order.shipping_address.city
                province=order.shipping_address.province
                zip = order.shipping_address.zip
                country=order.shipping_address.province
                country_code=order.shipping_address.country_code
                code = 0
                for shipping_lines in order.shipping_lines:
                    code = shipping_lines.code
                    if code == 'flat-rate-1':
                        Shipping_Service_Code = 1
                    elif code == 'flat-rate':
                        Shipping_Service_Code = 2
                    elif code == 'custom':
                        Shipping_Service_Code = 2
                    elif code:
                        Shipping_Service_Code = 2

                created_at = order.created_at
                DeliveryMethod = 'DPD Standard'
                AccountCode = 'account code if needed'

                #________________Convert Dates for created_at & shipped_date________________________________________________________________________________________________

                format_date = datetime.strptime(created_at,'%Y-%m-%dT%H:%M:%S%z')
                formatted_date = datetime.strftime(format_date,'%m/%d/%Y')
                parsed_date=datetime.strptime(formatted_date,'%m/%d/%Y') 
                required_date=parsed_date+timedelta(days=1)
                format_parsed_date=datetime.strftime(required_date,'%d/%m/%Y')

                #_____________________________________________________________________________________________________________________________

        
                #set pandas header values and what they should contain

                data = {
                    'External reference':order_number, #name
                    'StatementCustomer':'',
                    'CustomerOrderNumber':name,#order_number
                    'ShipTo':customer_name,
                    'ShippingNumber':phone,
                    'ContactEmail':email,
                    'DateRequired':format_parsed_date,
                    'DeliveryMethod':DeliveryMethod,
                    'Shipping service code':Shipping_Service_Code,
                    'CustomerCompany':company,
                    'AddressLine1':address1,
                    'AddressLine2':address2,
                    'Town/City':city,
                    'County':country,
                    'PostCode':zip,
                    'Shipping Country code':country_code,
                    'OrderQuantity':quantity,
                    'ProductCode':sku,
                    'Account Code':AccountCode
                        }
                order_list.append(data) #append all data



#end shopify session          
shopify.ShopifyResource.clear_session()


#set time or filename & save to csv file

cur_time = datetime.now(pytz.timezone('Europe/London')).strftime('%Y%m%d%H%M%S')
filename='your file name'+cur_time +'.01.csv'


#-------------------------------------------------------------------------------------------
#Save to csv

df = pd.DataFrame(order_list)
df.to_csv(filename,index=False)
print('saved to file.')


