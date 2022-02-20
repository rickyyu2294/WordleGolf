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

  await midnight()

async def midnight():
  now = datetime.now(tz=PST)
  targetTime = datetime(now.year, now.month, now.day + 1, 0, 0, 0, 0, PST)
  diff = (targetTime - now).total_seconds()
  await asyncio.sleep(diff)
  channel = client.get_channel(BOT_CHANNEL_ID)
  #await channel.send("Is it midnight?")

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
    #
    await displayScore(message, name, user_id)

  # Match Wordle Message
  pattern = re.compile("Wordle [0-9].. [0-9]/[0-9]")
  regex_match = re.match(pattern, message.content)

  if regex_match:
    s = message.content.split()
    name = str(message.author)
    puzzle_id = s[1]
    score = s[2].split("/")[0]
    await addScore(message, user_id, name, puzzle_id, score)

async def displayScore(message, name, user_id):
    if user_id is None:
      await message.channel.send("No record of user " + name)

    tokens = message.content.split()
    if len(tokens) == 1:
      # get scores of week
      today = datetime.today()
      print(today)
      today_weekday = today.weekday()
      if today_weekday == 0:
        #print only today's score
        puzzle_id = wordle_helper.date_to_puzzle_id(today)
        print(puzzle_id)
        score = database.select_user_score_for_puzzle_id(DB_FILE, user_id, puzzle_id)
        if score is None:
          score = 6
        await message.channel.send(name + " scored " + str(score) + "/6 this week")
      else:
        #print scores from monday to today
        delta = today.weekday()
        date = today - timedelta(days=delta)
        print("delta " + str(delta) + " date " + str(date))
        score = 0
        for i in range(0, delta):
          date = date + timedelta(days=1)
          puzzle_id = wordle_helper.date_to_puzzle_id(date)
          day_score = database.select_user_score_for_puzzle_id(DB_FILE, user_id, puzzle_id)
          print("Puzzle " + str(puzzle_id) + " Score " + str(day_score))
          if day_score is None:
            day_score = 6
          score = score + day_score 
        await message.channel.send(name + " score " + str(score) + "/" + str(6 * (delta + 1)) + " this week")

      print("show week score")

    if len(tokens) == 2 and tokens[1].isdigit():
      print("show score")
      puzzle_id = str(tokens[1])
      score = str(database.select_user_score_for_puzzle_id(DB_FILE, user_id, puzzle_id))
      if score is not None:
        await message.channel.send(name + " scored " + score + " on day " + puzzle_id)
      else:
        await message.channel.send(name + " does not have a score on day " + puzzle_id)

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

  temp = (name + " scored " + score + " on day " + puzzle_id)
  print(temp)

# Execute
client.run(BOT_TOKEN)