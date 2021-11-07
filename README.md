# cso-utils v5.2.0

This package contains wrappers for commonly used API calls from the S&S Activewear, Github, ChannelAdvisor, and Zendesk APIs.

## Requirements

- Python <= 3.9.6
- requests <= 2.25.1
- PyGithub <= 1.55
- pytest <= 6.2.4
- PyMySQL <= 1.0.2
- beautifulsoup4 <= 4.10.0

## Installation

```
pip install git+https://github.com/clothingshoponline/cso-utils.git@v5.2.0
```

## Usage

### S&S Activewear

#### Import

```
from cso_utils import ssactivewear
```

#### Connect to S&S Activewear API

```
ss_api = ssactivewear.SSActivewear('<account>', '<password>')
```

#### Get Order

_Returns an_ `Order` _object._

```
order = ss_api.get_order('<po number>')
```

#### Order

##### Print

```
print(order)
```

##### Get Order Data

```
data = order.data()
```

##### Get PO Number

```
po_number = order.po_number()
```

##### Get Lines

```
lines = order.lines()
```

##### Get Tracking Numbers

```
tracking = order.tracking_nums()
```

##### Get Order Numbers

```
order_nums = order.order_nums()
```

##### Get Invoices

```
invoices = order.invoices()
```

##### Get GUIDs

```
guids = order.guids()
```

#### Get Invoice

_Returns an_ `Order` _object._

```
invoice = ss_api.get_invoice('<invoice>')
```

#### Full Return

_Returns a_ `ReturnRequest` _object._
```
po_number = '123'
reason_code = 1 # reason codes defined at https://api.ssactivewear.com/V2/Returns_Post.aspx
reason_comment = 'do not want'
test = True

# optional
return_warehouses = ['NV', 'TX'] 
force_restock = True

return_request = ss_api.full_return(po_number, 
                                    reason_code, 
                                    reason_comment, 
                                    test, 
                                    return_warehouses, 
                                    force_restock)
```
#### Invoice Return

_Variables for a full return apply. Returns a_ `ReturnRequest` _object._

```
invoice = '123'

return_request = ss_api.invoice_return(invoice, 
                                       reason_code, 
                                       reason_comment, 
                                       test, 
                                       return_warehouses, 
                                       force_restock)
```

#### Partial Return

_Variables for a full return apply. Returns a_ `ReturnRequest` _object._

```
skus_and_qtys = {'B1': 1, 'B2': 2}

return_request = ss_api.partial_return(po_number, 
                                       skus_and_qtys, 
                                       reason_code, 
                                       reason_comment, 
                                       test, 
                                       return_warehouses, 
                                       force_restock)
```

#### ReturnRequest

##### Print

```
print(return_request)
```

##### Get Data

```
data = return_request.data()
```

##### Get Return Instructions

```
ra, address = return_request.instructions()
```

#### Track Using Tracking Numbers

_Returns a_ `Tracking` _object._

```
tracking = ss_api.track_using_tracking(['1', '2'])
```

#### Track Using Order Numbers

_Returns a_ `Tracking` _object._

```
tracking = ss_api.track_using_order_nums(['1', '2'])
```

#### Track Using Invoices

_Returns a_ `Tracking` _object._

```
tracking = ss_api.track_using_invoices(['1', '2'])
```

#### Track Using Actual Delivery Dates

_Returns a_ `Tracking` _object._

```
import datetime

# May 3, 2021
date1 = datetime.datetime(2021, 5, 3)
# October 12, 2021
date2 = datetime.datetime(2021, 10, 12) 

tracking = ss_api.track_using_actual_delivery_dates([date1, date2])
```

#### Tracking

##### Print

```
print(tracking)
```

##### Get Tracking Data

```
data = tracking.data()
```

##### Get Tracking Numbers and Status

```
status = tracking.num_and_status()
```

#### Get Product

_Returns a_ `Product` _object._

```
product = ss_api.get_product('<sku>')
```

