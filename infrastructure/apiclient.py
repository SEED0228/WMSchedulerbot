import logging
import requests
from urllib.parse import urlencode
from copy import deepcopy

from config.config import WMS_API_BASE_URL, WMS_API_BASIC_AUTHORIZATION

logger = logging.getLogger(__name__)


class ApiClient:
    def __init__(self, prefix_url: str, basic_headers: dict):
        self.prefix_url = prefix_url
        self.basic_headers = basic_headers

    def _create_url(self, endpoint: str, query: dict) -> str:
        params = urlencode(query)
        return self.prefix_url + endpoint + "?" + params

    def _create_headers(self, extra: dict = None) -> dict:
        headers = deepcopy(self.basic_headers)
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
        url = self._create_url("api/v1/events/progresses/", query)
        headers = self._create_headers()
        response = requests.post(url=url, headers=headers)
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
    basic_headers={"Authorization": f"Basic {WMS_API_BASIC_AUTHORIZATION}"},
)
