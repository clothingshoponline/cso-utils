# cso-utils v5.0.2

This package contains wrappers for commonly used API calls from the S&S Activewear, Github, ChannelAdvisor, and Zendesk APIs.

## Requirements

- Python <= 3.9.6
- requests <= 2.25.1
- PyGithub <= 1.55
- pytest <= 6.2.4

## Installation

```
pip install git+https://github.com/clothingshoponline/cso-utils.git@v5.0.2
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

#### Get Products

_Returns a dictionary where the keys are skus and the values are_ `Product` _objects._

```
products = ss_api.get_products()
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

### CSO Database

#### Import

```
from cso_utils import csodb
```

#### Start Database Connection
##### If using Linux OR using Windows on default port 40000
This will work in most cases
```
cursor = csodb.connection()
```
##### If using Windows and you need to specify a port other than 40000
Defaults to port 40000 if run on Windows. No port required for Linux.
Alternative port can be specified by using the "windows_port" argument (int)
```
cursor = csodb.connection()(windows_port=3306)
```

#### Execute Query
```
cursor.execute(
    f"""
    SELECT invoiceNumber,
        customerNumber,
        orderDate,
        invoiceDate
    FROM AllShipments
    WHERE invoiceDate > '2021-09-20'
    """
)
```

#### Get Query Results
```
cursor.fetchall()
```
