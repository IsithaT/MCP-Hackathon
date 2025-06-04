import requests
import json


class APIClient:
    def __init__(self, base_url):
        """
        Initialize the API client with a base URL

        Parameters:
        - base_url: The base URL of the API
        """
        self.base_url = base_url.rstrip("/")

    def make_request(self, endpoint="", params=None, headers=None, method="GET"):
        """
        Make an HTTP request to the API endpoint.

        Parameters:
        - endpoint: API endpoint (without leading slash)
        - params: Dictionary of parameters to include in the request
        - headers: Dictionary of headers to include in the request
        - method: HTTP method (GET, POST, PUT, DELETE)

        Returns:
        - String representation of the API response
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}" if endpoint else self.base_url

        # Initialize headers dictionary if None
        if headers is None:
            headers = {}

        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=params, headers=headers)
            elif method.upper() == "PUT":
                response = requests.put(url, json=params, headers=headers)
            elif method.upper() == "DELETE":
                response = requests.delete(url, json=params, headers=headers)
            else:
                return f"Unsupported method: {method}"

            # Check if the response is successful
            response.raise_for_status()

            # Try to parse JSON response
            try:
                result = response.json()
                return json.dumps(result, indent=2)
            except ValueError:
                # Return raw text if not JSON
                return response.text

        except requests.exceptions.RequestException as e:
            return f"Request error: {str(e)}"
