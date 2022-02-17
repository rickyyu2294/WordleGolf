import discord
import os
import re
import random
import asyncio
from datetime import date
from datetime import datetime
import pytz
from discord.ext import commands, tasks
import time
import threading
import database
import json
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
  print('v0.05')
  database.initialize_database(DB_FILE)

  await midnight()

async def midnight():
  now = datetime.now(tz=PST)
  targetTime = datetime(now.year, now.month, now.day + 1, 0, 0, 0, 0, PST)
  diff = (targetTime - now).total_seconds()
  await asyncio.sleep(diff)
  channel = client.get_channel(BOT_CHANNEL_ID)
  await channel.send("Is it midnight?")

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  name = str(message.author) 
  today = date.today()

  if message.content.startswith('$hello'):
    print('moo')
    await message.channel.send('hi')

  # if message.content.startswith('$delete'):
  #   delete(name)

  # CHECK SCORE ====================================================
  # check daily and weekly score and print both in channel
  if message.content.startswith('$score'):
    tokens = message.content.split()
    print("Today's date:", today)
    # dummy messages
    await message.channel.send("Stats for " + name)
    await message.channel.send("Today's score is: " + "[score]")
    await message.channel.send("Total points for the week: " + "[scoreSum]")

    # if played today, return daily score
    # print("Your score today is ")
    # else, notify that they need to play today

    # additionally, attempt to return running sum for weekly score
    # if sum does not exist, notify they need to participate once?
    # (or, default to giving them 6 pts per missed day?)

  # CHECK SCORE ==================================================

  # Match Wordle Message
  pattern = re.compile("Wordle [0-9].. [0-9]/[0-9]")
  regex_match = re.match(pattern, message.content)

  if regex_match:
    s = message.content.split()
    name = str(message.author)
    puzzle_id = s[1]
    score = s[2].split("/")[0]
    await addScore(message, name, puzzle_id, score)

async def addScore(message, name, puzzle_id, score):
  # add new score to user's score list
  # check if user is in database
  user_id = database.select_user_id(DB_FILE, name)
  if user_id is not None:
    score_id = database.select_user_score(DB_FILE, user_id, puzzle_id)
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