#### Get Products

_Returns a dictionary where the keys are skus and the values are_ `Product` _objects._

```
products = ss_api.get_products()
```

#### Get Products with a Specified Style ID

_Returns a list of_ `Product` _objects._

```
style_id = 1

products = ss_api.get_products_with_style_id(style_id)
```

#### Product

##### Print

```
print(product)
```

##### Get Product Data

```
data = product.data()
```

##### Get Sku

```
sku = product.sku()
```

##### Get Brand Name

```
brand_name = product.brand_name()
```

##### Get Style Name

```
style_name = product.style_name()
```

##### Get Piece Price

```
piece_price = product.piece_price()
```

##### Get Case Price

```
case_price = product.case_price()
```

##### Get Sale Price

```
sale_price = product.sale_price()
```

#### Get Style

_Returns a_ `Style` _object._

```
style_id = 1

style = ss_api.get_style(style_id)
```

#### Get Styles

_Returns a dictionary where the keys are style IDs and the values are_ `Style` _objects._

```
styles = ss_api.get_styles()
```

#### Style

##### Get Title

```
title = style.title()
```

##### Get Base Category

```
base_category = style.base_category()
```

##### Get Description

```
description = style.description()
```


### Github

#### Import

```
from cso_utils import github_api
```

#### Create Bug Report

_Creates a Github Issue with the traceback. Bad requests that cause a_ `requests.exceptions.HTTPError` _exception will include the traceback and response sent back._

```
try:
    ... # code that raises an exception
except:
    github_api.create_bug_report('<token>', '<repo name>')
```


### Zendesk

#### Import

```
from cso_utils import zendesk
```

#### Connect to Zendesk API

```
zen_api = zendesk.Zendesk('<subdomain>', '<email>', '<token>')
```

#### Get Ticket

_Returns a_ `Ticket` _object._

```
ticket = zen_api.get_ticket('<id number>')
```

#### Ticket

##### Print

```
print(ticket)
```

##### Get Ticket Data

```
data = ticket.data()
```

##### Get ID Number

```
id_number = ticket.id_num()
```

##### Get Subject

```
subject = ticket.subject()
```

##### Get Custom Fields

```
custom_fields = ticket.custom_fields()
```

##### Check That Ticket Has Given Tag

```
ticket.has_tag('<tag>')
```

##### Check That Ticket Has Given Text

_Only checks subject and first comment._

```
ticket.has_text('<text>')
```

##### Check That Ticket Has Given Status

```
ticket.has_status('<status>')
```

##### Check That Ticket is in Given Group

```
ticket.in_group('<group id>')
```

##### Check That Ticket Sent From Given Email

```
ticket.sent_from('<email>')
```

#### Create Ticket and Send Message to Customer

_Option 1:_

```
customer_name = 'first last'
customer_email = 'someone@example.com'
subject = 'Hello'
message = 'Welcome!'  # Use html for formatting

# optional
group_id = '123'
tag = 'tag1'
assignee = 'assignee@company.com'
support_email = 'support@company.com'

ticket_id = zen_api.create_ticket_and_send_to_customer(customer_name,
                                                       customer_email, 
                                                       subject, 
                                                       message,
                                                       group_id,
                                                       tag,
                                                       assignee,
                                                       support_email)
```

_Option 2:_

```
ticket_id = zen_api.create_ticket(customer_name,
                                  customer_email,
                                  subject,
                                  message,
                                  assignee,
                                  support_email)

ticket_id = zen_api.send_to_customer(ticket_id, 
                                     message,
                                     group_id,
                                     tag)
```

#### Reply to Existing Ticket

_Option 1:_

```
ticket_id = '123'
message = 'Hello!'  # Use html for formatting

# optional
group_id = '123'
tag = 'tag1'

ticket_id = zen_api.send_to_customer(ticket_id, 
                                     message,
                                     group_id,
                                     tag)
```

_Option 2:_

