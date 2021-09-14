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

    def test_tracking_nums(self):
        order = ssactivewear.Order([{'trackingNumber': '1'}, {'trackingNumber': '2'}])
        assert order.tracking_nums() == ['1', '2']

    def test_order_nums(self):
        order = ssactivewear.Order([{'orderNumber': '3'}, {'orderNumber': '4'}])
        assert order.order_nums() == ['3', '4']

    def test_invoices(self):
        order = ssactivewear.Order([{'invoiceNumber': '5'}, {'invoiceNumber': '6'}])
        assert order.invoices() == ['5', '6']

    def test_guids(self):
        order = ssactivewear.Order([{'guid': '7'}, {'guid': '8'}])
        assert order.guids() == ['7', '8']
        
    def test_data_nums(self):
        order1 = ssactivewear.Order([])
        order2 = ssactivewear.Order([{'invoiceNumber': '9'}])
        order3 = ssactivewear.Order([{'invoiceNumber': '10'}, {'invoiceNumber': '11'}])
        assert order1._data_nums('invoiceNumber') == []
        assert order2._data_nums('invoiceNumber') == ['9']
        assert order3._data_nums('invoiceNumber') == ['10', '11']
        

class TestTracking:
    def test_repr(self):
        tracking = ssactivewear.Tracking([{'carrierName': 'A', 'trackingNumber': '1'}])
        assert str(tracking) == "Tracking([{'carrierName': 'A', 'trackingNumber': '1'}])"

    def test_data(self):
        tracking = ssactivewear.Tracking([{'carrierName': 'A', 'trackingNumber': '1'}])
        assert tracking.data() == [{'carrierName': 'A', 'trackingNumber': '1'}]

    def test_num_and_status(self):
        tracking1 = ssactivewear.Tracking([{'trackingNumber': '1', 
                                            'latestCheckpoint': {'checkpointDate': '6/28/2021', 
                                                                 'checkpointTime': '7:00 AM', 
                                                                 'checkpointStatusMessage': 'A'}}])
        tracking2 = ssactivewear.Tracking([{'trackingNumber': '2', 
                                            'latestCheckpoint': {'checkpointDate': '6/29/2021', 
                                                                 'checkpointTime': '8:00 AM', 
                                                                 'checkpointStatusMessage': 'B'}}, 
                                           {'trackingNumber': '3', 
                                            'latestCheckpoint': {'checkpointDate': '6/30/2021', 
                                                                 'checkpointTime': '9:00 PM', 
                                                                 'checkpointStatusMessage': 'C'}}])
        assert tracking1.num_and_status() == [('1', '6/28/2021 at 7:00 AM - A')]
        assert tracking2.num_and_status() == [('2', '6/29/2021 at 8:00 AM - B'), 
                                              ('3', '6/30/2021 at 9:00 PM - C')]

class TestReturnRequest:
    def test_repr(self):
        return_request = ssactivewear.ReturnRequest([{'ra': '123'}])
        assert str(return_request) == "ReturnRequest([{'ra': '123'}])"

    def test_data(self):
        return_request = ssactivewear.ReturnRequest([{'ra': '123'}])
        assert return_request.data() == [{'ra': '123'}]

    def test_instructions(self):
        return_request = ssactivewear.ReturnRequest([{'returnInformation': {'raNumber': '321', 
                                                                            'returnToAddress': {'city': 'somewhere'}}}])
        assert return_request.instructions() == ('321', {'city': 'somewhere'})

class TestProduct:
    def test_sku(self):
        product = ssactivewear.Product({'sku': 'B0'})
        assert product.sku() == 'B0'

    def test_brand(self):
        product = ssactivewear.Product({'brandName': 'brand'})
        assert product.brand() == 'brand'

    def test_style(self):
        product = ssactivewear.Product({'styleName': 'style'})
        assert product.style() == 'style'

    def test_price(self):
        product = ssactivewear.Product({'piecePrice': 1.23})
        assert product.price() == 1.23


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


from cso_utils import channeladvisor

class TestChannelAdvisorOrder:
    def test_repr(self):
        ca_order = channeladvisor.ChannelAdvisorOrder({'ID': '123'})
        assert str(ca_order) == "ChannelAdvisorOrder({'ID': '123'})"

    def test_data(self):
        ca_order = channeladvisor.ChannelAdvisorOrder({'ID': '123'})
        assert ca_order.data() == {'ID': '123'}

    def test_po_number(self):
        ca_order = channeladvisor.ChannelAdvisorOrder({'ID': '123'})
        assert ca_order.po_number() == '123'