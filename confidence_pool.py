import json
import random
import re
import os
import cp_init


SCHEDULE = cp_init.SCHEDULE

weeks = [week['name'] for week in SCHEDULE['weeks'].values()]
WEEK = cp_init.CUR_WEEK

patterns = []
with open(cp_init.PATTERNS_PATH, encoding='utf-8') as f:
	patterns = f.readlines()
	patterns = [line.strip() for line in patterns]	
	patterns = tuple(eval(line) for line in patterns) 
	
patterns_long = []
with open(cp_init.PATTERNS_LONG_PATH, encoding='utf-8') as f:
	patterns_long = f.readlines()
	patterns_long = [line.strip() for line in patterns_long]	
	patterns_long = tuple(eval(line) for line in patterns_long) 

MAX = int(len({patterns[i][1] for i in range(len(patterns))}) / 2) # max score for the top pick  e.g. 16. 

def load_picks(path=cp_init.JSON_PATH):
        """ Deserialize the picks from the picks json file.
            path is the absolute path to the json file """
        with open(path, 'r') as f:
                return json.load(f)

PICKS = load_picks()
players = SCHEDULE['players']

def get_team(line):
	""" Look for a match of pattern from the (patterns, team) tuple to the line arg. 
	    If a match is found, return the associated team from the patterns tuple """
	for pattern, team in patterns:
		if re.search(pattern, line.upper()):
			return team

def get_team_long(line):
	""" Look for a match of pattern from the (patterns, team) tuple to the line arg. 
	    If a match is found, return the associated team from the patterns tuple """
	for pattern, team in patterns_long:
		if re.search(pattern, line.upper()):
			return team

def get_players(players_file):
	players = []
	with open(players_file, encoding='utf-8') as f:
		players = f.readlines()		
	players = [line.strip() for line in players]
	return players

def get_schedule(week=WEEK):
		""" Returns a list of the given week's schedule ['Away Home', 'Away Home',...] """
		return [away + ' ' + home for away, home in SCHEDULE['weeks'][week]['games']]

cur_week_sched = get_schedule()
cur_week_games = len(cur_week_sched)

def create_player_picks(player, week, player_picks):
  return {
		'week': week,
		'player': player,
		'picks': player_picks
	}

def player_week_key(player, week):
  return json.dumps([player, week], separators=',:')

def init_player_picks(player, week=WEEK):
  """ returns a blank picks list for a single player for a single week """
  game_count = len(get_schedule(week))
  player_picks = ['' for i in range(game_count)]
  player_picks = create_player_picks(player, week, player_picks)
  return player_picks
	
def init_picks():
	""" results in the current week getting initialized """
	return {player_week_key(player, week): init_player_picks(player, week)
			for week in [WEEK] for player in players}

def dump_picks(picks=PICKS, path=cp_init.JSON_PATH):
	""" Serialize the picks object to the picks json file. 
	    path is the absolute path to the json file """
	with open(path, 'w') as f:
		json.dump(picks, f)

def get_player_picks(player, path=cp_init.JSON_PATH, picks=PICKS, week=WEEK):
	""" Gets a single player's picks for a given week. 
	    path is the absolute path to the json file """
	return picks[player_week_key(player, week)]

def save_player_picks(player_picks, path=cp_init.JSON_PATH, picks=PICKS):
	""" Saves a single player's picks for a given week. 
	    path is the absolute path to the json file """
	picks[player_week_key(player_picks['player'], player_picks['week'])] = player_picks
	dump_picks(picks, path)
	
def gen_random_results(week=WEEK):
	""" Returns random game results for a given week
	    Used internally for testing and development """
	if week != WEEK:
		s = get_schedule(week) 
	else: s = cur_week_sched
	r = [random.choice(list(s[i].split())) for i in range(len(s))]
	return r

results = gen_random_results()  

def load_random_players_picks(week=WEEK):
	""" Saves random picks for all players for a given week.
		Used internally for testing and development """
	if week != WEEK:
		s = get_schedule(week) 
	else: s = cur_week_sched
	for player in players:
		player_picks = [random.choice(list(s[i].split())) for i in range(len(s))]
		random.shuffle(player_picks)
		player_picks = create_player_picks(player, week, player_picks)
		save_player_picks(player_picks)

def get_score(player, week=WEEK):
	score = 0
	if week != WEEK:
		s = get_schedule(week) 
	else: s = cur_week_sched
	weights = [i for i in range(MAX,MAX-len(s),-1)]
	#results = gen_random_results(week) # for testing and dev. replace with actual game results
	player_picks = get_player_picks(player, week=week)
	for i in range(len(weights)): 
		if player_picks['picks'][i] in results:
			score += weights[i]
	return score

def get_sorted_scores(week=WEEK):
	""" Returns list of (player, score) tuples sorted in decending order by player's score """
	scores = sorted([(player,get_score(player, week)) for player in players], key=lambda x: x[1], reverse=True)
	return scores

def write_picks_file(picks=PICKS, week=WEEK):
	""" Create a file suitable for importing a week's worth of picks to Excel """
	transposed = [[value['player']] + value['picks'] for _, value in sorted(picks.items()) if value['week'] == week]
	for i in range(len(players)):
		for j in range(1,cur_week_games+1):
			transposed[i][j] = get_team(transposed[i][j])
	with open('picks.txt', mode='w', encoding='utf-8') as picks_file:
		for row in zip(*transposed):
			picks_file.write('\t'.join(row) + '\n')

emailToName = {}
with open(cp_init.XREF_PATH, encoding='utf-8') as f:
	emailToName = {k:v for line in f for tokens in 
			[line.strip().split('\t', 1)] for k,v in [tokens]}

def in_schedule(team):
	""" checks if team arg is in the cur week schedule
	returns team if true else returns ''  """
	state = False
	for i in range(cur_week_games):
		state = state or team in cur_week_sched[i]
	return state

def picked_count(team, picks):
	count = 0
	for i in range(len(picks)):
		count += team in picks[i]
	return count

def get_opponent(team):
	for i in range(cur_week_games):
		if team in cur_week_sched[i]:
			away, home = cur_week_sched[i].split()
			if team == away:
				return home
			return away

def played_both_sides(team, picks):
	t = get_opponent(team)
	if t in picks:
		return True
	return False

def check_for_valid(picks):
	for i in range(len(picks)):
		if not in_schedule(picks[i]) or picked_count(picks[i], picks) > 1 \
		or played_both_sides(picks[i], picks):
			picks[i] = ''
	return picks

def read_picks_from_file():
	lines = []
	picks = []
	for filename in os.listdir(cp_init.EMAIL_PATH):
		if '.txt' in filename:
			with open(os.path.join(cp_init.EMAIL_PATH, filename), encoding='utf-8') as f:
				lines = f.readlines()
				filename = filename[:-4]
				playername = emailToName[filename]
				picks = [get_team_long(l) for l in lines]
				picks = check_for_valid(picks)
				picks = create_player_picks(playername, WEEK, picks)
				save_player_picks(picks)