```
# optional
status = 'open'  # defaults as 'solved'
public = False  # defaults as True

ticket_id = zen_api.reply_to(ticket_id, 
                             message, 
                             group_id, 
                             tag, 
                             status, 
                             public)
```

#### Get Tickets Created Between Today and Given Date

_Returns a list of_ `Ticket` _objects._

```
# December 1, 2020
tickets = zen_api.tickets_created_between_today_and(12, 1, 2020)
```


### ChannelAdvisor

#### Import

```
from cso_utils import channeladvisor
```

#### Connect to ChannelAdvisor API

```
ca_api = channeladvisor.ChannelAdvisor('<token>')
```

#### Get Order

_Returns a_ `ChannelAdvisorOrder` _object._

```
ca_order = ca_api.get_order('<site order id or po number>')
```

#### ChannelAdvisorOrder

##### Print

```
print(ca_order)
```

##### Get Order Data

```
data = ca_order.data()
```

##### Get PO Number

```
po_number = ca_order.po_number()
```

##### Get Site Name

```
site_name = ca_order.site_name()
```

##### Get Site Order ID

```
site_order_id = ca_order.site_order_id()
```

##### Get Lines

```
lines = ca_order.lines()
```

##### Get Creation Date and Time

```
creation_date = ca_order.creation_datetime()
```

##### Get Shipping Status

```
shipping_status = ca_order.shipping_status()
```

#### Get Orders Shipped on Given Date

_Returns a list of_ `ChannelAdvisorOrder` _objects._

```
# September 1, 2021
ca_orders = ca_api.get_orders_shipped_on(9, 1, 2021)
```

### SQL Database Connector

#### Import

```
from cso_utils import database
```

#### Start Database Connection
- username (str): Database Username
- password (str): Database Password
- db_name (str): Database Name
- port_or_socket (str): Port number if running on Windows ("40000" usually works) or Socket name if running on Linux
```
connection = database.Database(username, password, db_name, port_or_socket)
```

#### Execute Query and Get Query Results
```
connection.cursor.execute(
    f"""
    SELECT invoiceNumber,
        customerNumber,
        orderDate,
        invoiceDate
    FROM AllShipments
    WHERE invoiceDate > '2021-09-20'
    """
)

connection.cursor.fetchall()
```

#### Get List of Database Table Names
```
connection.get_table_names()
```
#### Get Database Table Column Schema
```
connection.get_table_schema()
```

### Tracking
Can be used to track UPS or USPS shipments. Has the option of returning standardized tracking data (at the expense of less tracking details).

Note: Because the USPS API supprots batch processing, the library will automatically create batches of 10 tracking numnbers. Both UPS and USPS shipments will be tracked asyncronously for maximum performance.

**The tracking responses may not be returened in the same order they were requested.**

#### Import
```
from cso_utils import tracking
```

#### Tracking

- usps_username (str): [USPS Web Tools User ID](https://www.usps.com/business/web-tools-apis/)
- ups_username (str): UPS Account Username
- ups_password (str): UPS Account Password
- ups_license (str): [UPS Account API License Key](https://www.ups.com/upsdeveloperkit?loc=en_US)
```
tracker = tracking.Tracking(USPS_API_USERNAME, UPS_USERNAME, UPS_PASSWORD, UPS_LICENSE)
```
##### Track USPS Shipments 
Note: Set "simplify=False" if you want the full USPS response.
```
tracking_list = [
    "9405511898524886244010", "9405511898524886360512", "9405511898524886602995"
    ]
tracking_responses = tracker.track_usps(tracking_list, simplify=True)
```
##### Track UPS Shipments
Note: Set "simplify=False" if you want the full UPS response.
```
tracking_list = [
    "1Z2R29910236894608", "1Z2R2991YN36493852", "1Z2R2991YN36495887", "1Z2R2991YN36555893"
    ]
tracking_responses = tracker.track_ups(tracking_list, simplify=True)
```