# cso-utils v3.5.1

This package contains wrappers for commonly used API calls from the S&S Activewear, Github, ChannelAdvisor, and Zendesk APIs.

## Requirements

- Python <= 3.9.5
- requests <= 2.25.1
- PyGithub <= 1.55
- pytest <= 6.2.4

## Installation

```
pip install git+https://github.com/clothingshoponline/cso-utils.git@v3.5.1
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

##### Get lines

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

```
po_number = '123'
reason_code = 1 # reason codes defined at https://api.ssactivewear.com/V2/Returns_Post.aspx
reason_comment = 'do not want'
test = True
return_warehouses = ['NV', 'TX'] # optional

ra, address = ss_api.full_return(po_number, 
                                 reason_code, 
                                 reason_comment, 
                                 test, 
                                 return_warehouses)
```

#### Partial Return

_Variables for a full return apply._

```
skus_and_qtys = {'B1': 1, 'B2': 2}

ra, address = ss_api.partial_return(po_number, 
                                    skus_and_qtys, 
                                    reason_code, 
                                    reason_comment, 
                                    test, 
                                    return_warehouses)
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
ca_order = ca_api.get_order('<site order id>')
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