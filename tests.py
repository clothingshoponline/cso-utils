from cso_utils import ssactivewear

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