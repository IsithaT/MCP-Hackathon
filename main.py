import gradio as gr
from apiCall import api_call


demo = gr.Interface(
    fn=api_call,
    inputs=[
        gr.Radio(choices=["GET", "POST", "PUT", "DELETE"], label="Method", value="GET"),
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
    ],
    outputs=gr.Textbox(label="API Response", lines=10),
    title="Universal API Client",
    description="Make API calls to any endpoint with custom parameters and headers. \n\n- **Method**: Choose the appropriate HTTP method for your request \n- **Base URL**: Enter the full API base URL (e.g., 'https://api.example.com') \n- **Endpoint**: The specific endpoint to call (without leading slash) \n- **Parameter Key-Value Pairs**: Format as 'key: value' with each pair on a new line \n  Example: \n```\nquery: search term\nlimit: 10\nfilter: active\n``` \n- **Header Key-Value Pairs**: Format as 'key: value' with each pair on a new line \n  Example: \n```\nx-api-key: your_api_key\ncontent-type: application/json\n``` \n- **Additional Parameters**: Use valid JSON format for nested or complex parameters",
    flagging_mode="manual",
    flagging_options=["Invalid Request", "API Error", "Other"],
    examples=[
        [
            "GET",
            "https://v2.xivapi.com/api",
            "search",
            'query: Name~"popoto"\nsheets: Item\nfields: Name,Description\nlanguage: en\nlimit: 1',
            "",
            "{}",
        ],
        [
            "GET",
            "https://api.github.com",
            "repos/microsoft/TypeScript/issues",
            "state: open\nper_page: 5",
            "Accept: application/vnd.github.v3+json",
            "{}",
        ],
        [
            "POST",
            "https://api.anthropic.com",
            "v1/messages",
            "model: claude-opus-4-20250514\nmax_tokens: 1024",
            "x-api-key: your_api_key_here\nanthropic-version: 2023-06-01\ncontent-type: application/json",
            '{"messages": [{"role": "user", "content": "what is a chicken"}]}',
        ],
    ],
)

if __name__ == "__main__":
    demo.launch(mcp_server=True)
