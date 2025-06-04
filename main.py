import gradio as gr
import apiCall
import json


def api_call(
    base_url=None,
    auth_token=None,
    endpoint=None,
    param_keys_values=None,
    header_keys_values=None,
    additional_params=None,
    method="GET",
):
    """
    Make an API call to fetch data with dynamic parameters.

    Parameters:
    - base_url: The base URL of the API (e.g., "https://api.example.com")
    - auth_token: Optional authentication token for APIs requiring authorization
    - endpoint: The specific API endpoint to call (e.g., "search", "users/profile")
    - param_keys_values: String containing parameter key-value pairs, one per line in format "key: value"
    - header_keys_values: String containing header key-value pairs, one per line in format "key: value"
    - additional_params: Optional JSON string for complex parameters
    - method: HTTP method to use (GET, POST, PUT, DELETE)

    Instructions:
    - Format param_keys_values and header_keys_values as a multi-line string with each pair on a new line
    - For numeric values, simply use numbers without quotes
    - For boolean values, use "true" or "false" (lowercase)
    - For string values, just provide the string without additional quotes
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
        client = apiCall.APIClient(base_url, auth_token)
        result = client.make_request(
            endpoint=endpoint,
            params=params,
            headers=headers,
            method=method,
        )
        return result
    except Exception as e:
        return f"Error making API call: {str(e)}"


demo = gr.Interface(
    fn=api_call,
    inputs=[
        gr.Textbox(
            label="Base URL",
            placeholder="Enter base URL",
            value="https://v2.xivapi.com/api",
        ),
        gr.Textbox(label="Endpoint", placeholder="Enter endpoint", value="search"),
        gr.Textbox(
            label="Parameter Key-Value Pairs",
            placeholder="Enter one parameter per line in format 'key: value'",
            value='query: Name~"popoto"\nsheets: Item\nfields: Name,Description\nlanguage: en\nlimit: 1',
            lines=5,
        ),
        gr.Textbox(
            label="Header Key-Value Pairs",
            placeholder="Enter one header per line in format 'key: value'",
            value="",
            lines=3,
        ),
        gr.Textbox(
            label="Additional Parameters (JSON)",
            placeholder="Enter any additional parameters as JSON",
            value="{}",
            lines=3,
        ),
        gr.Radio(choices=["GET", "POST", "PUT", "DELETE"], label="Method", value="GET"),
    ],
    outputs=gr.Textbox(label="API Response", lines=10),
    title="Universal API Client",
    description="Make API calls to any endpoint with custom parameters. \n\n"
    + "- **Base URL**: Enter the full API base URL (e.g., 'https://api.example.com') \n"
    + "- **Endpoint**: The specific endpoint to call (without leading slash) \n"
    + "- **Parameter Key-Value Pairs**: Format as 'key: value' with each pair on a new line \n"
    + "  Example: \n```\nquery: search term\nlimit: 10\nfilter: active\n``` \n"
    + "- **Header Key-Value Pairs**: Format as 'key: value' with each pair on a new line \n"
    + "  Example: \n```\nx-api-key: your_api_key\ncontent-type: application/json\n``` \n"
    + "- **Additional Parameters**: Use valid JSON format for nested or complex parameters \n"
    + "- **Method**: Choose the appropriate HTTP method for your request",
    examples=[
        [
            "https://v2.xivapi.com/api",
            "",
            "search",
            'query: Name~"popoto"\nsheets: Item\nfields: Name,Description\nlanguage: en\nlimit: 1',
            "",
            "{}",
            "GET",
        ],
        [
            "https://api.github.com",
            "",
            "repos/microsoft/TypeScript/issues",
            "state: open\nper_page: 5",
            "Accept: application/vnd.github.v3+json",
            "{}",
            "GET",
        ],
        [
            "https://api.anthropic.com",
            "",
            "v1/messages",
            "model: claude-opus-4-20250514\nmax_tokens: 1024",
            "x-api-key: API-KEY-HERE\nanthropic-version: 2023-06-01\ncontent-type: application/json",
            '{"messages": [{"role": "user", "content": "Hello there!"}]}',
            "POST",
        ],
    ],
    flagging_mode="manual",
    flagging_options=["Invalid Request", "API Error", "Other"],
)

if __name__ == "__main__":
    demo.launch(mcp_server=True)
