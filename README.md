---
title: Hermes - Automated Asynchronous REST API Monitoring
short_description: Input any API configuration and monitor responses over time.
sdk: gradio
sdk_version: "5.33.0"
emoji: 🪽
colorFrom: orange
colorTo: yellow
license: mit
pinned: true
tags:
  - Agents-MCP-Hackathon
  - mcp-server-track
---

# Hermes - Automated Asynchronous REST API Monitoring

## Link to demo video: (placeholder for video link)

## MCP API Key Generation link: [Generate MCP API Key](https://mcp-hackathon.vercel.app/main)

Hermes is a tool designed to automate the monitoring of REST API endpoints. It allows users to input their API configurations and monitor the responses over time, allowing for both data collection/tracking and API performance analysis.

## Who are we? Why did we build this?

We're a team of 4 late-second/early-third-year CS students. This hackathon was most of us's first time working with a lot of the technologies we used, such as database management, servers, and hosting. We decided to build Hermes since a lot of us realized that there wasn't really a good way to monitor APIs, at least not without a lot of manual work. We wanted to build a tool that would allow users to easily do this, no matter what it may be used for. We also wanted to build something that would allow us to learn more about the technologies we were using, and we definitely did that!

## How does it work?

Hermes requires users to generate an MCP API key, which you can do right [here at this link](https://mcp-hackathon.vercel.app/main). Once you have your API key, you (or an agent etc. Claude), can perform the following steps:

1. **Validate API Configuration**: Use the `validate_api_configuration` function to check if your API configuration is valid. If the request fails, it will return the error. Else, it will save the configuration to the database and return a success message with `config_id`. The user/agent can then decide whether to proceed with monitoring based on the response (etc. can reject the API configuration if it doesn't show the desired data content).
2. **Activate Monitoring**: Use the `activate_monitoring` function with the `config_id` from the previous step to start monitoring the API. This will set up a background task that will periodically check the API and store the responses.
3. **Get Monitoring Data**: Use the `get_monitoring_data` function with the `config_id` to retrieve the monitoring data. You can specify the mode of data retrieval (summary, details, or full) to get the desired level of information. This can be called anytime after monitoring is activated.

### :warning: Important! :warning:

Call results and configurations will be deleted 14 days after the last call to the API. This is to ensure that the database does not get too large and to protect user privacy.

## Problems we ran into

Since (free) Gradio is stateless, we had to find a way to pass down information between both the different API calls and the user calls, while still ensuring privacy. We ended up using the MCP API key as a user identifier, which allowed us to separate user data while still being able to access it when needed. There was also the problem of having to validate the data and making sure that the user/agent is satisfied with the data before activating monitoring. We solved this by separating the whole process into multiple functions, which allowed us to validate the data before activating monitoring.

## Future Steps

Currently, the API call results store the entire response, which can be quite large, especially for LLMs like Claude to handle (or reach conversation limits). In the future, we think that we can improve this by allowing users to specify a format for the response, such as only storing the text content or a specific field in the response. This would allow users to save space and make it easier to analyze the data later on.

Also, we plan to move the authentication backend off of Render, as Render spins down the backend after a period of inactivity, which can cause a lot of delay. (We used Render because Vercel would not work with our database library.)
