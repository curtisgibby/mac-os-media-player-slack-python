import json
import pyperclip
import re
import shutil

config_filepath = "config.json"

try:
    with open(config_filepath) as config_file:
        config = json.load(config_file)
except IOError as error:
    shutil.copyfile('config.default.json', config_filepath)
    print('Created `config.json` from `config.default.json`')

try:
    with open(config_filepath) as config_file:
        config = json.load(config_file)
except IOError as error:
    print('Unable to read `config.json` file. Delete it and start over.')
    quit()

print("This script will help you set up the configuration file")
print("---")
print("First, we'll need to get your Slack authentication tokens")
print("1. Open a Slack page in a browser and press F12 to open the developer tools")
print("2. Go to the Network tab and clear the existing requests by clicking the 'Clear' button")
print("3. Update your status in Slack")
print("4. Look for a request with the name 'users.profile.set' and right-click on it")
print("5. Click 'Copy' -> 'Copy as cURL'")
input("6. Press enter in this window to read the cURL command from the clipboard\n")

# Read the text from the clipboard
curl = pyperclip.paste()

cookieTokenMatch = re.search(" d=(xoxd-[\\w%]+)", curl)
if cookieTokenMatch is None:
    print("No cookie token found")
    exit(1)
config['slack-cookie-token'] = cookieTokenMatch.group(1)

tokenMatch = re.search("(xoxc-[\\w\\-%]+)", curl)
if tokenMatch is None:
    print("No token found")
    exit(1)
config['slack-token'] = tokenMatch.group(1)

default_time_format = config.get('time-format', '%X')
config['time-format'] = input("Enter the time formatting string (from https://strftime.org/) you want to use for the log (defaults to {0}): ".format(default_time_format)) or default_time_format

default_emoji_name = config.get('emoji-name', 'my-album-art')
config['emoji-name'] = input("Enter the emoji name you want to use (defaults to {0}): ".format(default_emoji_name)) or default_emoji_name

with open(config_filepath, 'w') as config_file:
    json.dump(config, config_file, indent=4)

print("\n---\n")
print('Updated `config.json`')
for key in config:
    print(key + ': ' + config[key])
