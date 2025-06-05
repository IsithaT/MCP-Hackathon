import requests
import json
import psycopg2

def api_call(
    method="GET",
    base_url=None,
    endpoint=None,
    param_keys_values=None,
    header_keys_values=None,
    additional_params=None,
):
    """Make an API call to fetch data with dynamic headers and parameters.

    Parameters:
    - method: HTTP method to use (GET, POST, PUT, DELETE)
    - base_url: The base URL of the API
    - endpoint: The specific API endpoint
    - param_keys_values: Parameter key-value pairs, one per line
    - header_keys_values: Header key-value pairs, one per line
    - additional_params: Optional JSON string for complex parameters

    Examples:

    1. Simple GET request to a search API:
        method: "GET"
        base_url: "https://v2.xivapi.com/api"
        endpoint: "search"
        param_keys_values:
            query: Name~"popoto"
            sheets: Item
            fields: Name,Description
            language: en
            limit: 1

    2. GitHub API request with headers:
        method: "GET"
        base_url: "https://api.github.com"
        endpoint: "repos/microsoft/TypeScript/issues"
        param_keys_values:
            state: open
            per_page: 5
        header_keys_values:
            Accept: application/vnd.github.v3+json

    3. POST request with JSON body. the "messages" parameter is complexly structured, so it requires special handling."
        method: "POST"
        base_url: "https://api.anthropic.com"
        endpoint: "v1/messages"
        param_keys_values:
            model: claude-opus-4-20250514
            max_tokens: 1024
        header_keys_values:
            x-api-key: your_api_key_here
            content-type: application/json
        additional_params: {"messages": [{"role": "user", "content": "Hello there!"}]}
    """
    # Build params dictionary from key-value pairs
    params = {}
    headers = {}

    # Process param_keys_values
    if param_keys_values:
        lines = param_keys_values.strip().split("\n")
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                if key:  # Only add non-empty keys
                    # Try to parse numeric values
                    if value.isdigit():
                        params[key] = int(value)
                    elif value.lower() == "true":
                        params[key] = True
                    elif value.lower() == "false":
                        params[key] = False
                    else:
                        params[key] = value

    # Process header_keys_values
    if header_keys_values:
        lines = header_keys_values.strip().split("\n")
        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()

                if key:  # Only add non-empty keys
                    headers[key] = value

    # Handle additional parameters
    if additional_params and additional_params.strip():
        try:
            # Parse additional JSON parameters
            extra_params = json.loads(additional_params)
            if isinstance(extra_params, dict):
                params.update(extra_params)
            else:
                return "Error: Additional parameters must be a valid JSON object"
        except json.JSONDecodeError as e:
            return f"Error parsing additional parameters: {str(e)}"

    try:
        client = APIClient(base_url)
        result = client.make_request(
            endpoint=endpoint,
            params=params,
            headers=headers,
            method=method,
        )        
        return result
    
    except Exception as e:
        return f"Error making API call: {str(e)}"


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
