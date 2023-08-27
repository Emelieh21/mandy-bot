# mandy-bot
A telegram bot that let's me know if Mandy is being noisy at home

## Introduction
We went on a trip last weekend with our two dogs and discovered our newly adopted dog Mandy howls like a wolf when she is left alone on the hotel room for just a few minutes. We wanted to become more aware of how much she howls and when so we can do something about it. We thought: why not give Mandy her own Telegram (bot) account so she can inform us when she is howling (meaning, the bot will send us a message, maybe even a voice clip, whenever too much noise is detected at home).

## Set up the bot
To set up the Telegram bot I just needed to start a conversation with the @BotFather on Telegram and say the following things:

/newbot

Which allowed me to set up the new bot by giving it a name and an ID. The name has to be unique so sadly I could not call this bot "MandyBot". Therefore it was baptized **MandyAtHomeBot**. A bit less catchy but it will do the job. Next thing was to set a profile picture for the bot to make it looks less boring:

/setuserpic

The BotFather will tell you "Current status is: ENABLED". You can disable this by simply saying "Disable".

## Make the bot talk
I am following [this tutorial](https://www.codementor.io/@karandeepbatra/part-1-how-to-create-a-telegram-bot-in-python-in-under-10-minutes-19yfdv4wrq) to set up the bot. To use the token the BotFather gave me, I am installing dotenv so I can use it as an env variable.

```
pipenv install python-dotenv
```

## Start tracking Mandy
This happens in the tracker.py file. We need a Postgres DB connection & we need to be able to listen to & record audio.

### Set up database connection
I am using Cockroach DB for storing the tracking data, since I already have it setup from previous projects. In my experience it was really easy to get started with, see [the official quickstart](https://www.cockroachlabs.com/docs/cockroachcloud/quickstart). 

To connect to my Cockroach DB from python I need to install psycopg2 module.

```
pipenv install psycopg2-binary
```

Sadly for me this did not work out of the box. I kept getting import errors, also after uninstalling and reinstalling and trying it without pipenv. After researching more I tried:

```
brew install libpq
? brew install openssl
```

Which took really long to run and I have no clue if it works

> Still in progres...

### Set up pyaudio
To install pyaudio, I needed to brew install portaudio first on my Mac:

```
brew install portaudio
```

Then I could install pyaudio:

```
pipenv install pyaudio
```
