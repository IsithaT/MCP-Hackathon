import apiCall
import json
import os
from datetime import datetime, timedelta
import hashlib


def validate_api_call(
    mcp_api_key,
    name,
    description,
    method,
    base_url,
    endpoint,
    param_keys_values,
    header_keys_values,
    additional_params,
    schedule_interval_minutes,
    stop_after_hours,
    start_time,
):
    """
    TOOL: Validate and store API configuration for monitoring.

    PURPOSE: Test an API endpoint and store the configuration if successful. This is STEP 1
    of the monitoring setup process. If validation fails, retry with corrected parameters.
    If successful, use the returned config_id in setup_scheduler() function.

    WORKFLOW:
    1. Call this function to validate API configuration
    2. If success=False: Fix parameters and retry this function
    3. If success=True: Use config_id in setup_scheduler() to activate monitoring

    Parameters:
    - mcp_api_key: MCP API key serves as user identifier
    - name: User-friendly name for the monitoring task
    - description: Description of what is being monitored
    - method: HTTP method (GET, POST, PUT, DELETE)
    - base_url: The base URL of the API
    - endpoint: The specific API endpoint
    - param_keys_values: Parameter key-value pairs, one per line
    - header_keys_values: Header key-value pairs, one per line
    - additional_params: Optional JSON string for complex parameters
    - schedule_interval_minutes: Minutes between calls
    - stop_after_hours: Hours after which to stop (max 168 = 1 week)
    - start_time: When to start the monitoring (datetime string or None for immediate)

    Input Examples:

    1. Simple GET request to monitor stock price:
        mcp_api_key: "your_mcp_key_here"
        name: "NVDA Stock Price"
        description: "Monitor NVIDIA stock price every 30 minutes"
        method: "GET"
        base_url: "https://api.example.com"
        endpoint: "stocks/NVDA"
        param_keys_values: "symbol: NVDA\ninterval: 1min"
        header_keys_values: "Authorization: Bearer your_token"
        additional_params: "{}"
        schedule_interval_minutes: 30
        stop_after_hours: 24
        start_time: ""

    2. API with complex parameters:
        mcp_api_key: "your_mcp_key_here"
        name: "Weather Alert Monitor"
        description: "Monitor severe weather alerts"
        method: "POST"
        base_url: "https://api.weather.com"
        endpoint: "alerts"
        param_keys_values: "lat: 40.7128\nlon: -74.0060"
        header_keys_values: "X-API-Key: weather_key\nContent-Type: application/json"
        additional_params: '{"severity": ["severe", "extreme"], "types": ["tornado", "hurricane"]}'
        schedule_interval_minutes: 15
        stop_after_hours: 48
        start_time: "2024-06-15 09:00:00"

    3. GitHub API monitoring:
        mcp_api_key: "your_mcp_key_here"
        name: "Repo Issues Monitor"
        description: "Monitor new issues in repository"
        method: "GET"
        base_url: "https://api.github.com"
        endpoint: "repos/microsoft/TypeScript/issues"
        param_keys_values: "state: open\nper_page: 10"
        header_keys_values: "Accept: application/vnd.github.v3+json\nUser-Agent: MyApp"
        additional_params: "{}"
        schedule_interval_minutes: 60
        stop_after_hours: 168
        start_time: ""

    Returns:
    - Dictionary with success status, config_id (needed for setup_scheduler), message, and sample_response

    Example return:
    {
        "success": True,
        "config_id": 123,
        "message": "API call validated and stored successfully",
        "sample_response": {...},
        "stop_at": "2025-06-11T12:00:00Z",
        "start_at": "2025-06-04T12:00:00Z"
    }

    NEXT STEP: If success=True, call setup_scheduler(config_id, mcp_api_key) to activate monitoring
    """
    try:
        # Validate input parameters
        if not mcp_api_key or not mcp_api_key.strip():
            return {
                "success": False,
                "message": "MCP API key is required",
                "config_id": None,
            }

        if not name or not name.strip():
            return {
                "success": False,
                "message": "Monitoring name is required",
                "config_id": None,
            }

        if not base_url or not base_url.strip():
            return {
                "success": False,
                "message": "Base URL is required",
                "config_id": None,
            }

        if not method or method not in ["GET", "POST", "PUT", "DELETE"]:
            return {
                "success": False,
                "message": "Valid HTTP method is required (GET, POST, PUT, DELETE)",
                "config_id": None,
            }

        if (
            not isinstance(schedule_interval_minutes, (int, float))
            or schedule_interval_minutes < 1
            or schedule_interval_minutes > 1440
        ):
            return {
                "success": False,
                "message": "Schedule interval must be between 1 and 1440 minutes",
                "config_id": None,
            }

        if (
            not isinstance(stop_after_hours, (int, float))
            or stop_after_hours < 1
            or stop_after_hours > 168
        ):
            return {
                "success": False,
                "message": "Stop after hours must be between 1 and 168 hours (1 week max)",
                "config_id": None,
            }

        # Validate start_time if provided
        if start_time:
            try:
                start_datetime = datetime.fromisoformat(
                    start_time.replace("Z", "+00:00")
                )
                if start_datetime < datetime.now():
                    return {
                        "success": False,
                        "message": "Start time cannot be in the past",
                        "config_id": None,
                    }
            except ValueError:
                return {
                    "success": False,
                    "message": "Invalid start time format",
                    "config_id": None,
                }
        else:
            start_datetime = datetime.now()

        # Test the API call
        result = apiCall.api_call(
            method=method,
            base_url=base_url,
            endpoint=endpoint,
            param_keys_values=param_keys_values,
            header_keys_values=header_keys_values,
            additional_params=additional_params,
        )

        # Check if the API call failed
        if isinstance(result, str) and result.startswith("Error"):
            return {
                "success": False,
                "message": f"API call test failed: {result}",
                "config_id": None,
            }

        # Generate config ID and calculate timestamps
        config_data = {
            "mcp_api_key": mcp_api_key,
            "name": name,
            "description": description,
            "method": method,
            "base_url": base_url,
            "endpoint": endpoint,
            "param_keys_values": param_keys_values,
            "header_keys_values": header_keys_values,
            "additional_params": additional_params,
            "schedule_interval_minutes": schedule_interval_minutes,
            "stop_after_hours": stop_after_hours,
            "start_time": start_time,
        }

        # Generate unique config ID
        config_str = json.dumps(config_data, sort_keys=True)
        config_id = int(hashlib.md5(config_str.encode()).hexdigest()[:8], 16)

        # Calculate timestamps
        created_at = datetime.now()
        stop_at = start_datetime + timedelta(hours=stop_after_hours)

        # Add metadata to config
        config_data.update(
            {
                "config_id": config_id,
                "created_at": created_at.isoformat(),
                "start_at": start_datetime.isoformat(),
                "stop_at": stop_at.isoformat(),
                # @JamezyKim This will be used to track the status of whether the api is confirmed or not
                "is_validated": False,
                "sample_response": result,
            }
        )

        # Store configuration
        # TODO: Implement database

        # Return success response
        return {
            "success": True,
            "config_id": config_id,
            "message": f"API call validated and stored successfully for '{name}'",
            "sample_response": result,
            "start_at": start_datetime.isoformat(),
            "stop_at": stop_at.isoformat(),
            "schedule_interval_minutes": schedule_interval_minutes,
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Validation failed with error: {str(e)}",
            "config_id": None,
        }


