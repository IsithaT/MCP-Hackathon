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

INSERT INTO api_configurations (
    mcp_api_key, name, description, method, base_url, endpoint,
    params, headers, additional_params,
    is_validated, is_active, stop, schedule_interval_minutes
) VALUES (
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
    TRUE,                              
    FALSE,                             
    20                                
);

INSERT INTO api_call_results (
    config_id, response_data, is_successful, error_message
) VALUES (
    1,
    '{"symbol":"NVDA", "price":1142.50, "timestamp":"2025-06-03T14:20:00Z"}',
    TRUE,
    NULL
);

INSERT INTO api_call_results (
    config_id, response_data, is_successful, error_message
) VALUES (
    1,
    NULL,
    FALSE,
    'Timeout while contacting the API'
);

select * from api_configurations;
select * from api_call_results;