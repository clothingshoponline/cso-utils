import datetime

import requests

from . import stored_data


class Order(stored_data.StoredData):
    def po_number(self) -> str:
        """Return the PO number."""
        return self._data[0]['poNumber']

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
                              'qty_shipped': line.get('qtyShipped', 0)})
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


class Tracking(stored_data.StoredData):
    def num_and_status(self) -> [(str, str)]:
        """Return a list of (tracking number, latest checkpoint status)."""
        tracking = []
        for package in self._data:
            latest = package['latestCheckpoint']
            status = f"{latest['checkpointDate']} at {latest['checkpointTime']} - {latest['checkpointStatusMessage']}"
            tracking.append((package['trackingNumber'], status))
        return tracking


class ReturnRequest(stored_data.StoredData):
    def instructions(self) -> (str, dict):
        """Return the (RA number, address to send items to)."""
        info = self._data[0]['returnInformation']
        return (info['raNumber'], info['returnToAddress'])


class Product(stored_data.StoredData):
    def sku(self) -> str:
        """Return the sku."""
        return self._data['sku']

    def brand_name(self) -> str:
        """Return the brand name."""
        return self._data['brandName']

    def style_name(self) -> str:
        """Return the style name."""
        return self._data['styleName']

    def piece_price(self) -> float:
        """Return the piece price."""
        return self._data['piecePrice']

    def case_price(self) -> float:
        """Return the case price."""
        return self._data['casePrice']

    def sale_price(self) -> float:
        """Return the sale price."""
        return self._data['salePrice']


class Style(stored_data.StoredData):
    def title(self) -> str:
        """Return the title."""
        return self._data['title']

    def base_category(self) -> str:
        """Return the base category."""
        return self._data['baseCategory']


class SSActivewear:
    def __init__(self, account: str, password: str):
        self._auth = (account, password)
        self._endpoint = 'https://api.ssactivewear.com/v2/'
        self._headers = {'Content-Type': 'application/json'}

    def get_order(self, po_number: str) -> Order:
        """Return an order object representing the order with 
        the given PO number. Ignore returns and cancellations.
        """
        return self._get_order_using(po_number)

    def get_invoice(self, invoice: str) -> Order:
        """Return an Order object representing the given invoice. 
        Ignore returns and cancellations.
        """ 
        return self._get_order_using(invoice, 'invoice')

    def _get_order_using(self, po_number_or_invoice: str, 
                         id_type: 'po' or 'invoice' = 'po') -> Order:
        """Return an Order object representing the order with 
        the given PO number or invoice. Ignore returns and cancellations.
        """
        response = requests.get(self._endpoint + 'orders/' + po_number_or_invoice + '?lines=true',
                                auth=self._auth,
                                headers=self._headers)
        response.raise_for_status()
        return Order(self._filter(po_number_or_invoice, response.json(), id_type))

    def _filter(self, po_number_or_invoice: str, response: [dict], 
                id_type: 'po' or 'invoice' = 'po') -> [dict]:
        """Filter out items with returns, cancelled orders, 
        wrong PO, or wrong invoice.
        """
        data = []
        if id_type == 'po':
            key = 'poNumber'
        elif id_type == 'invoice':
            key = 'invoiceNumber'
        for package in response:
            if (package[key] == po_number_or_invoice 
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
        response = requests.post(self._endpoint + 'returns/',
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

    def track_using_actual_delivery_dates(self, dates: [datetime.datetime]) -> Tracking:
        """Return Tracking for orders delivered on the given dates."""
        formatted_dates = []
        for date in dates:
            formatted_dates.append(f"{date.year}-{date.month}-{date.day}")
        return self._track_using('ActualDeliveryDate', formatted_dates)

    def _track_using(self, data_type: str, list_of_numbers: [str]) -> Tracking:
        """Return Tracking for the given data_type."""
        url = self._endpoint + 'TrackingDataBy' + \
              data_type + '/' + ','.join(list_of_numbers)
        response = requests.get(url, auth=self._auth, headers=self._headers)
        response.raise_for_status()
        return Tracking(response.json())

    def get_product(self, sku: str) -> Product:
        """Return Product for the given sku."""
        response = requests.get(self._endpoint + 'products/' + sku,
                                auth=self._auth,
                                headers=self._headers)
        response.raise_for_status()
        return Product(response.json()[0])
        
    def get_products(self) -> {str: Product}:
        """Return all products as Product objects stored in a dict 
        with the keys being the skus.
        """
        response = requests.get(self._endpoint + 'products/',
                                auth=self._auth,
                                headers=self._headers)
        response.raise_for_status()
        products = dict()
        for product in response.json():
            products[product['sku']] = Product(product)
        return products

    def get_style(self, style_id: int) -> Style:
        """Return Style for the given style ID."""
        response = requests.get(self._endpoint + 'styles/' + str(style_id),
                                auth=self._auth,
                                headers=self._headers)
        response.raise_for_status()
        return Style(response.json()[0])

    def get_styles(self) -> {int: Style}:
        """Return all styles as Style objects stored in a dict 
        with the keys being style IDs.
        """
        response = requests.get(self._endpoint + 'styles/',
                                auth=self._auth,
                                headers=self._headers)
        response.raise_for_status()
        styles = dict()
        for style in response.json():
            styles[style['styleID']] = Style(style)
        return styles