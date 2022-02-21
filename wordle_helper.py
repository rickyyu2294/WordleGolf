from datetime import date, timedelta
from datetime import datetime
import pytz

PST = pytz.timezone('US/Pacific')
BASE_WORDLE_ID_TO_DATE = (244, datetime(2022, 2, 18).astimezone(PST))

def date_to_puzzle_id(date):
  delta = date - BASE_WORDLE_ID_TO_DATE[1]
  delta_days = delta.days
  return_id = BASE_WORDLE_ID_TO_DATE[0] + delta_days
  if return_id > 0:
    return return_id

def puzzle_id_to_date(puzzle_id):
  # get diff b/t base and requested puzzle_id
  if puzzle_id <= 0:
    return None
  diff = puzzle_id - BASE_WORDLE_ID_TO_DATE[0]
  return BASE_WORDLE_ID_TO_DATE[1] + timedelta(days=diff)

async def numeric_reaction(message, num):
    for e in str(num):
        if e == '0':
            await message.add_reaction("0️⃣")
        elif e == '1':
            await message.add_reaction("1️⃣")
        elif e == '2':
            await message.add_reaction("2️⃣")
        elif e == '3':
            await message.add_reaction("3️⃣")
        elif e == '4':
            await message.add_reaction("4️⃣")
        elif e == '5':
            await message.add_reaction("5️⃣")
        elif e == '6':
            await message.add_reaction("6️⃣")
        elif e == '7':
            await message.add_reaction("7️⃣")
        elif e == '8':
            await message.add_reaction("8️⃣")
        elif e == '9':
            await message.add_reaction("9️⃣")

    return