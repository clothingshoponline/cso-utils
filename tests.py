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
                 'lines': [{'sku': '2', 'qtyShipped': 1}]}
        item2 = {'invoiceNumber': '3', 
                 'lines': [{'sku': '4', 'qtyShipped': 2}, 
                           {'sku': '5', 'qtyShipped': 3}, 
                           {'sku': '6', 'qtyShipped': 4}]}
        order1 = ssactivewear.Order([item1])
        order2 = ssactivewear.Order([item1, item2])
        assert order1.lines() == [{'invoice': '1', 'sku': '2', 'qty': 1}]
        assert order2.lines() == [{'invoice': '1', 'sku': '2', 'qty': 1}, 
                                  {'invoice': '3', 'sku': '4', 'qty': 2}, 
                                  {'invoice': '3', 'sku': '5', 'qty': 3}, 
                                  {'invoice': '3', 'sku': '6', 'qty': 4}]

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