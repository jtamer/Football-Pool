# sys.path.insert(0,'/Users/jimtamer/Modules/Football')

import re
import pickle
import random
import cp_init

def get_weeks():
	with open(cp_init.SCHED_PATH, encoding='utf-8') as f:
		s = f.readlines()
		s = [x.strip() for x in s]
		return len([x for x in s if 'Week' in x])

WEEKS = get_weeks()
weeks = ['Week'+str(i+1) for i in range(WEEKS)] 
WEEK = cp_init.CUR_WEEK  

patterns = []
with open(cp_init.PATTERNS_PATH, encoding='utf-8') as f:
	patterns = f.readlines()
	patterns = [line.strip() for line in patterns]	
	patterns = tuple(eval(line) for line in patterns) 
	
MAX = int(len({patterns[i][1] for i in range(len(patterns))}) / 2) # max score for the top pick  e.g. 16. 
	
players = []
with open(cp_init.PLAYERS_PATH, encoding='utf-8') as f:
	players = f.readlines()		
	players = [line.strip() for line in players]

def get_team(line):
	""" Look for a match of pattern from the (patterns, team) tuple to the line arg. 
	    If a match is found, return the associated team from the patterns tuple """
	for pattern, team in patterns:
		if re.search(pattern, line.upper()):
			return team

def fetch_players():
	return players
	
def get_players(players_file):
	players = []
	with open(players_file, encoding='utf-8') as f:
		players = f.readlines()		
	players = [line.strip() for line in players]
	return players
	 
def get_schedule(week=WEEK, schedule_file=cp_init.SCHED_PATH):
		""" Returns a list of the given week's schedule ['Away Home', 'Away Home',...] """
		schedule = []
		week_num = int(week[4:])
		with open(schedule_file, encoding='utf-8') as f:
			schedule = f.readlines()
			schedule = [x.strip() for x in schedule]
			i = schedule.index(week)
			schedule = schedule[i+1:]
			if "Week" in str(schedule):
				j = schedule.index("Week"+str(week_num+1))
				schedule = schedule[:j]
				schedule.remove('')
			schedule = [x.split() for x in schedule]
			l = len(schedule)
			schedule = [str(schedule[i][0]) + ' ' + str(schedule[i][1]) for i in range(l)]
			return schedule

cur_week_sched = get_schedule()
cur_week_games = len(cur_week_sched)

def create_player_picks(player, week, picks):
  return {
		'week': week,
		'player': player,
		'picks': picks
	}

def init_player_picks(player, week=WEEK):
  """ returns a blank picks list for a single player for a single week """
  game_count = len(get_schedule(week))
  picks = ['' for i in range(game_count)]
  player_picks = create_player_picks(player, week, picks)
  return player_picks
	
def init_picks():
	""" results in the entire season getting initialized """
	return {(player, week): init_player_picks(player, week)
			for week in weeks for player in fetch_players()}

def dump_picks(picks, path=cp_init.PKL_PATH):
	""" Serialize the picks object to the picks pickle file. 
	    path is the absolute path to the pickle file """
	with open(path, 'wb') as f:
		pickle.dump(picks, f)
		
def load_picks(path=cp_init.PKL_PATH):
	""" Deserialize the picks from the picks pickle file. 
	    path is the absolute path to the pickle file """
	with open(path, 'rb') as f:
		picks = pickle.load(f)
		return picks
		
def get_picks(player, path=cp_init.PKL_PATH, week=WEEK):
	""" Gets a single player's picks for a given week. 
	    path is the absolute path to the pickle file """
	picks = load_picks(path)  # ordered by week then by player, wk1 plr1, wk1 plr2,..., wk17 plr42
	return picks[(player, week)]
	
def save_picks(player_picks, path=cp_init.PKL_PATH):
	""" Saves a single player's picks for a given week. 
	    path is the absolute path to the pickle file """
	picks = load_picks(path) 
	picks[(player_picks['player'], player_picks['week'])] = player_picks
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
		picks = [random.choice(list(s[i].split())) for i in range(len(s))]
		random.shuffle(picks)
		picks = create_player_picks(player, week, picks)
		save_picks(picks, cp_init.PKL_PATH)		

def get_score(player, week=WEEK):
	score = 0
	if week != WEEK:
		s = get_schedule(week) 
	else: s = cur_week_sched
	weights = [i for i in range(MAX,MAX-len(s),-1)]
	#results = gen_random_results(week) # for testing and dev. replace with actual game results
	picks = get_picks(player, cp_init.PKL_PATH, week)
	for i in range(len(weights)): 
		if picks[i+1] in results:
			score += weights[i]
	return score

def get_sorted_scores(week=WEEK):
	""" Returns list of (player, score) tuples sorted in decending order by player's score """
	scores = sorted([(player,get_score(player, week)) for player in players], key=lambda x: x[1], reverse=True)
	return scores

def write_picks_file(picks, week=WEEK):
  """ Create a file suitable for importing a week's worth of picks to Excel """
  transposed = [[player] + value['picks']
      for (player, p_week), value in picks.items() if p_week == week]
  with open('picks.txt', mode='w', encoding='utf-8') as picks_file:
    for row in zip(*transposed):
      picks_file.write('\t'.join(row) + '\n')
