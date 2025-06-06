import api_client
import json
from datetime import datetime, timedelta
import hashlib
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


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
        database="testdb",
        user="postgres",
        host="localhost",
        password=db_password,
        port=5432,
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


def retrieve_monitored_data(config_id, mcp_api_key):
    """
    TOOL: Retrieve monitored data for a specific API configuration.

    PURPOSE: Fetch the latest monitored data for a given configuration ID.
    This is STEP 3 of the monitoring setup process.

    PREREQUISITE: Must call validate_api_configuration() first and obtain a config_id from successful validation, then activate_monitoring() to start monitoring.

    This function can be called at any time after monitoring activation to retrieve the latest data collected by the monitoring system.

    Parameters:
    - config_id: The ID of the API configuration to retrieve data for (required)
    - mcp_api_key: User's MCP API key for verification (must match validation step)

    Input Examples:
    1. Retrieve data for stock monitoring:
        config_id: 123456789
        mcp_api_key: "your_mcp_key_here"

    2. Retrieve data for weather alerts:
        config_id: 987654321
        mcp_api_key: "your_mcp_key_here"

    Returns:
    - Dictionary with success status, data, and message
    - If no data found, returns success=False with appropriate message
    Example return:
    {
        "success": True,
        "data": [
            {"timestamp": "2025-06-04T12:00:00Z", "response": {...}},
            {"timestamp": "2025-06-04T12:20:00Z", "response": {...}},
        ],
        "message": "Data retrieved successfully for config_id 123456789"
    }
    - If config_id not found or invalid, returns success=False with error message
    - If mcp_api_key does not match, returns success=False with error message

    Example error return:
    {
        "success": False,
        "message": "Invalid config_id or mcp_api_key",
        "data": []
    }
    ERROR HANDLING: If config_id not found or invalid, returns success=False with error message
    """
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM api_configurations WHERE config_id = %s", (config_id,)
        )
        config = cur.fetchone()

        if not config:
            conn.close()
            return {
                "success": False,
                "message": "Invalid config_id",
                "data": [],
            }
        print(config)
        # 2. Query the api_configurations table for the given config_id
        # 3. If found, retrieve the associated monitored data
        # 4. Return the data in the specified format
        conn.close()
        return {
            "success": False,
            "message": "Function not implemented yet; this is a placeholder.",
            "data": [],
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
    print(response)
