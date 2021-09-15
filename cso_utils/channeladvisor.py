import datetime

import requests

from . import stored_data

class ChannelAdvisorOrder(stored_data.StoredData):
    def po_number(self) -> str:
        """Return the PO Number."""
        return str(self._data['ID'])

    def site_name(self) -> str:
        """Return the site that the order is from."""
        return self._data['SiteName']

    def site_order_id(self) -> str:
        """Return the site order ID."""
        return self._data['SiteOrderID']

    def lines(self) -> [{'sku': str, 'title': str, 'qty': int, 'price': float, 'shipping_cost': float}]:
        """Return the items within the order as a list of dict."""
        items_ordered = []
        for item in self._data['Items']:
            items_ordered.append({'sku': item['Sku'], 
                                  'title': item['Title'], 
                                  'qty': item['Quantity'],
                                  'price': item['UnitPrice'], 
                                  'shipping_cost': item['UnitEstimatedShippingCost']})
        return items_ordered

    def creation_datetime(self) -> datetime.datetime:
        """Return the date and time the order was created."""
        return datetime.datetime.strptime(self._data['CreatedDateUtc'], '%Y-%m-%dT%H:%M:%SZ')

    def shipping_status(self) -> str:
        """Return the shipping status."""
        return self._data['ShippingStatus']


class ChannelAdvisor:
    def __init__(self, token: str):
        self._token = token

    def get_order(self, site_order_id_or_po: str) -> ChannelAdvisorOrder:
        """Return a ChannelAdvisorOrder object representing the order 
        with the given order ID or PO number.
        """
        if len(site_order_id_or_po) > 8:
            endpoint = f"https://api.channeladvisor.com/v1/Orders?access_token={self._token}&$expand=Items,Fulfillments&$filter=SiteOrderID eq '{site_order_id_or_po}'"
            response = requests.get(endpoint)
            response.raise_for_status()
            site_order_id_or_po = response.json()['value'][0]['ID']
        endpoint = f"https://api.channeladvisor.com/v1/Orders({site_order_id_or_po})?access_token={self._token}&$expand=Items,Fulfillments"
        response = requests.get(endpoint)
        response.raise_for_status()
        return ChannelAdvisorOrder(response.json())

    def get_orders_shipped_on(self, month: int, day: int, year: int) -> [ChannelAdvisorOrder]:
        """Return a list of orders shipped on the given date."""
        orders = []
        endpoint = f"https://api.channeladvisor.com/v1/Orders?access_token={self._token}&$expand=Items,Fulfillments&$filter=ShippingDateUtc eq {year}-{month}-{day} and ShippingStatus eq 'Shipped'"
        while True:
            response = requests.get(endpoint)
            response.raise_for_status()
            data = response.json()
            orders.extend([ChannelAdvisorOrder(item) for item in data['value']])
            endpoint = data.get('@odata.nextLink')
            if not endpoint:
                break
        return orders