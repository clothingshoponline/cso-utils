class StoredData:
    def __init__(self, json_data: [dict] or dict):
        self._data = json_data

    def __repr__(self) -> str:
        return f'{type(self).__name__}({self._data})'

    def data(self) -> [dict] or dict:
        """Return data."""
        return self._data