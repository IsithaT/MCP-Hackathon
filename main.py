import gradio as gr
import apiCall
import json


def api_call(
    base_url=None,
    auth_token=None,
    endpoint=None,
    param_keys_values=None,
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
    - additional_params: Optional JSON string for complex parameters
    - method: HTTP method to use (GET, POST, PUT, DELETE)

    Instructions:
    - Format param_keys_values as a multi-line string with each parameter on a new line
    - For numeric values, simply use numbers without quotes
    - For boolean values, use "true" or "false" (lowercase)
    - For string values, just provide the string without additional quotes
    """
    # Build params dictionary from key-value pairs
    params = {}

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
            method=method,
        )
        return result
    except Exception as e:
        return f"Error making API call: {str(e)}"


app = gr.Interface(
    fn=api_call,
    inputs=[
        gr.Textbox(
            label="Base URL",
            placeholder="Enter base URL",
            value="https://v2.xivapi.com/api",
        ),
        gr.Textbox(label="Auth Token", placeholder="Enter auth token (optional)"),
        gr.Textbox(label="Endpoint", placeholder="Enter endpoint", value="search"),
        gr.Textbox(
            label="Parameter Key-Value Pairs",
            placeholder="Enter one parameter per line in format 'key: value'",
            value='query: Name~"popoto"\nsheets: Item\nfields: Name,Description\nlanguage: en\nlimit: 1',
            lines=5,
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
    + "- **Auth Token**: Provide if the API requires authentication \n"
    + "- **Endpoint**: The specific endpoint to call (without leading slash) \n"
    + "- **Parameter Key-Value Pairs**: Format as 'key: value' with each pair on a new line \n"
    + "  Example: \n```\nquery: search term\nlimit: 10\nfilter: active\n``` \n"
    + "- **Additional Parameters**: Use valid JSON format for nested or complex parameters \n"
    + "- **Method**: Choose the appropriate HTTP method for your request",
    examples=[
        [
            "https://v2.xivapi.com/api",
            "",
            "search",
            'query: Name~"popoto"\nsheets: Item\nfields: Name,Description\nlanguage: en\nlimit: 1',
            "{}",
            "GET",
        ],
        [
            "https://api.github.com",
            "",
            "repos/microsoft/TypeScript/issues",
            "state: open\nper_page: 5",
            "{}",
            "GET",
        ],
    ],
    allow_flagging="never",
)

if __name__ == "__main__":
    app.launch(mcp_server=True)
