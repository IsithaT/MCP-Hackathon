import api_client
import json
from datetime import datetime, timedelta
import hashlib
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import requests

from apscheduler.schedulers.blocking import BlockingScheduler

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

    # Get database connection details from environment variables with defaults
    db_host = os.getenv("DB_HOST")
    db_port = int(os.getenv("DB_PORT"))
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")

    return psycopg2.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password,
        cursor_factory=psycopg2.extras.DictCursor,
    )


def verify_mcp_api_key(api_key):
    """
    Verify the MCP API key with the key generation server.

    Parameters:
    - api_key: The MCP API key to verify

    Returns:
    - Dictionary with success status and message
    """
    try:
        # Get the key server URL from environment or use default
        key_server_url = os.getenv("KEY_SERVER_URL")

        response = requests.post(
            f"{key_server_url}/api/verifyKey",
            json={"apiKey": api_key},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("valid"):
                return {"success": True, "message": "API key is valid"}
            else:
                return {"success": False, "message": "API key is invalid"}
        else:
            return {
                "success": False,
                "message": f"Key verification failed with status {response.status_code}",
            }

    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": f"Failed to connect to key verification service: {str(e)}",
        }
    except Exception as e:
        return {"success": False, "message": f"Key verification error: {str(e)}"}


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
    start_at,  # IMPORTANT: Use empty string "" for immediate start (most common case)
):
    """
    TOOL: Validate and store API configuration for monitoring.

    PURPOSE: Test an API endpoint and store the configuration if successful. This is STEP 1
    of the monitoring setup process. If validation fails, retry with corrected parameters.    If successful, use the returned config_id in activate_monitoring() function.

    CRITICAL: Even if success=True, you MUST manually check the 'sample_response' field
    before proceeding to activate_monitoring(). The API call may return success=True but contain
    error messages (like "401 Unauthorized", "Invalid API key", etc.) in the sample_response.

    CRITICAL: Always try to add parameters that will limit the API response to a manageable size.

    CRITICAL: Be sure to always clearly inform the user of the config_id after a desired validation result.

    CRITICAL: If you don't have an MCP API KEY given by the user, prompt them to get it here: https://mcp-hackathon.vercel.app/

    WORKFLOW:
    1. Call this function to validate API configuration
    2. If success=False: Fix parameters and retry this function
    3. If success=True: MANUALLY INSPECT the 'sample_response' field for errors
    4. If sample_response contains error messages: Fix API parameters and retry validation
    5. If sample_response looks valid: Use config_id in activate_monitoring() to activate monitoring

    ARGUMENTS:
    - mcp_api_key: MCP API key serves as user identifier.
    - name: User-friendly name for the monitoring task
    - description: Description of what is being monitored
    - method: HTTP method (GET, POST, PUT, DELETE)
    - base_url: The base URL of the API
    - endpoint: The specific API endpoint
    - param_keys_values: Parameter key-value pairs, one per line
    - header_keys_values: Header key-value pairs, one per line
    - additional_params: Optional JSON string for complex parameters
    - schedule_interval_minutes: Minutes between calls
    - stop_after_hours: Hours after which to stop (supports decimals, max 168 = 1 week)
    - start_at: Optional datetime string for when to start the monitoring.

    IMPORTANT: Leave as empty string "" for immediate start (most common use case, always default to this if no start time provided). Only provide a datetime string (e.g., "2024-06-15 09:00:00") if you need to schedule monitoring for a specific future time.

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
        stop_after_hours: 1.5
        start_at: ""

    2. Weather monitoring with free API:
        mcp_api_key: ""
        name: "Weather Monitor"
        description: "Monitor current weather conditions every 2 hours for one week using Open-Meteo free API"
        method: "GET"
        base_url: "https://api.open-meteo.com"
        endpoint: "v1/forecast"
        param_keys_values: "latitude: 40.7128\nlongitude: -74.0060\ncurrent: temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m\ntimezone: America/New_York"
        header_keys_values: "Content-Type: application/json"
        additional_params: "{}"
        schedule_interval_minutes: 120
        stop_after_hours: 168
        start_at: "2024-06-15 09:00:00"

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
        if not mcp_api_key or not mcp_api_key.strip() or mcp_api_key == "":
            mcp_api_key = os.getenv("MCP_API_KEY", "")
            if not mcp_api_key or not mcp_api_key.strip():
                return {
                    "success": False,
                    "message": "MCP API key is required",
                    "config_id": None,
                }

        # Verify the MCP API key with the key generation server
        key_verification = verify_mcp_api_key(mcp_api_key)
        if not key_verification["success"]:
            return {
                "success": False,
                "message": f"API key verification failed: {key_verification['message']}",
                "config_id": None,
            }

        # Validate required parameters
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
            or schedule_interval_minutes <= 0
            or schedule_interval_minutes > 1440
        ):
            return {
                "success": False,
                "message": "Schedule interval must be between 0 and 1440 minutes",
                "config_id": None,
            }

        if (
            not isinstance(stop_after_hours, (int, float))
            or stop_after_hours < 0.1
            or stop_after_hours > 168
        ):
            return {
                "success": False,
                "message": "Stop after hours must be between 0.1 and 168 hours (1 week max)",
                "config_id": None,
            }

        # Validate start_at if provided
        if start_at:
            try:
                parsed_start_time = datetime.fromisoformat(
                    start_at.replace("Z", "+00:00")
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

        # Generate unique config ID and calculate timestamps
        config_str = (
            f"{mcp_api_key}_{name}_{base_url}_{endpoint}_{datetime.now().timestamp()}"
        )
        config_id = int(hashlib.md5(config_str.encode()).hexdigest()[:7], 16)

        # Calculate timestamps
        created_at = datetime.now()
        stop_at = parsed_start_time + timedelta(hours=float(stop_after_hours))

        # Store configuration
        try:
            conn = connect_to_db()
            cur = conn.cursor()

            cur.execute(
                """
                INSERT INTO api_configurations (
                config_id, mcp_api_key, name, description, method,
                base_url, endpoint, params, headers, additional_params,
                is_active, schedule_interval_minutes, start_at, stop_at, created_at
                ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s
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
                    float(schedule_interval_minutes),
                    parsed_start_time,
                    stop_at.isoformat(),
                    created_at,
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
            "message": f"API call tested, validated, and stored successfully for '{name}'. Make sure to review the message manually before activating monitoring. Use this config_id in activate_monitoring() to activate monitoring.",
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


async def activate_monitoring(config_id, mcp_api_key):
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

    ARGUMENTS:
    - config_id: The ID from successful validate_api_configuration() execution (required)
    - mcp_api_key: User's MCP API key for verification (must match validation step).

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

    # need to extract
    """
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
    this
    """

    # Attempt to create the scheduler
    try:
        if not mcp_api_key or not mcp_api_key.strip() or mcp_api_key == "":
            mcp_api_key = os.getenv("MCP_API_KEY", "")
            if not mcp_api_key or not mcp_api_key.strip():
                return {
                    "success": False,
                    "message": "MCP API key is required",
                    "config_id": None,
                }

        # Verify the MCP API key with the key generation server first
        key_verification = verify_mcp_api_key(mcp_api_key)
        if not key_verification["success"]:
            return {
                "success": False,
                "message": f"API key verification failed: {key_verification['message']}",
                "config_id": config_id,
            }

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
                "config_id": config_id,
            }
        config = dict(config_row)
        if config["mcp_api_key"] != mcp_api_key:
            conn.close()
            return {
                "success": False,
                "message": "Invalid mcp_api_key. You are not authorized to activate this configuration.",
                "config_id": config_id,
            }  

        # Extract scheduling parameters
        name = config.get("name", "Unknown")
        schedule_interval_minutes = float(config.get("schedule_interval_minutes", 20))
        stop_at = config.get("stop_at")
        start_at = config.get("start_at")
        if not start_at:
            start_at = datetime.now()
        else:
            if not isinstance(start_at, datetime):
                start_at = datetime.fromisoformat(str(start_at))
        if not stop_at:
            stop_at = start_at + timedelta(hours=config.get("stop_after_hours", 24))
        else:
            if not isinstance(stop_at, datetime):
                stop_at = datetime.fromisoformat(
                    str(stop_at)
                )  

        # Job function to make actual API calls

        def api_monitoring_job():
            now = datetime.now()
            next_call = now + timedelta(minutes=schedule_interval_minutes)
            print(
                f"Executing API monitoring job for {name} at {now.isoformat()}. Next call at {next_call.isoformat()}"
            )

            try:
                # Extract API configuration parameters
                method = config.get("method", "GET")
                base_url = config.get("base_url")
                endpoint = config.get("endpoint", "")
                params = config.get("params", {})
                headers = config.get("headers", {})
                additional_params = config.get("additional_params", {})

                # Convert JSON strings back to dicts if needed
                if isinstance(params, str):
                    params = json.loads(params) if params else {}
                if isinstance(headers, str):
                    headers = json.loads(headers) if headers else {}
                if isinstance(additional_params, str):
                    additional_params = (
                        json.loads(additional_params) if additional_params else {}
                    )

                # Convert params and headers back to key-value string format for api_client
                param_keys_values = (
                    "\n".join([f"{k}: {v}" for k, v in params.items()])
                    if params
                    else ""
                )
                header_keys_values = (
                    "\n".join([f"{k}: {v}" for k, v in headers.items()])
                    if headers
                    else ""
                )
                additional_params_str = (
                    json.dumps(additional_params) if additional_params else "{}"
                )

                # Make the actual API call
                api_result = api_client.call_api(
                    method=method,
                    base_url=base_url,
                    endpoint=endpoint,
                    param_keys_values=param_keys_values,
                    header_keys_values=header_keys_values,
                    additional_params=additional_params_str,
                )

                # Determine if the call was successful
                is_successful = not (
                    isinstance(api_result, str) and api_result.startswith("Error")
                )
                error_message = api_result if not is_successful else None
                response_data = api_result if is_successful else None

                # Convert response to JSON if it's a string representation
                if is_successful and isinstance(response_data, str):
                    try:
                        if response_data.startswith("{") or response_data.startswith(
                            "["
                        ):
                            response_data = json.loads(response_data)
                    except json.JSONDecodeError:
                        # Keep as string if not valid JSON
                        pass

                job_conn = connect_to_db()
                job_cur = job_conn.cursor()

                # Mark config as active (only once, on first run)
                if not config["is_active"]:
                    job_cur.execute(
                        """
                        UPDATE api_configurations SET is_active = %s WHERE config_id = %s
                        """,
                        (True, config_id),
                    )
                    print(f"Marked configuration {config_id} as active.")

                # Check if this is the last call by comparing current time to stop_at
                current_time = datetime.now()
                next_call_time = current_time + timedelta(
                    minutes=schedule_interval_minutes
                )

                if next_call_time >= stop_at:
                    # This is the last call, mark as inactive
                    job_cur.execute(
                        """
                        UPDATE api_configurations SET is_active = %s WHERE config_id = %s
                        """,
                        (False, config_id),
                    )
                    print(
                        f"Last call for configuration {config_id}. Marked as inactive."
                    )

                # Insert the actual API call result
                job_cur.execute(
                    """
                    INSERT INTO api_call_results (
                        config_id, response_data, is_successful, error_message, called_at
                    ) VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        config_id,
                        (
                            json.dumps(response_data)
                            if response_data is not None
                            else None
                        ),
                        is_successful,
                        error_message,
                        now,
                    ),
                )
                job_conn.commit()
                job_cur.close()
                job_conn.close()

                print(
                    f"API call result for {name}: {'Success' if is_successful else 'Failed'}"
                )
                if not is_successful:
                    print(f"Error: {error_message}")

            except Exception as job_exc:
                print(f"API monitoring job error for {name}: {job_exc}")
                try:
                    job_conn = connect_to_db()
                    job_cur = job_conn.cursor()
                    job_cur.execute(
                        """
                        INSERT INTO api_call_results (
                            config_id, response_data, is_successful, error_message, called_at
                        ) VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            config_id,
                            None,
                            False,
                            f"Job execution error: {str(job_exc)}",
                            now,
                        ),
                    )
                    job_conn.commit()
                    job_cur.close()
                    job_conn.close()
                except Exception as db_exc:
                    print(
                        f"Failed to log error to database: {db_exc}"
                    )  

        # Setup AsyncIO scheduler

        scheduler = AsyncIOScheduler()
        # Schedule the API monitoring job
        scheduler.add_job(
            api_monitoring_job,
            "interval",
            minutes=schedule_interval_minutes,
            start_date=start_at,
            end_date=stop_at,
            id=f"monitor_{config_id}",
        )
        scheduler.start()
        # Mark config as active (only once, on first run)
        if not config["is_active"]:
            cur.execute(
                """
                UPDATE api_configurations SET is_active = %s WHERE config_id = %s
                """,
                (True, config_id),
            )
            print(f"Marked configuration {config_id} as active.")
        conn.close()
        return {
            "success": True,
            "message": f"Scheduler activated for '{name}'",
            "config_id": config_id,
            "schedule_interval_minutes": schedule_interval_minutes,
            "stop_at": stop_at.isoformat(),
            "next_call_at": (
                start_at + timedelta(minutes=schedule_interval_minutes)
            ).isoformat(),
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to create scheduler: {str(e)}",
            "config_id": config_id,
        }


