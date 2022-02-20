BASE_WORDLE_ID_TO_DATE = (244, datetime(2022, 2, 18))

def date_to_puzzle_id(date):
  delta = date - BASE_WORDLE_ID_TO_DATE[1]
  delta_days = delta.days
  print("Delta_day " + str(delta_days))
  return_id = BASE_WORDLE_ID_TO_DATE[0] + delta_days
  if return_id > 0:
    return return_id

def puzzle_id_to_date(puzzle_id):
  # get diff b/t base and requested puzzle_id
  if puzzle_id <= 0:
    return None
  diff = puzzle_id - BASE_WORDLE_ID_TO_DATE[0]
  return BASE_WORDLE_ID_TO_DATE[1] + timedelta(days=diff)