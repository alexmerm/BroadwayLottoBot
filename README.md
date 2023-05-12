# Telecharge Broadway Lottery Enterer
This program will allow you to automatically enter any number of Broadway Telecharge Lotteries automatically using selenium automation every day at 10:20am

## Installation

1. rename config_example.json to config.json
2.  enter your information in config.json 
3. run ``docker compose up -d --build`` to bring up the service
4. Once the service runs once, update showsToGet.json with your preference on which lotteries to enter

Note: to trigger the program manually, uncomment ``entrypoint : ['python', 'runDefault.py']`` in docker-compose.yml
### config.json
- FACEBOOK_EMAIL : your facebook email login
- FACEBOOK_PASSWORD : your facebook password
- NUM_TICKETS_FOR_NEW_SHOW : if a show appears for the lottery thats not specified in showToEnter.json, enter for this many tickets

### showsToEnter.json
Each entry is the title of a show, and the value is the number of tickets to enter the lottery for
