from cso_utils import ssactivewear

class TestOrder:
    def test_repr(self):
        order = ssactivewear.Order([{'A': 1}, {'B': 2}])
        assert str(order) == "Order([{'A': 1}, {'B': 2}])"

    def test_data(self):
        order = ssactivewear.Order([{'A': 1}, {'B': 2}])
        assert order.data() == [{'A': 1}, {'B': 2}]

    def test_lines(self):
        item1 = {'invoiceNumber': '1', 
                 'lines': [{'sku': '2', 'qtyOrdered': 5, 'qtyShipped': 1}]}
        item2 = {'invoiceNumber': '3', 
                 'lines': [{'sku': '4', 'qtyOrdered': 6, 'qtyShipped': 2}, 
                           {'sku': '5', 'qtyOrdered': 7, 'qtyShipped': 3}, 
                           {'sku': '6', 'qtyOrdered': 8, 'qtyShipped': 4}]}
        order1 = ssactivewear.Order([item1])
        order2 = ssactivewear.Order([item1, item2])
        assert order1.lines() == [{'invoice': '1', 'sku': '2', 'qty_ordered': 5, 'qty_shipped': 1}]
        assert order2.lines() == [{'invoice': '1', 'sku': '2', 'qty_ordered': 5, 'qty_shipped': 1}, 
                                  {'invoice': '3', 'sku': '4', 'qty_ordered': 6, 'qty_shipped': 2}, 
                                  {'invoice': '3', 'sku': '5', 'qty_ordered': 7, 'qty_shipped': 3}, 
                                  {'invoice': '3', 'sku': '6', 'qty_ordered': 8, 'qty_shipped': 4}]

class TestSSActivewear:
    def test_filter(self):
        response = [{'poNumber': '111', 'orderType': 'Order', 'orderStatus': 'Shipped'}, 
                    {'poNumber': '222', 'orderType': 'Order', 'orderStatus': 'Shipped'}, 
                    {'poNumber': '111', 'orderType': 'Credit', 'orderStatus': 'Shipped'}, 
                    {'poNumber': '111', 'orderType': 'Order', 'orderStatus': 'Cancelled'}, 
                    {'poNumber': '222', 'orderType': 'Credit', 'orderStatus': 'Shipped'}, 
                    {'poNumber': '222', 'orderType': 'Order', 'orderStatus': 'Cancelled'}, 
                    {'poNumber': '111', 'orderType': 'Credit', 'orderStatus': 'Cancelled'}, 
                    {'poNumber': '222', 'orderType': 'Credit', 'orderStatus': 'Cancelled'}]
        ssapi = ssactivewear.SSActivewear('test', 'test')
        assert ssapi._filter('111', response) == response[:1]


from cso_utils import zendesk

class TestTicket:
    def test_sent_from(self):
        email = 'someone@example.com'
        ticket1 = zendesk.Ticket({'via': {'channel': 'email', 
                                          'source': {'from': {'address': email}}}})
        ticket2 = zendesk.Ticket({'via': {'channel': 'api', 
                                          'source': {'from': {}}}})
        assert ticket1.sent_from(email)
        assert not ticket1.sent_from('bla')
        assert not ticket2.sent_from(email)

class TestZendesk:
    def test_init(self):
        zen = zendesk.Zendesk('subdomain', 'someone@example.com', 'token1')
        assert zen._subdomain == 'subdomain'
        assert zen._auth == ('someone@example.com/token', 'token1')
        assert zen._url == 'https://subdomain.zendesk.com/api/v2/tickets'