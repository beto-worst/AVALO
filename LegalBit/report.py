import requests
import json


class ReportService:
    base_url = 'http://45.15.168.142:3001/'

    def __init__(self):
        self.session = requests.Session()

    def request(
        self, method: str, endpoint: str, data: dict, **kwargs
    ) -> bytes:
        url = self.base_url + endpoint
        response = self.session.request(method, url, json=data, **kwargs)
        if not response.ok:
            response.raise_for_status()
        return response.json()

    def render(self, data: dict, **kwargs) -> bytes:
        result = self.request(
            method='post', endpoint='report', data=data, **kwargs)
        return result
