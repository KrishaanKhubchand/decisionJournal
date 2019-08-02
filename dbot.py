#cfc!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler, CallbackQueryHandler)

import logging
import sqlite3
from sqlite3 import Error
import datetime
from datetime import time
import schedule
import time


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

ENERGY, DECISIONDESC, BACKGROUND, COMPONENTS, COMPLICATIONS, UNDECIDED, OUTCOMES, RIFF, FINALANSWER, DONE = range(10)

## CREATING FUCKING DATABASE MOFO:
# reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True

def start(bot, update, job_queue):
    global user
    user = update.message.from_user
    global userid
    userid = user['id']
    global name
    name = user['username']

    bot.send_message(chat_id = update.message.chat_id, text= "Hi, I'm your Decision Journal Bot. Many of our outcomes are the product of the decisions we make. My goal is to help you make better decisions by: \n\n1. Helping you regularly think through decisions you have to make. \n2. Creating a consious feedback loop, where you reflect on your decisions and learn from them over time. \n\nHere are my commands: \n/newdecision - Creates a new Decision Journal Entry. I'll ask you a bunch of questions so you can think through your choice. \n/review - Let's you review your decisions and extract lessons from them. \n/learn - Receive a list of resources for improving decision-making. \n \nThat's it. Happy decision-making! :)")
    # change to run daily; w/time in date.time formatting
    job_queue.run_daily(reminders, time(13, 00), context = update.message.chat_id)

    update.message.reply_text(" ")
    #add user to db here: -- need to check if user exists first? -> use integrity check! yea boy
    userconnection = sqlite3.connect('decisionDB.db')
    userCon = userconnection.cursor()
    try:
        userCon.execute("INSERT INTO users (user_id, name) VALUES (?,?)", (userid, name,))
        userconnection.commit()
        print (userCon.fetchone())
    except sqlite3.IntegrityError:
        print("not today mugabee!")

def newdecision(bot, update):
    reply_keyboard = [["Let's do this!"]]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text("It's decision-time, which means it's time for you to combat the urge to avoid honest reflection or engage in self deception. Ready?  \n \nYou ready to start?", reply_markup = markup)

    return ENERGY

def energy(bot, update):
    energykeyboard = [["Energised,", "Focused", "Relaxed"],
                        ["Confident", "Tired", "Accepting"],
                        ["Anxious", "Frustrated", "Apathetic"]]
    new_markup = ReplyKeyboardMarkup(energykeyboard, one_time_keyboard = True)
    update.message.reply_text("Starting with how you feel. Which descriptor from below is most accurate? Small things like these can have big effects on the quality of our decisions.", reply_markup = new_markup)

    return DECISIONDESC

def decisionDesc(bot, update):
    global theEnergy
    theEnergy = update.message.text
    update.message.reply_text("In one sentence, What is the decision that you have to make?")

    return BACKGROUND

def background(bot, update):
    global decisionStatement
    decisionStatement = update.message.text
    update.message.reply_text("What is the background context/situation for this decision?")

    return COMPONENTS

def components(bot, update):
    global theBackground
    theBackground = update.message.text
    update.message.reply_text("What are the individual variables that govern the situation and the possible outcomes of your decision?")

    return COMPLICATIONS

def complications(bot, update):
    global theComponents
    theComponents = update.message.text
    update.message.reply_text("What complications might arise? How might you avoid/deal with them?")

    return UNDECIDED

def undecided(bot, update):
    global theComplications
    theComplications = update.message.text
    update.message.reply_text("What is the cost of indecisiveness?")

    return OUTCOMES

def outcomes(bot, update):
    global oppCost
    oppCost = update.message.text
    update.message.reply_text("What's the range of outcomes that could occur, as a consequence of the choices you make? Assign a % probaility to each of them and explain the reasoning/why.")

    return RIFF

def riff(bot, update):
    global allOutcomes
    allOutcomes = update.message.text
    update.message.reply_text("Before making your final decision, a few things worth considering / riffing on: \n\nAre you failing to consider something because of your background? \nWhat might the second and third order consequences be? \nWho is the best person person to make this decision? \nWhat would failure look like? How would you recover? \nHow can you measure the effectiveness of this decision in the future? \nHow might you make this decision easier to execute?")

    return FINALANSWER

def finalanswer(bot, update):
    global theRiff
    theRiff = update.message.text
    update.message.reply_text("Given what you've considered - What is your decision going to be?")

    return DONE

