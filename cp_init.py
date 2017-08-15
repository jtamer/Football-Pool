import json
import os

PATH = '/Users/jimtamer/Documents/GitHub/Football-Pool'
#PATH = '/Users/tardigcode/code/Football-Pool'

EMAIL_PATH = os.path.join(PATH, 'Emails')
PATTERNS_PATH = os.path.join(PATH, 'patterns.txt')
PATTERNS_LONG_PATH = os.path.join(PATH, 'patterns_long.txt')
JSON_PATH = os.path.join(PATH, 'football-server/picks.json')
XREF_PATH = os.path.join(PATH, 'EmailPlayerXref.txt')

_SCHEDULE_PATH = os.path.join(PATH, 'football-server/schedule.json')
with open(_SCHEDULE_PATH, encoding='utf-8') as f:
	SCHEDULE = json.load(f)

CUR_WEEK = SCHEDULE['current_week']
