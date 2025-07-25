import gradio as gr
import os
from api_monitor import (
    validate_api_configuration,
    activate_monitoring,
    retrieve_monitored_data,
)


def load_readme():
    """Load and return the README content."""
    try:
        readme_path = os.path.join(os.path.dirname(__file__), "README.md")
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Remove the YAML front matter for cleaner display
        if content.startswith("---"):
            lines = content.split("\n")
            yaml_end = -1
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == "---":
                    yaml_end = i
                    break
            if yaml_end > 0:
                content = "\n".join(lines[yaml_end + 1 :])
        return content
    except Exception as e:
        return f"Error loading README: {str(e)}"


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
            label="Schedule Interval (minutes)", value=20, minimum=0.1, maximum=1440
        ),
        gr.Number(
            label="Stop After (hours)", value=24, minimum=0.1, maximum=168, step=0.1
        ),
        gr.Textbox(
            label="Start Time (optional - leave empty for immediate start)",
            placeholder="Leave empty for immediate start, or enter YYYY-MM-DD HH:MM:SS for scheduled start",
            value="",
        ),
    ],
    outputs=gr.Textbox(label="Validation Result", lines=10),
    title="API Validation & Storage",
    description="STEP 1: Validate and test your API configuration. This tool tests the API call and stores the configuration if successful. If validation fails, retry with corrected parameters. If validation succeeds, proceed directly to 'Activate Scheduler' tab with the returned Config ID. Required for LLM tools that need to monitor external APIs periodically. Max monitoring period is 1 week (168 hours). Supports decimal hours (e.g., 0.5 for 30 minutes). If you don't have an MCP API key, get it here: https://mcp-hackathon.vercel.app/. To read more: go here https://huggingface.co/spaces/Agents-MCP-Hackathon/hermes/blob/main/README.md",
    flagging_mode="manual",
    flagging_options=["Invalid Request", "API Error", "Config Issue", "Other"],
    examples=[
        [
            "test_mcp_key_123",
            "FFXIV Wind-up Tonberry Price Monitor",
            "Monitor Wind-up Tonberry (ID: 6184) prices on Aether-Siren server every 30 minutes for one week",
            "GET",
            "https://universalis.app",
            "api/v2/Siren/6184",
            "listings: 1\nentries: 1\nfields: listings.pricePerUnit,listings.quantity,listings.worldName",
            "User-Agent: FFXIV-Price-Monitor/1.0",
            "{}",
            30,
            168,
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
            "state: open\nper_page: 1",
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

# README Tab - Static display only
with gr.Blocks() as readme_tab:
    gr.Markdown("# Documentation/Readme")

    gr.Markdown(load_readme())

# Create tabbed interface
demo = gr.TabbedInterface(
    [validation_tab, scheduler_tab, retrieve_tab, readme_tab],
    ["Validate & Store", "Activate Scheduler", "Retrieve Data", "Documentation/Readme"],
    title="Hermes - Automated Asynchronous REST API Monitoring",
)

if __name__ == "__main__":
    demo.launch(mcp_server=True)
