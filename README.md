# MacOS media / Slack Integration

## Why does this exist?

I wanted to be able to push my now-listening status (including album art) to my company's Slack.

## Sounds cool. What do I need to do?

### 1. Install the dependencies

```bash
pip3 install -r ./requirements.txt
brew install nowplaying-cli
```

### 2. Create and update your `config.json` file

```bash
cp config.default.json config.json
```

#### Get Slack tokens

Help coming soon

#### Update `emoji-name` _(optional)_

Replace `my-album-art` with your desired Slack emoji name

#### Update `time-format` _(optional)_

Replace `%X` with your desired [datetime formatting string](https://strftime.org/)

### 3. Start your media player

You need to be playing your media _before_ moving on to step 4.

### 4. Run the track change listener script

```bash
python3 macos-media-player-track-change-to-slack.py
```

The script will attempt to:

- save your album art as a Slack emoji and
- set your status to the now-playing text including the artist and title and the album-art emoji

```plaintext
[✓] 15:00:57 → 15:04:30 [:my-album-art:] Now Playing: All-4-One - So Much In Love
[✓] 15:04:28 → 15:08:47 [:radio:] Now Playing: Haley Reinhart - I Belong to You
```

If the script is unable to create the album-art emoji (because of a bad token, no local album art, whatever), it will try to set the status using a standard emoji instead, randomly picking one of the following:

- :cd: (`:cd:`)
- :headphones: (`:headphones:`)
- :musical_note: (`:musical_note:`)
- :notes: (`:notes:`)
- :radio: (`:radio:`)

## Whom should I thank?

- Thanks to Jack Ellenberger (@jackellenberger) for his [":slack_on_fire:" article](https://medium.com/@jack.a.ellenberger/slack-on-fire-part-two-please-stop-rotating-my-user-token-replay-attacking-slack-for-emoji-fun-c87da4e54b03) and his emojme library (particularly [`emoji-add.js`](https://github.com/jackellenberger/emojme/blob/e076b58bbe310da154013b51f77d3e1047938983/lib/emoji-add.js#L79-L82)) for helping me figure out how to push an emoji to Slack's [undocumented `/api/emoji.add` endpoint](https://webapps.stackexchange.com/a/126154/35105).
- Thanks to [Kirtan Shah](https://github.com/kirtan-shah) for his [`nowplaying-cli`](https://github.com/kirtan-shah/nowplaying-cli) utility that provides the media information under the hood.

## Do you have any improvements planned?

- Add artist and/or song title blacklists to prevent specific tracks from being sent to Slack.
- Check the current play time to more accurately determine an end time for the Slack status (instead of assuming that the whole song still needs to be played).
- Consolidate the Mac, [Windows](https://github.com/curtisgibby/winrt-slack-python), and [Linux](https://github.com/curtisgibby/mpris-slack-python) versions of this script (so that the OS-specific parts of the process are pulled out into modules, and the common stuff can all be run in a single python script).
- If possible, get rid of the external dependency on `nowplaying-cli`. (If you know how to get this data from native Python APIs, please add an answer to [my Stack Overflow question](https://stackoverflow.com/questions/78609762/how-can-i-use-pythons-mpnowplayinginfocenter-to-get-current-song-information-fr).)
