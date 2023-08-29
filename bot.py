#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import os
import logging
from utils.functions import get_update, generate_latest_plot, is_invalid_user
from subprocess import Popen, DEVNULL
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define global object to assign subprocess to
extProc = None

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.


def help(update, context):
    """Send a message when the command /help is issued."""
    # For now, Mandy can only talk to me
    if is_invalid_user(update):
        return
    help_text = (
        "Hi, I am Mandy. I can assist you with the following commands:\n"
        "/send_update - Sends a summary of my noise\n"
        "/send_audio - Sends a voice clip\n"
        "/send_plot - Sends a plot\n"
        "/start_tracking - To start tracking Mandy's noise\n"
        "/stop_tracking - To stop tracking Mandy's noise\n"
    )
    update.message.reply_text(help_text)


def send_update(update, context):
    """Send a message when the command /update is issued."""
    # For now, Mandy can only talk to me
    if is_invalid_user(update):
        return
    txt = get_update()
    update.message.reply_text(txt)


def send_plot(update, context):
    """Send a message when the command /update is issued."""
    # For now, Mandy can only talk to me
    if is_invalid_user(update):
        return
    generate_latest_plot()
    update.message.reply_photo(open("./plot.jpg", "rb"))


def send_audio(update, context):
    """Send a message when the command /update is issued."""
    # For now, Mandy can only talk to me
    if is_invalid_user(update):
        return
    update.message.reply_audio(open("./output.wav", "rb"), title="Here is my most impressive bark")


def start_tracking(update, context):
    """Starts a background process running the tracking script"""
    if is_invalid_user(update):
        return
    global extProc 
    if extProc == None:
        # TODO: repetitive code, make this a function
        # TODO: we need some kind of id, shared between the bot and the tracker script to give info on the current tracking session only...
        extProc = Popen(['pipenv', 'run', 'python','tracker.py'], stdout=DEVNULL, stderr=DEVNULL)
        update.message.reply_text("Started tracking...") 
    # If the tracking has previously be terminated we can see detect it with the statuscode -15
    elif Popen.poll(extProc) == -15:
        #TODO: it looks like this script is quite heavy in the background... it also crashed already once. Check maybe if it could be leaner?
        extProc = Popen(['pipenv', 'run', 'python','tracker.py'], stdout=DEVNULL, stderr=DEVNULL)
        update.message.reply_text("Started tracking...") 
    else:
        update.message.reply_text("I can't start tracking, because a tracking process is already running...") 


def stop_tracking(update, context):
    """Stops the tracking script that is running in the background"""
    if is_invalid_user(update):
        return
    global extProc 
    if extProc != None:
        Popen.terminate(extProc)
        print(Popen.poll(extProc))
        update.message.reply_text("Tracking process stopped.")
    else:
        update.message.reply_text("No tracking process running...")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    print("MandyBot is running...")
    updater = Updater(os.environ.get("TOKEN"), use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("send_update", send_update))
    dp.add_handler(CommandHandler("send_plot", send_plot))
    dp.add_handler(CommandHandler("send_audio", send_audio))
    dp.add_handler(CommandHandler("start_tracking", start_tracking))
    dp.add_handler(CommandHandler("stop_tracking", stop_tracking))
    # TODO: add a function to record audio and send it...

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()