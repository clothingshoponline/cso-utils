import requests

class ChannelAdvisorOrder:
    def __init__(self, json_data: [dict]):
        self._data = json_data

    def __repr__(self) -> str:
        return f'ChannelAdvisorOrder({self._data})'

    def data(self) -> [dict]:
        """Return order data."""
        return self._data

    def po_number(self) -> str:
        """Return the PO Number."""
        return str(self._data[0]['ID'])


class ChannelAdvisor:
    def __init__(self, token: str):
        self._token = token

    def get_order(self, site_order_id: str) -> ChannelAdvisorOrder:
        """Return a ChannelAdvisorOrder object representing the order 
        with the given order ID.
        """
        endpoint = f"https://api.channeladvisor.com/v1/Orders?access_token={token}&$expand=Items,Fulfillments&$filter=SiteOrderID eq '{site_order_id}'"
        response = requests.get(endpoint)
        response.raise_for_status()
        return ChannelAdvisorOrder(response.json()['value'])