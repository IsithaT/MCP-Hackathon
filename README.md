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