def done(bot, update, job_queue):
    global finalDecision
    finalDecision = update.message.text
    bot.send_message(chat_id = update.message.chat_id, text= "Awesome. I'll be checking in with you in a couple of weeks to review your decision and its implications!")
    # change to run daily; w/time in date.time formatting
    job_queue.run_daily(theupdate, time(17, 00), context = update.message.chat_id)
    originalInterval = 18
    countdownInterval = 18
    user = update.message.from_user
    userid = user['id']
    connection = sqlite3.connect('decisionDB.db')
    longCon = connection.cursor()
    try:
        longCon.execute("INSERT INTO decisions (user_id, energy, decision_statement, background, components, complications, undecided, outcomes, riff, final_answer, original_interval, countdown_interval) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (userid, theEnergy, decisionStatement, theBackground, theComponents, theComplications, oppCost, allOutcomes, theRiff, finalDecision, originalInterval, countdownInterval))
        connection.commit()
        longCon.execute("SELECT * FROM decisions")
        print (longCon.fetchone())
    except Error as e:
        print(e)

    return ConversationHandler.END


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

# user_id = ?", (userid, )
def theupdate(bot, job):
    userid = job.context
    print(userid)
    connection = sqlite3.connect('decisionDB.db')
    longCon = connection.cursor()
    try:
        longCon.execute("UPDATE decisions SET countdown_interval = countdown_interval - 1 WHERE countdown_interval > 0 AND user_id = ?", (userid, ))
        connection.commit()
        longCon.execute("SELECT countdown_interval FROM decisions WHERE user_id = ?", (userid, ))
        print (longCon.fetchone())
    except Error as e:
        print(e)

    #if / then loop; if there is a decision to review, remind of reviewing decisions .. otherwise, don't..

    # also can have a reminder (probs better to have this one in another func, based on /start, x2 daily; asking - do you have any decisions that you might have to make?)

def reminders(bot, job):
    bot.send_message(chat_id = job.context, text="Hey! Any decisions you'd like to think through today?\n\nJust press /newdecision. Or, to review previous decisions and their outcomes, press /review :)")

def review(bot, update):
    #check if there are reviews, if there aren't print NOPE!
    user = update.message.from_user
    userid = int(user['id'])
    connection = sqlite3.connect('decisionDB.db')
    longCon = connection.cursor()
    try:
        longCon.execute("SELECT * FROM decisions WHERE countdown_interval = 0  AND user_id = ?", (userid, ))
        givenDecision = (longCon.fetchall())
        for decision in givenDecision:
            energy = decision[2]
            description = decision[3]
            bg = decision[4]
            comp = decision[5]
            complication = decision[6]
            nose = decision[7]
            outcomeRange = decision[8]
            thatRiff = decision[9]
            answer = decision[10]
            update.message.reply_text(f, "Here are the details for your decision regarding {description}. \n\nEnergy: {energy}. \nBackground: {bg}. \nVariables: {comp}. \nComplications: {complication}. \nOpportunity Costs: {nose}. \nRange of Outcomes: {outcomeRange}. \nExtra Details: {thatRiff}. \nFinal Answer: {answer}.")
            update.message.reply_text("Were you happy with this decision? How did it turn out?")
        #update.message.reply_text(f"Here are the details of your decision:") DDD THIS LATER countdown_interval = 0  AND
        longCon.execute("UPDATE decisions SET countdown_interval = original_interval * 2 AND original_interval = original_interval * 2 WHERE countdown_interval = 0 AND user_id = ?", (userid, ))
        connection.commit()
    except Error as e:
        print(e)

def learn(bot, update):
    update.message.reply_text("Hi! This Bot was made by me, @krishkhubchand and takes great inspiration from the Decision Journals at Farnam Street. Below are 3 important links on decision-making: \n\nhttp://krishaan.net/decisions \nhttps://fs.blog/smart-decisions/ \nhttp://wisdomcurated.com \n\nIf you'd like to message me, you can do it via telegram or twitter, both of my handles are the same - @krishkhubchand.")

def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("682789220:AAHXudGvXeHVQGy4t3B84ETYh21PTnEWgEg")


    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    #get USER info 1st time round:

    #create Job Q:
    jp = updater.job_queue

    Conv_Handler = ConversationHandler(
    entry_points=[CommandHandler('newdecision', newdecision)],
    states = {
        ENERGY: [MessageHandler(Filters.text, energy)],

        DECISIONDESC: [MessageHandler(Filters.text, decisionDesc)],

        BACKGROUND: [MessageHandler(Filters.text, background)],

        COMPONENTS: [MessageHandler(Filters.text, components)],

        COMPLICATIONS: [MessageHandler(Filters.text, complications)],

        UNDECIDED: [MessageHandler(Filters.text, undecided)],

        OUTCOMES: [MessageHandler(Filters.text, outcomes)],

        RIFF: [MessageHandler(Filters.text, riff)],

        FINALANSWER: [MessageHandler(Filters.text, finalanswer)],

        DONE: [MessageHandler(Filters.text, done, pass_job_queue=True)],

    },

    fallbacks = [CommandHandler('cancel', cancel)]
    )
    resource_handler = CommandHandler("learn", learn)
    review_handler = CommandHandler("review", review)
    hello_handler = CommandHandler('start', start, pass_job_queue=True)
    dp.add_handler(hello_handler)
    dp.add_handler(Conv_Handler)
    dp.add_handler(review_handler)
    dp.add_handler(resource_handler)
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
