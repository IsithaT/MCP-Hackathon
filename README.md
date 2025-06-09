# MCP Hackathon Project

## Steps to Run

if it your first time running it:

```
python -m venv venv
```

then activate your virtual environment

then:

```
pip install -r requirements.txt
```

## general understanding/explanation for william by william

user flow ish

1. user goes to input api data and intervals for whenst they want to grab data from said apis
2. in api_validator.py, it gets all that stuff and verifies that it can be done
3. in api_validator.py, it saves all that information under a config_id in the database
4. that is step 1. Now that the information is in the database its time for step 2
5. user indicates that they want to start a schedule, and provides the config_id for that saved configuration of schedule
6. in api_validator.py, we grab the config_id from database and set up an automated scheduler to periodically grab the required information from api and store it in database until no more events are specified that need grabbing and return such info to user upon request
7. i think thats it

### as william, my job should be to set up

1. code that grabs config information
   1. make sure to confirm that mcp api key matches with config id - Coleman
2. creates a schedule for config_id
3. attempts to grab info for api
4. add said info to database
5. make sure that this schedule is robust hopefully

## Deployment to Tailscale Server

1. Update the server configuration in `deploy.sh`:

   ```bash
   SERVER_IP="your-tailscale-server-ip"
   SERVER_USER="your-username"
   ```

2. Make the deploy script executable:

   ```bash
   chmod +x deploy.sh
   ```

3. Run the deployment:

   ```bash
   ./deploy.sh
   ```

4. On the server, set up the daily cron job:

   ```bash
   ./setup-cron.sh
   ```

The application will now run continuously and execute daily at 2 AM.

## Server Management

- Check service status: `sudo systemctl status mcp-hackathon`
- View logs: `sudo tail -f /var/log/mcp-hackathon.log`
- Restart service: `sudo systemctl restart mcp-hackathon`
