DROP TABLE IF EXISTS api_call_results;
DROP TABLE IF EXISTS api_configurations;

CREATE TABLE api_configurations (
    id SERIAL PRIMARY KEY,
    config_id INTEGER NOT NULL UNIQUE,
    mcp_api_key VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    method VARCHAR(10) NOT NULL DEFAULT 'GET',
    base_url VARCHAR(500) NOT NULL,
    endpoint VARCHAR(500),
    params JSONB,
    headers JSONB,
    additional_params JSONB,
    is_active BOOLEAN DEFAULT FALSE,
    schedule_interval_minutes DECIMAL(10,2),
    start_at TIMESTAMP,
    stop_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE api_call_results (
    id SERIAL PRIMARY KEY,
    config_id INTEGER REFERENCES api_configurations(config_id) ON DELETE CASCADE,
    response_data JSONB,
    is_successful BOOLEAN,
    error_message TEXT,
    called_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO api_configurations (
    config_id, mcp_api_key, name, description, method, base_url, endpoint,
    params, headers, additional_params,
    is_active, schedule_interval_minutes, start_at, stop_at
) VALUES (
	10101,
    'abc123xyz',            
    'Track NVDA Price',               
    'Tracking NVIDIA stock price every 20 minutes',
    'GET',
    'https://api.example.com',         
    '/stocks/nvda',                   
    '{"interval":"1d","range":"5d"}',  
    '{"Authorization":"Bearer token"}', 
    '{}',                               
    TRUE,                              
    20,
    '2025-06-04T12:00:00',
    '2025-06-11T12:00:00'
);

INSERT INTO api_call_results (
    config_id, response_data, is_successful, error_message
) VALUES (
    10101,
    '{"symbol":"NVDA", "price":1142.50, "timestamp":"2025-06-03T14:20:00Z"}',
    TRUE,
    NULL
);

INSERT INTO api_call_results (
    config_id, response_data, is_successful, error_message
) VALUES (
    10101,
    NULL,
    FALSE,
    'Timeout while contacting the API'
);

select * from api_configurations;
select * from api_call_results;