import requests

from . import stored_data

class ChannelAdvisorOrder(stored_data.StoredData):
    def po_number(self) -> str:
        """Return the PO Number."""
        return str(self._data['ID'])


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
