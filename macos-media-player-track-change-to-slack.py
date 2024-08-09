from MediaPlayer import MPNowPlayingInfoCenter
import asyncio
import base64
import calendar
import datetime
import json
import random
import requests
import subprocess
import os
from PIL import Image
from io import BytesIO
from time import sleep
from time import strftime

def get_default_status_emoji():
    return random.choice([
        ':cd:',
        ':headphones:',
        ':musical_note:',
        ':notes:',
        ':radio:',
    ])

def get_local_file():
    imageData = current_media_info['thumbnail']
    if imageData is None or imageData == 'null' or imageData == '':
        return False

    try:
        # Load image from BytesIO
        im = Image.open(BytesIO(base64.b64decode(imageData)))
        local_filename = 'album-art.jpg'
        im.thumbnail((96, 96))
        im.save(local_filename)
    except Exception as error:
        print('Error writing file: ' + str(error))
        return False

    return local_filename


def delete_slack_emoji():
    postBody = {
        'token': slack_token,
        'name': emoji_name,
    }
    
    r = requests.post(
        'https://slack.com/api/emoji.remove',
        data = postBody,
        cookies = {'d': slack_cookie_token}
    )

    if(r.ok):
        parsed = json.loads(r.text)
        if parsed['ok']:
            return True
        else:
            return False
    else:
        r.raise_for_status()
    
    return False

def ensure_slack_does_not_have_emoji():
    r = requests.get(
        'https://slack.com/api/emoji.list',
        params = {'token': slack_token},
        cookies = {'d': slack_cookie_token}
    )

    if(r.ok):
        parsed = json.loads(r.text)
        if parsed['ok']:
            if emoji_name in parsed['emoji']:
                return delete_slack_emoji()
            else:
                return True
        else:
            return False
    else:
        r.raise_for_status()
    
    return False

def upload_file_to_slack(local_file):
    if not os.path.exists(local_file):
        return False

    slack_does_not_have_emoji = ensure_slack_does_not_have_emoji()
    if not slack_does_not_have_emoji:
        return False

    with open(local_file, 'rb') as f:
        postBody = {
            'token': slack_token,
            'mode': 'data',
            'name': emoji_name,
        }
        
        files = {'image': f}

        r = requests.post(
            'https://slack.com/api/emoji.add',
            data = postBody,
            files = files,
            cookies = {'d': slack_cookie_token}
        )
    
    if os.path.exists(local_file):
        os.remove(local_file)
    if(r.ok):
        parsed = json.loads(r.text)
        if parsed['ok']:
            return emoji_name
        else:
            return False
    else:
        # r.raise_for_status() # debug!
        return False

def get_status_emoji():
    local_file = get_local_file()
    if local_file:
        uploaded_file_to_slack = upload_file_to_slack(local_file)
        if uploaded_file_to_slack:
            return ':' + uploaded_file_to_slack + ':'

    return get_default_status_emoji()

def set_slack_status():
    if current_media_info['artist'] == '' or current_media_info['title'] == '':
        return False
    status_text = 'Now Playing: ' + current_media_info['artist'][:50] + ('...' if len(current_media_info['artist']) > 50 else '') + ' - ' + current_media_info['title']
    status_text = status_text[:97] + ('...' if len(status_text) > 97 else '')

    status_emoji = get_status_emoji()

    expiration_time = datetime.datetime.now(datetime.UTC) + datetime.timedelta(seconds=current_media_info["length"])
    local_expiration_time = datetime.datetime.now() + datetime.timedelta(seconds=current_media_info["length"])

    profile = {
        'status_emoji': status_emoji,
        'status_expiration': calendar.timegm(expiration_time.timetuple()),
        'status_text': status_text,
    }

    postBody = {
        'token': slack_token,
        'profile': json.dumps(profile),
    }

    print('[ ] \u001b[36m' + strftime(time_format) +
          ' → ' + local_expiration_time.strftime(time_format) +
          ' \u001b[33m[' + status_emoji + ']' +
          ' \u001b[0m' + status_text, end='\r')

    r = requests.post(
        'https://bamboohr.slack.com/api/users.profile.set',
        data = postBody,
        cookies = {'d': slack_cookie_token}
    )

    if(r.ok):
        parsed = json.loads(r.text)
        if parsed['ok']:
            print('[\u001b[32m✓\u001b[0m')
        else:
            print('[\u001b[30m×\u001b[0m')
            print('Error setting status : ' + parsed['error'])
            quit()
    else:
        r.raise_for_status()

async def get_media_info():

    # Command to execute
    cmd = ["nowplaying-cli", "get", "artist", "title", "duration", "artworkData"]

    # Execute the command
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output, error = process.communicate()

    # Check if the command was executed without errors
    if error is None:
        [artist, title, duration, thumbnail, *junk] = output.decode('utf-8').split('\n')
        if duration != 'null':
            duration = int(float(duration))
        else:
            duration = 180
    else:
        print(f"Error occurred while executing command: {error}")

    if artist == 'null' or title == 'null':
        raise RuntimeError

    return {
        'artist': artist,
        'title': title,
        'length': duration,
        'thumbnail': thumbnail
    }

try:
    with open("config.json") as config_file:
        config = json.load(config_file)
except IOError as error:
    print('Unable to read `config.json` file. Run `python3 set-up-configuration.py`.')
    quit()

try:
    slack_token = config['slack-token']
except Exception as error:
    print('Config value `slack-token` not defined in `config.json`')
    quit()

try:
    slack_cookie_token = config['slack-cookie-token']
except Exception as error:
    print('Config value `slack-cookie-token` not defined in `config.json`')
    quit()

try:
    time_format = config['time-format']
except Exception as error:
    print('Config value `time-format` not defined in `config.json`')
    quit()

try:
    emoji_name = config['emoji-name']
except Exception as error:
    emoji_name = 'my-album-art'

try:
    title_blacklist = config['title-blacklist']
except Exception as error:
    title_blacklist = []

try:
    artist_blacklist = config['artist-blacklist']
except Exception as error:
    artist_blacklist = []

try:
    if slack_token == '':
        raise Exception('empty string')
    if slack_token == 'YOUR_SLACK_TOKEN' :
        raise Exception(slack_token)
except Exception as error:
    print('Invalid value for `slack-token` in `config.json`: ' + str(error))
    quit()

previous_media_info = {
    'artist': '',
    'title': ''
}

while True:
    try:
        current_media_info = asyncio.run(get_media_info())
    except RuntimeError:
        current_media_info = previous_media_info

    if current_media_info is None:
        current_media_info = previous_media_info

    if any(x in current_media_info['title'] for x in title_blacklist):
        current_media_info = previous_media_info

    if any(x in current_media_info['artist'] for x in artist_blacklist):
        current_media_info = previous_media_info

    if current_media_info['artist'] == '' or current_media_info['title'] == '':
        current_media_info = previous_media_info

    if current_media_info['artist'] != previous_media_info['artist'] or current_media_info['title'] != previous_media_info['title']:
        previous_media_info = current_media_info
        set_slack_status()

    try:
        sleep(5)
    except KeyboardInterrupt:
        quit()
