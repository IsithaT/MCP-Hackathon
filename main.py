import gradio as gr
from apiCall import api_call
from api_validator import validate_api_call, setup_scheduler


def format_validation_result(result):
    """Format validation result for display"""
    if result["success"]:
        return f"✅ Success!\n\nConfig ID: {result['config_id']}\nMessage: {result['message']}\n\nSample Response:\n{result.get('sample_response', 'No sample response')}"
    else:
        return f"❌ Failed!\n\nMessage: {result['message']}"


def format_scheduler_result(result):
    """Format scheduler result for display"""
    if result["success"]:
        return f"✅ Scheduler Active!\n\nConfig ID: {result['config_id']}\nMessage: {result['message']}\n\nSchedule Details:\n{result.get('schedule_interval_minutes', 'N/A')} minutes interval\nStops at: {result.get('stop_at', 'N/A')}"
    else:
        return f"❌ Scheduler Failed!\n\nMessage: {result['message']}"


# API Validation Tab
validation_tab = gr.Interface(
    fn=lambda *args: format_validation_result(validate_api_call(*args)),
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
)

# Scheduler Setup Tab
scheduler_tab = gr.Interface(
    fn=lambda *args: format_scheduler_result(setup_scheduler(*args)),
    inputs=[
        gr.Number(label="Config ID (from validation step)", value=None),
        gr.Textbox(
            label="MCP API Key", placeholder="Enter your MCP API key", type="password"
        ),
    ],
    outputs=gr.Textbox(label="Scheduler Result", lines=8),
    title="Scheduler Setup",
    description="STEP 2: Activate periodic monitoring for a validated API configuration. PREREQUISITE: Must complete validation step first and obtain a Config ID. This tool sets up automated recurring API calls based on the validated configuration. Use the Config ID from the validation step output.",
)

# Create tabbed interface
demo = gr.TabbedInterface(
    [validation_tab, scheduler_tab],
    ["Validate & Store", "Activate Scheduler"],
    title="MCP API Monitoring System",
)

if __name__ == "__main__":
    demo.launch(mcp_server=True)
