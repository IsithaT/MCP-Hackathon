---
title: Hermes - Automated Asynchronous REST API Monitoring
short_description: Input any API configuration and monitor responses over time.
sdk: gradio
sdk_version: "5.33.0"
emoji: 🪽
colorFrom: red
colorTo: yellow
license: mit
pinned: true
tags:
  - Agents-MCP-Hackathon
  - mcp-server-track
---

# Hermes - Automated Asynchronous REST API Monitoring

## Built By:

Isitha Tennakoon - IsithaT
Coleman Lai - Googolplexic
William Chen - potatooine
James Kim - JamesyKim


## Link to demo video: (placeholder for video link)

## MCP API Key Generation link: [Generate MCP API Key](https://mcp-hackathon.vercel.app/main)

Hermes is a tool designed to automate the monitoring of REST API endpoints. It allows users to input their API configurations and monitor the responses over time, allowing for both data collection/tracking and API performance analysis.

## What does it do?

This is meant to be an MCP tool, which means that it can be used by agents (like Claude) to monitor APIs (It can be used by humans too, especially to view the data, but it is primarily designed for agents). It allows users to input any API configuration and monitor the responses over time. The tool can validate the API configuration, activate monitoring, and retrieve monitored data in different formats (summary, details, or full). This makes it easy to track API performance and analyze the data collected.

## Who are we? Why did we build this?

We're a team of 4 late-second/early-third-year CS students. This hackathon was most of us's first time working with a lot of the technologies we used, such as database management, servers, and hosting. We decided to build Hermes since a lot of us realized that there wasn't really a good way to monitor APIs, at least not without a lot of manual work. We wanted to build a tool that would allow users to easily do this, no matter what it may be used for. We also wanted to build something that would allow us to learn more about the technologies we were using, and we definitely did that!

## How does it work?

Hermes requires users to generate an MCP API key, which you can do right [here at this link](https://mcp-hackathon.vercel.app/main). Once you have your API key, you (or an agent etc. Claude), can perform the following steps:

1. **Validate API Configuration**: Use the `validate_api_configuration` function to check if your API configuration is valid. If the request fails, it will return the error. Else, it will save the configuration to the database and return a success message with `config_id`. The user/agent can then decide whether to proceed with monitoring based on the response (etc. can reject the API configuration if it doesn't show the desired data content).
2. **Activate Monitoring**: Use the `activate_monitoring` function with the `config_id` from the previous step to start monitoring the API. This will set up a background task that will periodically check the API and store the responses.
3. **Retrieve Monitored Data**: Use the `retrieve_monitored_data` function with the `config_id` to retrieve the monitoring data. You can specify the mode of data retrieval (summary, details, or full) to get the desired level of information. This can be called anytime after monitoring is activated.

### ⚠️ Important! ⚠️

Call results and configurations will be deleted 14 days after the last call to the API. This is to ensure that the database does not get too large and to protect user privacy.

## 📋 Complete Workflow Process

### Prerequisites

- **Get your MCP API Key**: Visit [https://mcp-hackathon.vercel.app/main](https://mcp-hackathon.vercel.app/main) to generate your unique API key
- **Have your API details ready**: Know the endpoint you want to monitor, required parameters, headers, and authentication

### Step-by-Step Process (For Humans)

#### **Step 1: Validate & Configure**

Use the `validate_api_configuration` function to:

- Test your API endpoint to ensure it works
- Verify the response contains the data you expect
- Store the configuration if validation passes

**What you need:**

- Your MCP API key
- API details (URL, method, parameters, headers)
- Monitoring schedule (how often to check, for how long)

**What you get:**

- A `config_id` (save this - you'll need it for the next steps!)
- Sample response to verify the data is what you expect
- Confirmation that your API configuration is valid

#### **Step 2: Activate Monitoring**

Use the `activate_monitoring` function to:

- Start the automated monitoring process
- Begin collecting data at your specified intervals

**What you need:**

- The `config_id` from Step 1
- Your MCP API key

**What happens:**

- Background monitoring starts immediately (or at your scheduled time)
- API calls are made automatically at your specified intervals
- All responses are stored in the database

#### **Step 3: Retrieve Data**

Use the `retrieve_monitored_data` function to:

- Check monitoring status and progress
- Get collected data in your preferred format

**What you need:**

- The `config_id` from Step 1
- Your MCP API key
- Data mode preference:
  - `summary`: Quick overview with recent results (best for LLMs)
  - `details`: Full API responses with minimal metadata
  - `full`: Complete data including all metadata and debug info

### Example Workflow

```md
1. You want to monitor a weather API every 30 minutes for 2 hours
   ↓
2. Call validate_api_configuration() with your weather API details
   → Returns: config_id = 123456
   ↓
3. Review the sample response - looks good!
   ↓
4. Call activate_monitoring(config_id=123456, mcp_api_key="your_key")
   → Monitoring starts immediately
   ↓
5. Wait for data collection (or check progress anytime)
   ↓
6. Call retrieve_monitored_data(config_id=123456, mode="summary")
   → Get your weather monitoring results!
```

## Problems we ran into

Since (free) Gradio is stateless, we had to find a way to pass down information between both the different API calls and the user calls, while still ensuring privacy. We ended up using the MCP API key as a user identifier, which allowed us to separate user data while still being able to access it when needed.

There was also the problem of having to validate the data and making sure that the user/agent is satisfied with the data before activating monitoring. We solved this by separating the whole process into multiple functions, which allowed us to validate the data before activating monitoring.

Another problem we ran into was finding a way to pass the MCP API key automatically to the API calls without having to manually input it every time. We were unavble to find a way to do this, as the server is remote and we couldn't upload an environment variable to the server.

## Future Steps

Currently, the API call results store the entire response, which can be quite large, especially for LLMs like Claude to handle (or reach conversation limits), hence the need for three different returns for monitored data. In the future, we think that we can improve this by allowing users to specify a format for the response, such as only storing the text content or a specific field in the response. This would allow users to save space and make it easier to analyze the data later on.

Also, we plan to move the authentication backend off of Render, as Render spins down the backend after a period of inactivity, which can cause a lot of delay. (We used Render because Vercel would not work with our database library.)
