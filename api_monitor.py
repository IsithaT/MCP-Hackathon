import api_client
import json
from datetime import datetime, timedelta
import hashlib
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)


def connect_to_db():
    """
    Connect to the PostgreSQL database using environment variables.
    Returns a connection object.
    """
    db_password = os.getenv("DB_PASSWORD")
    if not db_password:
        raise ValueError(
            "Database password not found in environment variables. Please set DB_PASSWORD."
        )
    return psycopg2.connect(
        host="aws-0-us-west-1.pooler.supabase.com",
        port=6543,
        database="postgres",
        user="postgres.rivuplskngyevyzlshuh",
        host="aws-0-us-west-1.pooler.supabase.com",
        password=db_password,
        port=6543,
        cursor_factory=psycopg2.extras.DictCursor,
    )


def validate_api_configuration(
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
    time_to_start,
):
    """
    TOOL: Validate and store API configuration for monitoring.

    PURPOSE: Test an API endpoint and store the configuration if successful. This is STEP 1
    of the monitoring setup process. If validation fails, retry with corrected parameters.    If successful, use the returned config_id in activate_monitoring() function.

    CRITICAL: Even if success=True, you MUST manually check the 'sample_response' field
    before proceeding to activate_monitoring(). The API call may return success=True but contain
    error messages (like "401 Unauthorized", "Invalid API key", etc.) in the sample_response.

    WORKFLOW:
    1. Call this function to validate API configuration
    2. If success=False: Fix parameters and retry this function
    3. If success=True: MANUALLY INSPECT the 'sample_response' field for errors
    4. If sample_response contains error messages: Fix API parameters and retry validation
    5. If sample_response looks valid: Use config_id in activate_monitoring() to activate monitoring

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
    - time_to_start: When to start the monitoring (datetime string or None for immediate)

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
        time_to_start: ""

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
        time_to_start: "2024-06-15 09:00:00"

    Returns:
    - Dictionary with success status, config_id (needed for setup_scheduler), message, and sample_response

    Example return:
    {
        "success": True,
        "config_id": 123,
        "message": "API call tested and stored successfully",
        "sample_response": {...},
        "stop_at": "2025-06-11T12:00:00Z",
        "start_at": "2025-06-04T12:00:00Z"
    }

    NEXT STEP: If success=True, call activate_monitoring(config_id, mcp_api_key) to activate monitoring
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

        # Validate time_to_start if provided
        if time_to_start:
            try:
                parsed_start_time = datetime.fromisoformat(
                    time_to_start.replace("Z", "+00:00")
                )
                if parsed_start_time < datetime.now():
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
            parsed_start_time = datetime.now()  # Test the API call
        result = api_client.call_api(
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
        }

        # Generate unique config ID
        config_str = json.dumps(config_data, sort_keys=True) + str(
            datetime.now().timestamp()
        )
        config_id = int(hashlib.md5(config_str.encode()).hexdigest()[:7], 16)

        # Calculate timestamps
        created_at = datetime.now()
        stop_at = parsed_start_time + timedelta(hours=stop_after_hours)

        # Add metadata to config
        config_data.update(
            {
                "config_id": config_id,
                "created_at": created_at.isoformat(),
                "start_at": parsed_start_time.isoformat(),
                "stop_at": stop_at.isoformat(),
                # @JamezyKim This will be used to track the status of whether the api is confirmed or not
                "is_validated": False,
                "api_response": result,
            }
        )

        # Store configuration
        try:
            conn = connect_to_db()
            cur = conn.cursor()

            cur.execute(
                """
                INSERT INTO api_configurations (
                config_id, mcp_api_key, name, description, method,
                base_url, endpoint, params, headers, additional_params,
                is_validated, is_active, stop, schedule_interval_minutes,
                time_to_start, created_at, validated_at
                ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    config_id,
                    mcp_api_key,
                    name,
                    description,
                    method,
                    base_url,
                    endpoint,
                    json.dumps(api_client.parse_key_value_string(param_keys_values)),
                    json.dumps(api_client.parse_key_value_string(header_keys_values)),
                    additional_params,
                    False,
                    False,
                    False,
                    schedule_interval_minutes,
                    parsed_start_time,
                    created_at,
                    None,
                ),
            )

            conn.commit()
            cur.execute("SELECT * FROM api_configurations WHERE id = %s", (config_id,))
            rows = cur.fetchall()
            for row in rows:
                print(row)

            conn.close()
            cur.close()

        except Exception as db_error:
            return {
                "success": False,
                "message": f"Database error: {str(db_error)}",
                "config_id": None,
            }

        # Return success response
        return {
            "success": True,
            "config_id": config_id,
            "message": f"API call tested and stored successfully for '{name}'. Use this config_id in activate_monitoring() to activate monitoring.",
            "sample_response": (
                json.loads(result)
                if result.startswith("{") or result.startswith("[")
                else result
            ),
            "start_at": parsed_start_time.isoformat(),
            "stop_at": stop_at.isoformat(),
            "schedule_interval_minutes": schedule_interval_minutes,
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Validation failed with error: {str(e)}",
            "config_id": None,
        }


