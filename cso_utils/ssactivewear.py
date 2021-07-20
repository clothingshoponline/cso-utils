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

    def tracking_nums(self) -> [str]:
        """Return a list of tracking numbers."""
        return self._data_nums('trackingNumber')

    def order_nums(self) -> [str]:
        """Return a list of order numbers."""
        return self._data_nums('orderNumber')

    def invoices(self) -> [str]:
        """Return a list of invoice numbers."""
        return self._data_nums('invoiceNumber')

    def guids(self) -> [str]:
        """Return a list of guids."""
        return self._data_nums('guid')

    def _data_nums(self, data_type: str) -> [str]:
        """Return a list of invoice/order/tracking/guid numbers."""
        numbers = []
        for package in self._data:
            numbers.append(package[data_type])
        return numbers


class Tracking:
    def __init__(self, json_data: [dict]):
        self._data = json_data

    def __repr__(self) -> str:
        return f'Tracking({self._data})'

    def data(self) -> [dict]:
        """Return tracking data."""
        return self._data

    def num_and_status(self) -> [(str, str)]:
        """Return a list of (tracking number, latest checkpoint status)."""
        tracking = []
        for package in self._data:
            latest = package['latestCheckpoint']
            status = f"{latest['checkpointDate']} at {latest['checkpointTime']} - {latest['checkpointStatusMessage']}"
            tracking.append((package['trackingNumber'], status))
        return tracking

class ReturnRequest:
    def __init__(self, json_data: [dict]):
        self._data = json_data

    def __repr__(self) -> str:
        return f'ReturnRequest({self._data})'

    def data(self) -> [dict]:
        """Return the Return's data."""
        return self._data

    def instructions(self) -> (str, dict):
        """Return the (RA number, address to send items to)."""
        info = self._data[0]['returnInformation']
        return (info['raNumber'], info['returnToAddress'])

class SSActivewear:
    def __init__(self, account: str, password: str):
        self._auth = (account, password)
        self._endpoint = 'https://api.ssactivewear.com/v2/'
        self._orders_endpoint = self._endpoint + 'orders/'
        self._returns_endpoint = self._endpoint + 'returns/'
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
                    reason_comment: str, test: bool, 
                    return_warehouses: [str] = None, 
                    force_restock: bool = False) -> ReturnRequest:
        """Request a full return."""
        original_order = self.get_order(po_number)
        ra_info = self._return_request(original_order.lines(), reason_code, 
                                       reason_comment, test, return_warehouses, 
                                       force_restock)
        return ra_info

    def partial_return(self, po_number: str, skus_and_qtys: {str: int}, reason_code: int, 
                       reason_comment: str, test: bool, 
                       return_warehouses: [str] = None, 
                       force_restock: bool = False) -> ReturnRequest:
        """Request a partial return."""
        original_order = self.get_order(po_number)
        lines_with_invoice = self._match_skus_with_invoice(original_order.lines(), 
                                                           skus_and_qtys)
        ra_info = self._return_request(lines_with_invoice, reason_code, 
                                       reason_comment, test, return_warehouses, 
                                       force_restock)
        return ra_info

    def _return_request(self, lines_to_return: [{'invoice': str, 'sku': str, 'qty_shipped': int}], 
                        reason_code: int, reason_comment: str, test: bool, 
                        return_warehouses: [str] or None, force_restock: bool) -> ReturnRequest:
        """Create return request and send to API."""
        lines = []
        for line in lines_to_return:
            lines.append({'invoiceNumber': line['invoice'], 
                          'identifier': line['sku'], 
                          'qty': line['qty_shipped'], 
                          'returnReason': reason_code, 
                          'isReplace': False, 
                          'returnReasonComment': reason_comment})
        data = {'emailConfirmation': '', 
                'testOrder': test, 
                'shippingLabelRequired': False, 
                'showBoxes': False, 
                'lines': lines, 
                'OverrideRestockFee': True, 
                'OverrideHandling': True, 
                'ForceRestock': force_restock}
        if return_warehouses:
            data['returnToWareHouses'] = ','.join(return_warehouses)
        response = requests.post(self._returns_endpoint, 
                                 auth=self._auth, 
                                 json=data)
        response.raise_for_status()
        return ReturnRequest(response.json())

    def _match_skus_with_invoice(self, 
                                 original_lines: [{'invoice': str, 'sku': str, 'qty_shipped': int}],
                                 skus_and_qtys: {str: int}) -> [dict]:
        """Match skus with invoices from original order. Return [dict] where each dict 
        has invoice, sku, and qty_shipped.
        """
        lines_with_invoice = []
        for original_line in original_lines:
            sku = original_line['sku']
            if sku in skus_and_qtys and original_line['qty_shipped'] >= skus_and_qtys[sku]:
                lines_with_invoice.append({'invoice': original_line['invoice'], 
                                           'sku': sku, 
                                           'qty_shipped': skus_and_qtys[sku]})
                del skus_and_qtys[sku]
        if len(skus_and_qtys) != 0:
            raise ValueError('sku or qty not in original order')
        return lines_with_invoice

    def track_using_invoices(self, nums: [str]) -> Tracking:
        """Return Tracking for the given invoices."""
        return self._track_using('Invoice', nums)

    def track_using_tracking(self, nums: [str]) -> Tracking:
        """Return Tracking for the given tracking numbers."""
        return self._track_using('TrackingNum', nums)

    def track_using_order_nums(self, nums: [str]) -> Tracking:
        """Return Tracking for the given order numbers."""
        return self._track_using('OrderNum', nums)

    def _track_using(self, data_type: str, list_of_numbers: [str]) -> Tracking:
        """Return Tracking for the given data_type."""
        url = self._endpoint + 'TrackingDataBy' + data_type + '/' + ','.join(list_of_numbers)
        response = requests.get(url, auth=self._auth, headers=self._headers)
        response.raise_for_status()
        return Tracking(response.json())