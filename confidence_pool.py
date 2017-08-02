# sys.path.insert(0,'/Users/jimtamer/Modules/Football')

import re
import pickle
import random
import cp_init

WEEKS = cp_init.TOT_WEEKS
weeks = ['Week'+str(i+1) for i in range(WEEKS)]
WEEK = cp_init.CUR_WEEK

MAX = cp_init.MAX  # max score for the top pick. 

patterns = []
with open(cp_init.PATTERNS_PATH, encoding='utf-8') as f:
	patterns = f.readlines()
	patterns = [line.strip() for line in patterns]	
	patterns = tuple(eval(line) for line in patterns)
	
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

def init_player_picks(player, week=WEEK):
	""" returns a blank picks list for a single player for a single week """
	game_count = len(get_schedule(week))
	player_picks = [([week] + [player])] + ['' for i in range(game_count)]
	return player_picks
	
def init_picks():
	""" results in the entire season getting initialized """
	return [init_player_picks(player, week) for week in weeks for player in fetch_players()]

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
	w_indx = weeks.index(week)
	p_indx = players.index(player)
	return picks[(w_indx*len(players)) + p_indx]
	
def save_picks(player_picks, path=cp_init.PKL_PATH):
	""" Saves a single player's picks for a given week. 
	    path is the absolute path to the pickle file """
	picks = load_picks(path) 
	w_indx = weeks.index(player_picks[0][0])
	p_indx = players.index(player_picks[0][1])
	picks[(w_indx*len(players)) + p_indx] = player_picks
	dump_picks(picks, path)
	
def gen_random(week=WEEK):
	""" Returns random game results for a given week
	    Used internally for testing and development """
	if week != WEEK:
		s = get_schedule(week) 
	else: s = cur_week_sched
	r = [random.choice(list(s[i].split())) for i in range(len(s))]
	return r

results = gen_random()  

def load_random_players_picks(week=WEEK):
	""" Saves random picks for all players for a given week.
		Used internally for testing and development """
	if week != WEEK:
		s = get_schedule(week) 
	else: s = cur_week_sched
	for player in players:
		picks = [random.choice(list(s[i].split())) for i in range(len(s))]
		picks = [[week,player]] + picks
		save_picks(picks, cp_init.PKL_PATH)		

def load_random_player_picks(player, week=WEEK):
	""" Saves random picks for one player for a given week.
		Used internally for testing and development """
	if week != WEEK:
		s = get_schedule(week) 
	else: s = cur_week_sched
	picks = [random.choice(list(s[i].split())) for i in range(len(s))]
	picks = [[week,player]] + picks
	save_picks(picks, cp_init.PKL_PATH)		

def get_score(player, week=WEEK):
	score = 0
	if week != WEEK:
		s = get_schedule(week) 
	else: s = cur_week_sched
	weights = [i for i in range(MAX,MAX-len(s),-1)]
	#results = gen_random(week) # for testing and dev. replace with actual game results
	picks = get_picks(player, cp_init.PKL_PATH, week)
	for i in range(len(weights)): 
		if results[i] == picks[i+1]:
			score += weights[i]
	return score

def get_sorted_scores(week=WEEK):
	""" Returns list of (player, score) tuples sorted in decending order by player's score """
	scores = sorted([(player,get_score(player, week)) for player in players], key=lambda x: x[1], reverse=True)
	return scores

def write_picks_file(picks):
	""" Create a file suitable for importing a week's worth of picks to Excel """
	with open('picks.txt', mode='w', encoding='utf-8') as picks_file:
		line = ''
		# Write player names across 1st line
		for i in range(len(picks)):
			line += str(picks[i][0][1]) + '\t' 	
		line += '\n'
		picks_file.write(line)
		line = ''
		# for each [pick] in [picks], get the jth item and append it to the line
		l = len(picks[0])  # each [pick] in [picks] is the same length
		for j in range(1,l):
			for i in range(len(picks)):  # 0, 41
				line += str(picks[i][j]) + '\t'
			line += '\n'
			picks_file.write(line)
			line = ''
		