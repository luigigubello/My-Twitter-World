import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
import os
import calendar
import copy
import sys
import argparse
import datetime
import operator

def user_analysis(username, path_csv):
	data = pd.read_csv(path_csv, header=0, low_memory=False)
	user_screen_name = list(data.user_screen_name)
	tweet_time = list(data.tweet_time)
	is_retweet = list(data.is_retweet)
	account_creation_date = list(data.account_creation_date)

	volume_tweet = [] # [year, [..., [month, number_of_tweets, number_of_retweets], ...]]
	year = [[1, 0, 0], [2, 0, 0], [3, 0, 0], [4, 0, 0], [5, 0, 0], [6, 0, 0], [7, 0, 0], [8, 0, 0], [9, 0, 0], [10, 0, 0], [11, 0, 0], [12, 0, 0]]
	day = [[0, 0],[1, 0],[2, 0],[3, 0],[4, 0],[5, 0],[6, 0],[7, 0],[8, 0],[9, 0],[10, 0],[11, 0],[12, 0],[13, 0],[14, 0],[15, 0],[16, 0],[17, 0],[18, 0],[19, 0],[20, 0],[21, 0],[22, 0],[23, 0]]
	daily_rhytm = [] # [day, [..., [hour, number_of_tweets], ...]]
	k = 0
	while k < 7:
		daily_rhytm.append([k, copy.deepcopy(day)])
		k += 1
	i = 0
	while i < len(user_screen_name):
		if str(user_screen_name[i]) == username:
			if volume_tweet == []:
				year_array = copy.deepcopy(year)
				for month in year_array:
					if month[0] == int(tweet_time[i][5:7]):
						if str(is_retweet[i]) == 'False' or str(is_retweet[i]) == 'false':
							month[1] += 1
						else:
							month[2] += 1
						break
				volume_tweet.append([int(tweet_time[i][:4]), year_array])
			else:
				k = 0
				for element in volume_tweet:
					if int(element[0]) == int(tweet_time[i][:4]):
							for month in element[1]:
								if month[0] == int(tweet_time[i][5:7]):
									if str(is_retweet[i]) == 'False' or str(is_retweet[i]) == 'false':
										month[1] += 1
									else:
										month[2] += 1
									k = 1
									break
				if k == 0:
					year_array = copy.deepcopy(year)
					for month in year_array:
						if month[0] == int(tweet_time[i][5:7]):
							if str(is_retweet[i]) == 'False' or str(is_retweet[i]) == 'false':
								month[1] += 1
							else:
								month[2] += 1
							break
					volume_tweet.append([int(tweet_time[i][:4]), year_array])


			dt = str(tweet_time[i][:10])
			year_t, month_t, day_t = (int(x) for x in dt.split('-'))
			for item in daily_rhytm:
				if item[0] == datetime.datetime(year_t, month_t, day_t).weekday():
					for hour in item[1]:
						if hour[0] == int(tweet_time[i][11:13]):
							hour[1] += 1
							break
					break
		i += 1
	if volume_tweet != []:
		volume_tweet = sorted(volume_tweet, key=operator.itemgetter(0))
		j = 0
		while j+1 < len(volume_tweet):
			if volume_tweet[j+1][0] - volume_tweet[j][0] > 1:
				year_array = copy.deepcopy(year)
				volume_tweet = volume_tweet[:j+1] + [[volume_tweet[j][0]+1, year_array]] + volume_tweet[j+1:]
			j += 1
	return([volume_tweet, daily_rhytm])

def volume_tweet(volume, username):
	y1 = []
	y2 = []
	x_label = []
	for element in volume:
		for elem in element[1]:
			if elem[0] % 3 == 1:
				x_label.append(calendar.month_abbr[elem[0]] + ' \'' + str(element[0])[2:])
			y1.append(elem[2])
			y2.append(elem[1])
	x = np.arange(len(y1))
	plt.plot(x, y1, label='retweet', color='green', markersize=2)
	plt.plot(x, y2, label='tweet', color='skyblue', markersize=2)
	plt.xticks(np.arange(0, len(y1), 3), x_label, rotation=45, fontsize=5)
	plt.legend()
	plt.savefig(username + '_tweet_date_list.png', bbox_inches='tight', dpi=200)
	plt.close()

def daily_rhytm(week_rhytm, username):
	week = []
	for element in week_rhytm:
		day = []
		for hour in element[1]:
			day.append(hour[1])
		week.append(day)
	df = pd.DataFrame(week, columns=['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23'])
	plt.figure(figsize=(10,5))
	sns.heatmap(df, yticklabels=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], annot=False, linewidths=.5)
	plt.savefig(username + '_density.png', bbox_inches='tight', dpi=100)
	plt.close()

parser = argparse.ArgumentParser(description='Twitter dataset users\' analysis')
parser.add_argument('username', type=str, help='username of account to analyse')
parser.add_argument('path', type=str, help='Path of Twitter dataset')
args = parser.parse_args()
try:
	print("\x1b[1;34;49m" + "\n\n                 ./oss+:    -\n /d:           .hMMMMMMMNydm/`\n hMMd+`       `NMMMMMMMMMMNdy-\n /MMMMMds/-`  /MMMMMMMMMMMN-         \n .+mMMMMMMMMNmmMMMMMMMMMMMm\n sMNMMMMMMMMMMMMMMMMMMMMMMs\n  sMMMMMMMMMMMMMMMMMMMMMMN.\n   -smMMMMMMMMMMMMMMMMMMM/\n   .dMMMMMMMMMMMMMMMMMMN:\n     :ydNMMMMMMMMMMMMMh.\n     `:omMMMMMMMMMMMy-\n./ymNMMMMMMMMMMMmy/`\n   `-/+ssssso/-`\n" + "\x1b[0m")
	print("\x1b[1;39;49m" + "  Made with" + "\x1b[0m" + "\x1b[1;31;49m" + " ❤" + "\x1b[0m" + "\x1b[1;39;49m" + " - https://www.github.com/luigigubello" + "\x1b[0m\n\n")
	print('\x1b[1;39;49m' + 'Wait...' + '\x1b[0m')
	vectors = user_analysis(args.username, args.path)
	volume_tweet(vectors[0], args.username)
	daily_rhytm(vectors[1], args.username)
	print('\x1b[1;39;49m' + 'Done!' + '\x1b[0m')
except KeyboardInterrupt:
	print('\x1b[1;39;49m' + '\n\nGoodbye\n' + '\x1b[0m')
	exit(0)

	


				
			
			
