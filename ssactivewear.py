class Order:
    def __init__(self, json_data: dict):
        self._data = json_data

    def __repr__(self) -> str:
        return f'Order({self._data})'

    def data(self) -> dict:
        """Return order data."""
        return self._data