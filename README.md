# Discord Email Verify Bot

## Usage

Install all of the requirements by running the following commands:

- First time only: `python3 -m venv .venv`
- Every run:
  - Activate venv:
    - Linux/macOS: `source .venv/bin/activate`
    - Windows (cmd): `.venv\Scripts\activate.bat`
    - Windows (PowerShell): `.venv\Scripts\Activate.ps1`
  - `pip install -r requirements.txt -U`

Create a config file named `config.ini` with the following syntax, replacing
the variables with the apporiate items.  Comments can be deleted as desired.

```ini
[DEFAULT]
AUTH0_URL = https://AUTH0_DOMAIN_NAME.us.auth0.com 
AUTH0_CLIENT_ID = abcdefg
AUTH0_CLIENT_SECRET = abcdefg
DISCORD_TOKEN = abcdefg

# Replace the number in the brackets with the Guild ID for the server.
# This can be gathered by visiting and signing into Dicord in your browser,
# visiting a channel in the server that you plan to join the bot to,
# then getting the guild from the URL like below:
#
#                              |- This Part -|
# https://discord.com/channels/123456789012345/98765
#
# This section can be added for as many servers as desired.

[123456789012345]
# This can have multiple domains as desired, separated with commas,
# without any spaces.
EMAIL_VALID_DOMAINS = example.com,test.example.com
# Name of the role has to be exactly the same as it appears in Discord.
DISCORD_ROLE_TO_GIVE = Test-Role

```

Once the configuration file has been created, ensure that you are in the
virtual environment as noted above, then start the bot by running `./start.sh`
(Linux/macOS) or `./start.bat` (Windows).