def activate_monitoring(config_id, mcp_api_key):
    """
    TOOL: Activate periodic monitoring for a validated API configuration.

    PURPOSE: Start automated recurring API calls based on a previously validated configuration.
    This is STEP 2 of the monitoring setup process.

    PREREQUISITE: Must call validate_api_configuration() first and obtain a config_id from successful validation. Make sure that the sample_response is what you expect
    to see before proceeding with this function.

    WORKFLOW:
    1. First call validate_api_configuration() to get config_id
    2. If validation successful, call this function with the config_id
    3. Monitoring will run automatically according to the validated schedule

    Parameters:
    - config_id: The ID from successful validate_api_configuration() execution (required)
    - mcp_api_key: User's MCP API key for verification (must match validation step)

    Input Examples:

    1. Activate scheduler for stock monitoring:
        config_id: 123456789
        mcp_api_key: "your_mcp_key_here"

    2. Activate scheduler for weather alerts:
        config_id: 987654321
        mcp_api_key: "your_mcp_key_here"

    NOTE: The config_id must be obtained from a successful validate_api_configuration() response.
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
    try:
        conn = connect_to_db()
        # TODO: Implement activation logic here
        conn.close()

        return {
            "success": False,
            "message": "Function not implemented yet; this is a placeholder.",
            "config_id": config_id,
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Database connection failed: {str(e)}",
            "config_id": config_id,
        }


def retrieve_monitored_data(config_id, mcp_api_key, mode="summary"):
    """
    TOOL: Retrieve monitored data for a specific API configuration.

    PURPOSE: Fetch the latest monitored data for a given configuration ID.
    This is STEP 3 of the monitoring setup process.

    PREREQUISITE: Must call validate_api_configuration() first and obtain a config_id from successful validation, then activate_monitoring() to start monitoring.

    This function can be called at any time after monitoring activation to retrieve the latest data collected by the monitoring system.    Parameters:
    - config_id: The ID of the API configuration to retrieve data for (required)
    - mcp_api_key: User's MCP API key for verification (must match validation step)
    - mode: Data return mode - "summary" (LLM-optimized), "details" (full responses, minimal metadata), "full" (everything)

    Input Examples:
    1. Retrieve data for stock monitoring:
        config_id: 123456789
        mcp_api_key: "your_mcp_key_here"

    2. Retrieve data for weather alerts:
        config_id: 987654321
        mcp_api_key: "your_mcp_key_here"    Returns:
    - Dictionary with monitoring status in one of three formats based on mode parameter

    SUMMARY mode (LLM-optimized, default):
    {
        "success": True,
        "config_name": "Weather Alert Monitor",
        "summary": {
            "status": "active",  // "active", "inactive"
            "health": "good",    // "good", "degraded", "no_data"
            "calls_made": 15,
            "success_rate": 93.3,
            "last_call": "2025-06-05T15:20:00",
            "last_success": "2025-06-05T15:20:00"
        },
        "recent_calls": [
            {
                "timestamp": "2025-06-05T15:20:00",
                "success": true,
                "error": null,
                "response_preview": "{'alerts': [{'type': 'tornado'}]}..."  // truncated
            }
            // ... up to 5 most recent calls
        ],
        "full_data_available": 15,
        "monitoring_details": {
            "interval_minutes": 20,
            "is_finished": false
        }
    }

    DETAILS mode (full responses, minimal metadata):
    {
        "success": True,
        "config_name": "Weather Alert Monitor",
        "status": "active",
        "calls_made": 15,
        "success_rate": 93.3,
        "recent_responses": [
            {
                "timestamp": "2025-06-05T15:20:00",
                "success": true,
                "response_data": {...},  // full response data
                "error": null
            }
            // ... up to 10 most recent calls with full responses
        ]
    }

    FULL mode (everything):
    {
        "success": True,
        "config_name": "Weather Alert Monitor",
        "config_description": "Monitor severe weather alerts",
        "is_active": True,
        "is_finished": False,
        "progress": {...},
        "schedule_info": {...},
        "data": [...]  // all historical data
    }

    Error return format:
    {
        "success": False,
        "message": "Invalid config_id or mcp_api_key"
    }
    ERROR HANDLING: If config_id not found or invalid, returns success=False with error message
    """
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM api_configurations WHERE config_id = %s", (config_id,)
        )
        config_row = cur.fetchone()

        if not config_row:
            conn.close()
            return {
                "success": False,
                "message": "Invalid config_id",
                "data": [],
            }

        config = dict(config_row)
        print(f"Retrieved config: {config}")

        if config["mcp_api_key"] != mcp_api_key:
            conn.close()
            return {
                "success": False,
                "message": "Invalid mcp_api_key. You are not authorized to access this configuration.",
                "data": [],
            }

        # Query the api_call_results table for monitored data
        cur.execute(
            "SELECT * FROM api_call_results WHERE config_id = %s ORDER BY called_at DESC",
            (config_id,),
        )
        monitored_data_rows = cur.fetchall()

        # Convert rows to dictionaries and format timestamps
        monitored_data = []
        for row in monitored_data_rows:
            row_dict = dict(row)
            # Format the timestamp for better readability
            if row_dict.get("called_at"):
                row_dict["called_at"] = row_dict["called_at"].isoformat()
            monitored_data.append(row_dict)

        # Check if monitoring is finished
        now = datetime.now()
        stop_time = config.get("time_to_start")
        if stop_time and config.get("schedule_interval_minutes"):
            # Calculate when monitoring should stop
            stop_after_hours = (
                config.get("schedule_interval_minutes", 24) / 60 * 24
            )  # Default fallback
            if hasattr(stop_time, "replace"):
                stop_at = stop_time + timedelta(hours=stop_after_hours)
            else:
                stop_at = datetime.fromisoformat(str(stop_time)) + timedelta(
                    hours=stop_after_hours
                )
            is_finished = now > stop_at or config.get("stop", False)
        else:
            is_finished = config.get("stop", False)

        # Calculate progress statistics
        total_expected_calls = 0
        if config.get("time_to_start") and config.get("schedule_interval_minutes"):
            start_time = config["time_to_start"]
            if hasattr(start_time, "replace"):
                start_dt = start_time
            else:
                start_dt = datetime.fromisoformat(str(start_time))

            elapsed_minutes = (now - start_dt).total_seconds() / 60
            if elapsed_minutes > 0:
                total_expected_calls = max(
                    1, int(elapsed_minutes / config["schedule_interval_minutes"])
                )

        # Get success/failure counts
        successful_calls = len(
            [d for d in monitored_data if d.get("is_successful", False)]
        )
        failed_calls = len(
            [d for d in monitored_data if not d.get("is_successful", True)]
        )
        total_calls = len(
            monitored_data
        )  # Create simplified summary for LLM consumption
        summary = {
            "status": (
                "active"
                if config.get("is_active", False) and not is_finished
                else "inactive"
            ),
            "health": (
                "good"
                if total_calls > 0 and (successful_calls / total_calls) > 0.8
                else "degraded" if total_calls > 0 else "no_data"
            ),
            "calls_made": total_calls,
            "success_rate": (
                round(successful_calls / total_calls * 100, 1) if total_calls > 0 else 0
            ),
            "last_call": monitored_data[0]["called_at"] if monitored_data else None,
            "last_success": next(
                (d["called_at"] for d in monitored_data if d.get("is_successful")), None
            ),
        }

        # Handle different return modes
        if mode == "full":
            # Return complete detailed data (original detailed format)
            return {
                "success": True,
                "message": f"Full data retrieved for config_id {config_id}",
                "config_name": config.get("name", "Unknown"),
                "config_description": config.get("description", ""),
                "is_active": config.get("is_active", False),
                "is_finished": is_finished,
                "progress": {
                    "total_calls": total_calls,
                    "successful_calls": successful_calls,
                    "failed_calls": failed_calls,
                    "expected_calls": total_expected_calls,
                    "success_rate": (
                        round(successful_calls / total_calls * 100, 2)
                        if total_calls > 0
                        else 0
                    ),
                },
                "schedule_info": {
                    "interval_minutes": config.get("schedule_interval_minutes"),
                    "started_at": (
                        config.get("time_to_start").isoformat()
                        if config.get("time_to_start")
                        else None
                    ),
                    "is_stopped": config.get("stop", False),
                },
                "data": monitored_data,
            }

        elif mode == "details":
            # Return full response data but minimal metadata (up to 10 recent calls)
            recent_responses = []
            for item in monitored_data[:10]:  # Last 10 calls with full responses
                recent_responses.append(
                    {
                        "timestamp": item["called_at"],
                        "success": item.get("is_successful", False),
                        "response_data": item.get(
                            "response_data"
                        ),  # Full response data
                        "error": (
                            item.get("error_message")
                            if not item.get("is_successful")
                            else None
                        ),
                    }
                )

            return {
                "success": True,
                "config_name": config.get("name", "Unknown"),
                "status": summary["status"],
                "calls_made": total_calls,
                "success_rate": summary["success_rate"],
                "recent_responses": recent_responses,
            }

        else:  # mode == "summary" (default)
            # Get recent data (last 5 calls) with essential info only
            recent_data = []
            for item in monitored_data[:5]:  # Only last 5 calls
                recent_data.append(
                    {
                        "timestamp": item["called_at"],
                        "success": item.get("is_successful", False),
                        "error": (
                            item.get("error_message")
                            if not item.get("is_successful")
                            else None
                        ),
                        "response_preview": (
                            str(item.get("response_data", ""))[:100] + "..."
                            if item.get("response_data")
                            else None
                        ),
                    }
                )

            return {
                "success": True,
                "config_name": config.get("name", "Unknown"),
                "summary": summary,
                "recent_calls": recent_data,
                "full_data_available": len(monitored_data),
                "monitoring_details": {
                    "interval_minutes": config.get("schedule_interval_minutes"),
                    "is_finished": is_finished,
                },
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Database connection failed: {str(e)}",
            "data": [],
        }


## testing
if __name__ == "__main__":
    validation_response = validate_api_configuration(
        mcp_api_key="your_api_key",
        name="Dog Facts API",
        description="Monitor random dog facts from a free API",
        method="GET",
        base_url="https://dogapi.dog",
        endpoint="api/v2/facts",
        param_keys_values="",
        header_keys_values="",
        additional_params="{}",
        schedule_interval_minutes=20,
        stop_after_hours=24,
        time_to_start="",
    )
    print(validation_response)
    print()
    print()

    activate_monitoring_response = activate_monitoring(
        config_id=validation_response.get("config_id"),
        mcp_api_key="your_api_key",
    )
    print(activate_monitoring_response)
    print()
    print()

    response = retrieve_monitored_data(
        config_id=activate_monitoring_response.get("config_id"),
        mcp_api_key="your_api_key",
    )
    print(json.dumps(response, indent=2, default=str))
