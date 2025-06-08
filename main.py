import gradio as gr
from api_monitor import (
    validate_api_configuration,
    activate_monitoring,
    retrieve_monitored_data,
)


# API Validation Tab
validation_tab = gr.Interface(
    fn=validate_api_configuration,
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
        gr.Number(
            label="Stop After (hours)", value=24, minimum=0.1, maximum=168, step=0.1
        ),
        gr.Textbox(
            label="Start Time (optional)",
            placeholder="YYYY-MM-DD HH:MM:SS or leave empty for immediate start",
            value="",
        ),
    ],
    outputs=gr.Textbox(label="Validation Result", lines=10),
    title="API Validation & Storage",
    description="STEP 1: Validate and test your API configuration. This tool tests the API call and stores the configuration if successful. If validation fails, retry with corrected parameters. If validation succeeds, proceed directly to 'Activate Scheduler' tab with the returned Config ID. Required for LLM tools that need to monitor external APIs periodically. Max monitoring period is 1 week (168 hours). Supports decimal hours (e.g., 0.5 for 30 minutes).",
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
            1.5,
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
            0.5,
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
            2.25,
            "",
        ],
    ],
)

# Scheduler Setup Tab
scheduler_tab = gr.Interface(
    fn=activate_monitoring,
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

# Retrieve Data Tab
retrieve_tab = gr.Interface(
    fn=retrieve_monitored_data,
    inputs=[
        gr.Number(label="Config ID", value=None),
        gr.Textbox(
            label="MCP API Key", placeholder="Enter your MCP API key", type="password"
        ),
        gr.Dropdown(
            choices=["summary", "details", "full"],
            label="Data Mode",
            value="summary",
            info="summary: LLM-optimized | details: full responses, minimal metadata | full: everything",
        ),
    ],
    outputs=gr.JSON(label="Monitoring Progress & Data"),
    title="Retrieve Monitoring Data",
    description="STEP 3: Check the progress and retrieve data from your active monitoring configurations. Use the Config ID from the validation step. Three modes: 'summary' (LLM-optimized), 'details' (full responses), 'full' (complete debug info).",
    flagging_mode="manual",
    flagging_options=[
        "Config Not Found",
        "Invalid API Key",
        "No Data Available",
        "Other",
    ],
    examples=[
        [123456789, "test_mcp_key_123", "summary"],
        [987654321, "test_mcp_key_456", "details"],
        [456789123, "test_mcp_key_789", "full"],
    ],
)

# Create tabbed interface
demo = gr.TabbedInterface(
    [validation_tab, scheduler_tab, retrieve_tab],
    ["Validate & Store", "Activate Scheduler", "Retrieve Data"],
    title="MCP API Monitoring System",
)

if __name__ == "__main__":
    demo.launch(mcp_server=True)
