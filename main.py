import gradio as gr
from apiCall import api_call
from api_validator import validate_api_call, setup_scheduler
import json


# API Validation Tab
validation_tab = gr.Interface(
    fn=lambda *args: json.dumps(validate_api_call(*args), indent=2),
    inputs=[
        gr.Textbox(
            label="MCP API Key", placeholder="Enter your MCP API key", type="password"
        ),
        gr.Textbox(
            label="Monitoring Name", placeholder="e.g., 'NVDA Stock Price'", value=""
        ),
        gr.Textbox(
            label="Description",
            placeholder="What are you monitoring?",
            value="",
            lines=2,
        ),
        gr.Radio(choices=["GET", "POST", "PUT", "DELETE"], label="Method", value="GET"),
        gr.Textbox(label="Base URL", placeholder="https://api.example.com", value=""),
        gr.Textbox(label="Endpoint", placeholder="endpoint/path", value=""),
        gr.Textbox(
            label="Parameter Key-Value Pairs",
            placeholder="Enter one parameter per line in format 'key: value'",
            value="",
        ),
        gr.Textbox(
            label="Header Key-Value Pairs",
            placeholder="Enter one header per line in format 'key: value'",
            value="",
        ),
        gr.Textbox(
            label="Additional Parameters (JSON)",
            placeholder="Enter any additional parameters as JSON",
            value="{}",
        ),
        gr.Number(
            label="Schedule Interval (minutes)", value=20, minimum=1, maximum=1440
        ),
        gr.Number(label="Stop After (hours)", value=24, minimum=1, maximum=168),
        gr.Textbox(
            label="Start Time (optional)",
            placeholder="YYYY-MM-DD HH:MM:SS or leave empty for immediate start",
            value="",
        ),
    ],
    outputs=gr.Textbox(label="Validation Result", lines=10),
    title="API Validation & Storage",
    description="STEP 1: Validate and test your API configuration. This tool tests the API call and stores the configuration if successful. If validation fails, retry with corrected parameters. If validation succeeds, proceed directly to 'Activate Scheduler' tab with the returned Config ID. Required for LLM tools that need to monitor external APIs periodically. Max monitoring period is 1 week (168 hours).",
    flagging_mode="manual",
    flagging_options=["Invalid Request", "API Error", "Config Issue", "Other"],
    examples=[
        [
            "test_mcp_key_123",
            "Dog Facts Monitor",
            "Monitor random dog facts from a free API",
            "GET",
            "https://dogapi.dog",
            "api/v2/facts",
            "",
            "",
            "{}",
            30,
            2,
            "",
        ],
        [
            "test_mcp_key_456",
            "XIVAPI Item Search",
            "Monitor FFXIV item data",
            "GET",
            "https://v2.xivapi.com/api",
            "search",
            'query: Name~"popoto"\nsheets: Item\nfields: Name,Description\nlanguage: en\nlimit: 1',
            "",
            "{}",
            60,
            4,
            "",
        ],
        [
            "test_mcp_key_789",
            "GitHub Issues Monitor",
            "Monitor TypeScript repository issues",
            "GET",
            "https://api.github.com",
            "repos/microsoft/TypeScript/issues",
            "state: open\nper_page: 5",
            "Accept: application/vnd.github.v3+json\nUser-Agent: MCP-Monitor",
            "{}",
            120,
            12,
            "",
        ],
    ],
)

# Scheduler Setup Tab
scheduler_tab = gr.Interface(
    fn=lambda *args: json.dumps(setup_scheduler(*args), indent=2),
    inputs=[
        gr.Number(label="Config ID (from validation step)", value=None),
        gr.Textbox(
            label="MCP API Key", placeholder="Enter your MCP API key", type="password"
        ),
    ],
    outputs=gr.Textbox(label="Scheduler Result", lines=8),
    title="Scheduler Setup",
    description="STEP 2: Activate periodic monitoring for a validated API configuration. PREREQUISITE: Must complete validation step first and obtain a Config ID. This tool sets up automated recurring API calls based on the validated configuration. Use the Config ID from the validation step output.",
    flagging_mode="manual",
    flagging_options=[
        "Config Not Found",
        "Invalid API Key",
        "Scheduler Error",
        "Other",
    ],
    examples=[
        [123456789, "test_mcp_key_123"],
        [987654321, "test_mcp_key_456"],
        [456789123, "test_mcp_key_789"],
    ],
)

# Create tabbed interface
demo = gr.TabbedInterface(
    [validation_tab, scheduler_tab],
    ["Validate & Store", "Activate Scheduler"],
    title="MCP API Monitoring System",
)

if __name__ == "__main__":
    demo.launch(mcp_server=True)
