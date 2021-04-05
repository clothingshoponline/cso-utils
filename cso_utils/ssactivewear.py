import requests


class Order:
    def __init__(self, json_data: [dict]):
        self._data = json_data

    def __repr__(self) -> str:
        return f'Order({self._data})'

    def data(self) -> dict:
        """Return order data."""
        return self._data

    def lines(self) -> [dict]:
        """Return a list of lines where each line 
        has invoice, sku, qty_ordered and qty_shipped.
        """
        lines = []
        for package in self._data:
            for line in package['lines']:
                lines.append({'invoice': package['invoiceNumber'], 
                              'sku': line['sku'], 
                              'qty_ordered': line['qtyOrdered'], 
                              'qty_shipped': line['qtyShipped']})
        return lines


class SSActivewear:
    def __init__(self, account: str, password: str):
        self._auth = (account, password)
        self._orders_endpoint = 'https://api.ssactivewear.com/v2/orders/'
        self._returns_endpoint = 'https://api.ssactivewear.com/v2/returns/'
        self._headers = {'Content-Type': 'application/json'}

    def get_order(self, po_number: str) -> Order:
        """Return an Order object representing the order with 
        the given PO number. Ignore returns and cancellations.
        """
        response = requests.get(self._orders_endpoint + po_number + '?lines=true', 
                                auth=self._auth, 
                                headers=self._headers)
        response.raise_for_status()
        return Order(self._filter(po_number, response.json()))

    def _filter(self, po_number: str, response: [dict]) -> [dict]:
        """Filter out items with the wrong PO, returns, or cancelled orders."""
        data = []
        for package in response:
            if (package['poNumber'] == po_number 
                and package['orderType'] != 'Credit' 
                and package['orderStatus'] != 'Cancelled'):
                data.append(package)
        return data

    def full_return(self, po_number: str, reason_code: int, 
                    reason_comment: str, test: bool) -> (str, dict):
        """Request a full return. Return (RA number, shipping address)."""
        original_order = self.get_order(po_number)
        lines = []
        for line in original_order.lines():
            lines.append({'invoiceNumber': line['invoice'], 
                          'identifier': line['sku'], 
                          'qty': line['qty_shipped'], 
                          'showBoxes': False, 
                          'returnReason': reason_code, 
                          'isReplace': False, 
                          'returnReasonComment': reason_comment})
        data = {'emailConfirmation': '', 
                'testOrder': test, 
                'shippingLabelRequired': False, 
                'lines': lines}
        response = requests.post(self._returns_endpoint, 
                                 auth=self._auth, 
                                 json=data)
        response.raise_for_status()
        return_info = response.json()[0]['returnInformation']
        return (return_info['raNumber'], return_info['returnToAddress'])