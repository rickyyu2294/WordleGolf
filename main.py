import discord
import os
import re
import asyncio
from datetime import date, timedelta
from datetime import datetime
import pytz
from discord.ext import commands, tasks
import database
import json
import wordle_helper
f = open('config.json')
data = json.load(f)

# constants and literals
MAX_TRIES = 6
BOT_CHANNEL_ID = 879170130125414450
BOT_TOKEN = data["token"]
PST = pytz.timezone('US/Pacific')
DB_FILE = r"sqliteDatabase.db"
client = discord.Client()

#def delete(name):
#  match = db.prefix(name)
  #userScores = db[name];
  #if len(match) != 0:
  #  del db[name]
  #  print("Deleted " + name)
  #else:
  #  print("No entry for " + name)

# ============================
# Events
# ============================

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  print('v0.08')
  database.initialize_database(DB_FILE)

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  name = str(message.author) 
  user_id = database.select_user_id(DB_FILE, name)

  if message.content.startswith('$hello'):
    print('moo')
    await message.channel.send('hi')

  # if message.content.startswith('$delete'):
  #   delete(name)

  # CHECK SCORE ====================================================
  if message.content.startswith('$score'):
    #weekly
    tokens = message.content.split()
    if len(tokens) == 1:
      score = weekly_score(message, user_id)
      total = (datetime.today().astimezone(PST).weekday() + 1) * 6
      if score is not None:
        await message.channel.send(name + " scored " + str(score) + "/" + str(total) + " this week")
    elif len(tokens) == 2 and tokens[1].isdigit():
      # score for specific day
      score = date_score(user_id, tokens[1])
      await message.channel.send(name + " scored " + str(score) + " on day " + str(tokens[1]))
    elif len(tokens) == 2:
      user_id = database.select_user_id(DB_FILE, tokens[1])
      score = weekly_score(message, user_id)
      total = (datetime.today().astimezone(PST).weekday() + 1) * 6
      if score is not None:
        await message.channel.send(tokens[1] + " scored " + str(score) + "/" + str(total) + " this week")

  # Match Wordle Message
  pattern = re.compile("Wordle [0-9].. [0-9]/[0-9]")
  regex_match = re.match(pattern, message.content)

  if regex_match:
    s = message.content.split()
    name = str(message.author)
    puzzle_id = s[1]
    score = s[2].split("/")[0]
    await addScore(message, user_id, name, puzzle_id, score)

def weekly_score(message, user_id):
  if user_id is None:
    return None

  # get scores of week
  today = datetime.today().astimezone(PST)
  print("Today " + str(today))
  today_weekday = today.weekday()
  print("Weekday " + str(today_weekday))
  if today_weekday == 0:
    #print only today's score
    puzzle_id = wordle_helper.date_to_puzzle_id(today)
    print(puzzle_id)
    score = database.select_user_score_for_puzzle_id(DB_FILE, user_id, puzzle_id)
    if score is None:
      score = 6
    return score
  else:
    #print scores from monday to today
    print(user_id)
    date = today - timedelta(days=today_weekday)
    print("delta " + str(today_weekday) + " date " + str(date))
    score = 0
    for i in range(0, today_weekday + 1):
      puzzle_id = wordle_helper.date_to_puzzle_id(date)
      day_score = database.select_user_score_for_puzzle_id(DB_FILE, user_id, puzzle_id)
      print("Puzzle " + str(puzzle_id) + "Date " + str(date) +  " Score " + str(day_score))
      if day_score is None:
        day_score = 6
      score = score + day_score 
      date = date + timedelta(days=1)
    return score

def date_score(user_id, puzzle_id):
  score = str(database.select_user_score_for_puzzle_id(DB_FILE, user_id, puzzle_id))
  if score is not None:
    return score
  else:
    return None

async def addScore(message, user_id, name, puzzle_id, score):
  # add new score to user's score list
  # check if user is in database

  if user_id is not None:
    score_id = database.select_user_score_for_puzzle_id(DB_FILE, user_id, puzzle_id)
    if score_id is None:
      database.add_score(DB_FILE, user_id, puzzle_id, score)
    else:
      await message.add_reaction("❌")
      print(name + " already scored on day " + puzzle_id)
      return

  # else, add new user to db
  else:
    user_id = database.insert_user(DB_FILE, name)
    database.add_score(DB_FILE, user_id, puzzle_id, score)
  await message.add_reaction("✅")
  week_score = weekly_score(message, user_id)

  temp = (name + " scored " + score + " on day " + puzzle_id)
  print(temp)

# Execute
client.run(BOT_TOKEN)