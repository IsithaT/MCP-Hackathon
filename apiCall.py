import requests
import json


class APIClient:
    def __init__(self, base_url="https://v2.xivapi.com/api", auth_token=None):
        self.base_url = base_url if base_url else "https://v2.xivapi.com/api"
        self.auth_token = auth_token

    def make_request(
        self, endpoint=None, params=None, method="GET", data=None, json_data=None
    ):
        """
        Make an API request with flexible parameters.
        """
        url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url

        # Remove trailing slash if endpoint is empty
        if endpoint == "":
            url = self.base_url.rstrip("/")

        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        kwargs = {"headers": headers}

        if params:
            kwargs["params"] = params
        if data:
            kwargs["data"] = data
        if json_data:
            kwargs["json"] = json_data

        try:
            print(f"Making {method} request to {url}")
            print(f"Parameters: {params}")

            response = requests.request(method, url, **kwargs)

            # Try to parse response as JSON
            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return response.text

            return f"Error {response.status_code}: {response.text}"
        except requests.exceptions.RequestException as e:
            return f"Request Error: {str(e)}"
