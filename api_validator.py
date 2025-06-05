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
    Validate API call parameters and store successful configuration.

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

    Returns:
    - Dictionary with success status, config_id, message, and sample_response

    Example return:
    {
        "success": True,
        "config_id": 123,
        "message": "API call validated and stored successfully",
        "sample_response": {...},
        "stop_at": "2025-06-11T12:00:00Z",
        "start_at": "2025-06-04T12:00:00Z"
    }
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
    Set up periodic calling for a validated API configuration.

    Parameters:
    - config_id: The ID from validated configuration
    - mcp_api_key: User's MCP API key for verification

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
    """

    return {
        "success": False,
        "message": "Function not implemented yet",
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
