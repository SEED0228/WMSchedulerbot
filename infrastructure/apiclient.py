import json
import logging
import requests
from urllib.parse import urlencode
from copy import deepcopy

from config.config import WMS_API_BASE_URL, WMS_API_BASIC_AUTHORIZATION

logger = logging.getLogger(__name__)


class ApiClient:
    def __init__(self, prefix_url: str, auth_header: dict):
        self.prefix_url = prefix_url
        self.auth_header = auth_header

    def _create_url(self, endpoint: str, query: dict = None) -> str:
        if query:
            params = urlencode(query)
            return self.prefix_url + endpoint + "?" + params
        return self.prefix_url + endpoint

    def _create_headers(self, extra: dict = None) -> dict:
        headers = deepcopy(self.auth_header)
        if extra:
            headers.update(extra)
        return headers

    def fetch_events(self, query: dict) -> requests.Response:
        url = self._create_url("api/v1/events/", query)
        headers = self._create_headers()
        response = requests.get(url=url, headers=headers)
        logger.info(response.text)
        return response

    def fetch_event_progresses(self, query: dict) -> requests.Response:
        url = self._create_url("api/v1/events/progresses/", query)
        headers = self._create_headers()
        response = requests.get(url=url, headers=headers)
        logger.info(response.text)
        return response

    def create_and_update_event_progresses(self, query: dict) -> requests.Response:
        url = self._create_url("api/v1/events/progresses/")
        headers = self._create_headers(
            {
                "Content-Type": "application/json",
            }
        )
        response = requests.post(url=url, headers=headers, data=json.dumps(query))
        logger.info(response.text)
        return response

    def delete_event_progresses(self, query: dict) -> requests.Response:
        url = self._create_url("api/v1/events/progresses/", query)
        headers = self._create_headers()
        response = requests.delete(url=url, headers=headers)
        logger.info(response.text)
        return response


apiClient = ApiClient(
    prefix_url=WMS_API_BASE_URL,
    auth_header={"Authorization": f"Basic {WMS_API_BASIC_AUTHORIZATION}"},
)
