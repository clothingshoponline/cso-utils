import pytest

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

class TestTracking:
    def test_repr(self):
        tracking = ssactivewear.Tracking([{'carrierName': 'A', 'trackingNumber': '1'}])
        assert str(tracking) == "Tracking([{'carrierName': 'A', 'trackingNumber': '1'}])"

    def test_data(self):
        tracking = ssactivewear.Tracking([{'carrierName': 'A', 'trackingNumber': '1'}])
        assert tracking.data() == [{'carrierName': 'A', 'trackingNumber': '1'}]

    def test_num_and_status(self):
        tracking1 = ssactivewear.Tracking([{'trackingNumber': '1', 
                                            'latestCheckpoint': {'checkpointStatusMessage': 'A'}}])
        tracking2 = ssactivewear.Tracking([{'trackingNumber': '2', 
                                            'latestCheckpoint': {'checkpointStatusMessage': 'B'}}, 
                                           {'trackingNumber': '3', 
                                            'latestCheckpoint': {'checkpointStatusMessage': 'C'}}])
        assert tracking1.num_and_status() == [('1', 'A')]
        assert tracking2.num_and_status() == [('2', 'B'), ('3', 'C')]

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

    def test_match_skus_with_invoice(self):
        original_lines = [{'invoice': '0', 'sku': '2', 'qty_shipped': 11}, 
                          {'invoice': '0', 'sku': '3', 'qty_shipped': 12}, 
                          {'invoice': '0', 'sku': '4', 'qty_shipped': 13}, 
                          {'invoice': '1', 'sku': '5', 'qty_shipped': 14}, 
                          {'invoice': '1', 'sku': '6', 'qty_shipped': 15}, 
                          {'invoice': '1', 'sku': '7', 'qty_shipped': 16}, 
                          {'invoice': '1', 'sku': '8', 'qty_shipped': 17}, 
                          {'invoice': '1', 'sku': '9', 'qty_shipped': 18}]
        ssapi = ssactivewear.SSActivewear('test', 'test')

        wrong_sku = {'10': 1, '2': 5}
        with pytest.raises(ValueError, match=r'sku or qty not in original order'):
            ssapi._match_skus_with_invoice(original_lines, wrong_sku)

        wrong_qty = {'2': 12}
        with pytest.raises(ValueError, match=r'sku or qty not in original order'):
            ssapi._match_skus_with_invoice(original_lines, wrong_qty)

        part_of_order = {'2': 5, '7': 4, '9': 9, '3': 12}
        assert (ssapi._match_skus_with_invoice(original_lines, part_of_order) == 
                [{'invoice': '0', 'sku': '2', 'qty_shipped': 5}, 
                 {'invoice': '0', 'sku': '3', 'qty_shipped': 12}, 
                 {'invoice': '1', 'sku': '7', 'qty_shipped': 4}, 
                 {'invoice': '1', 'sku': '9', 'qty_shipped': 9}])

        all_of_order = {'2': 11, '3': 12, '4': 13, '5': 14, 
                        '6': 15, '7': 16, '8': 17, '9': 18}
        assert ssapi._match_skus_with_invoice(original_lines, all_of_order) == original_lines



from cso_utils import zendesk

class TestTicket:
    def test_id_num(self):
        ticket = zendesk.Ticket({'id': '1'})
        assert ticket.id_num() == '1'

    def test_subject(self):
        ticket = zendesk.Ticket({'subject': 'Where is my order?'})
        assert ticket.subject() == 'Where is my order?'

    def test_custom_fields(self):
        ticket1 = zendesk.Ticket({'custom_fields': [{'id': '1', 'value': '2'}]})
        ticket2 = zendesk.Ticket({'custom_fields': [{'id': '3', 'value': '4'}, 
                                                    {'id': '5', 'value': '6'}]})
        assert ticket1.custom_fields() == {'1': '2'}
        assert ticket2.custom_fields() == {'3': '4', '5': '6'}

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