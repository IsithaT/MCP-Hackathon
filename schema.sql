DROP TABLE IF EXISTS api_call_results;
DROP TABLE IF EXISTS api_configurations;

CREATE TABLE api_configurations (
    id SERIAL PRIMARY KEY,
    mcp_api_key VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    method VARCHAR(10) NOT NULL DEFAULT 'GET',
    base_url VARCHAR(500) NOT NULL,
    endpoint VARCHAR(500),
    params JSONB,
    headers JSONB,
    additional_params JSONB,
    is_validated BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT FALSE,
    stop BOOLEAN DEFAULT FALSE,
    schedule_interval_minutes INTEGER,
	time_to_start TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    validated_at TIMESTAMP
);

CREATE TABLE api_call_results (
    id SERIAL PRIMARY KEY,
    config_id INTEGER REFERENCES api_configurations(id) ON DELETE CASCADE,
    response_data JSONB,
    is_successful BOOLEAN,
    error_message TEXT,
    called_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);