def setup_scheduler(config_id, mcp_api_key):
    """
    TOOL: Activate periodic monitoring for a validated API configuration.

    PURPOSE: Start automated recurring API calls based on a previously validated configuration.
    This is STEP 2 of the monitoring setup process.

    PREREQUISITE: Must call validate_api_call() first and obtain a config_id from successful validation.

    WORKFLOW:
    1. First call validate_api_call() to get config_id
    2. If validation successful, call this function with the config_id
    3. Monitoring will run automatically according to the validated schedule

    Parameters:
    - config_id: The ID from successful validate_api_call() execution (required)
    - mcp_api_key: User's MCP API key for verification (must match validation step)

    Input Examples:

    1. Activate scheduler for stock monitoring:
        config_id: 123456789
        mcp_api_key: "your_mcp_key_here"

    2. Activate scheduler for weather alerts:
        config_id: 987654321
        mcp_api_key: "your_mcp_key_here"

    3. Activate scheduler for GitHub issues:
        config_id: 456789123
        mcp_api_key: "your_mcp_key_here"

    NOTE: The config_id must be obtained from a successful validate_api_call() response.
    The mcp_api_key must match the one used during validation.

    Returns:
    - Dictionary with success status and scheduling details

    Example return:
    {
        "success": True,
        "message": "Scheduler activated for 'NVDA Stock Price'",
        "config_id": 123,
        "schedule_interval_minutes": 20,
        "stop_at": "2025-06-11T12:00:00Z",
        "next_call_at": "2025-06-04T12:20:00Z"
    }

    ERROR HANDLING: If config_id not found or invalid, returns success=False with error message
    """

    return {
        "success": False,
        "message": "Function not implemented yet; this is a placeholder.",
        "config_id": config_id,
    }


if __name__ == "__main__":
    # Example usage
    response = validate_api_call(
        mcp_api_key="your_api_key",
        name="NVDA Stock Price",
        description="Monitor the stock price of NVIDIA",
        method="GET",
        base_url="https://api.example.com",
        endpoint="stocks/NVDA",
        param_keys_values="",
        header_keys_values="",
        additional_params="{}",
        schedule_interval_minutes=20,
        stop_after_hours=24,
        start_time=None,
    )
    print(response)