def retrieve_monitored_data(config_id, mcp_api_key, mode="summary"):
    """
    TOOL: Retrieve monitored data for a specific API configuration.

    PURPOSE: Fetch the latest monitored data for a given configuration ID.
    This is STEP 3 of the monitoring setup process.

    PREREQUISITE: Must call validate_api_configuration() first and obtain a config_id from successful validation, then activate_monitoring() to start monitoring.

    This function can be called at any time after monitoring activation to retrieve the latest data collected by the monitoring system.

    ARGUMENTS:
    - config_id: The ID of the API configuration to retrieve data for (required)
    - mcp_api_key: User's MCP API key for verification (must match validation step).
    - mode: Data return mode - "summary" (LLM-optimized), "details" (full responses, minimal metadata), "full" (everything)

    Input Examples:
    1. Retrieve data for stock monitoring:
        config_id: 123456789
        mcp_api_key: "your_mcp_key_here"

    2. Retrieve data for weather alerts:
        config_id: 987654321
        mcp_api_key: "your_mcp_key_here"

    Returns:
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
                "response_preview": "{'alerts': [{'type': 'tornado'}]}..."  // truncated to 150 characters
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
        if not mcp_api_key or not mcp_api_key.strip() or mcp_api_key == "":
            mcp_api_key = os.getenv("MCP_API_KEY", "")
            if not mcp_api_key or not mcp_api_key.strip():
                return {
                    "success": False,
                    "message": "MCP API key is required",
                    "config_id": None,
                }
        # Verify the MCP API key with the key generation server first
        key_verification = verify_mcp_api_key(mcp_api_key)
        if not key_verification["success"]:
            return {
                "success": False,
                "message": f"API key verification failed: {key_verification['message']}",
                "data": [],
            }

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
        stop_at_time = config.get("stop_at")
        if stop_at_time:
            if hasattr(stop_at_time, "replace"):
                stop_at = stop_at_time
            else:
                stop_at = datetime.fromisoformat(
                    str(stop_at_time).replace("Z", "+00:00")
                )
            is_finished = now > stop_at
        else:
            is_finished = False

        # Calculate progress statistics
        total_expected_calls = 0
        if config.get("start_at") and config.get("schedule_interval_minutes"):
            start_time = config["start_at"]
            if hasattr(start_time, "replace"):
                start_dt = start_time
            else:
                start_dt = datetime.fromisoformat(str(start_time))

            elapsed_minutes = (now - start_dt).total_seconds() / 60
            if elapsed_minutes > 0:
                total_expected_calls = max(
                    1, int(elapsed_minutes / float(config["schedule_interval_minutes"]))
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
                    "start_at": (
                        config.get("start_at").isoformat()
                        if config.get("start_at")
                        else None
                    ),
                    "stop_at": (
                        config.get("stop_at").isoformat()
                        if config.get("stop_at")
                        else None
                    ),
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
                        ), 
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
                            str(item.get("response_data", ""))[:150] + "..."
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
