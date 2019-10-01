import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import calendar
import copy
import sys
import argparse
import datetime
import operator

def tweet_analysis(language, path_csv):
	data = pd.read_csv(path_csv, header=0, low_memory=False)
	user_screen_name = list(data.user_screen_name)
	tweet_language = list(data.tweet_language)
	tweet_time = list(data.tweet_time)
	is_retweet = list(data.is_retweet)
	account_creation_date = list(data.account_creation_date)
	reply_count = list(data.reply_count)
	like_count = list(data.like_count)
	retweet_count = list(data.retweet_count)
	quote_count = list(data.quote_count)

	volume_tweet = [] # [year, [..., [month, number_of_tweets, number_of_retweets, replies, hearts, retweets, quotes], ...]]
	year = [[1, 0, 0, 0, 0, 0, 0], [2, 0, 0, 0, 0, 0, 0], [3, 0, 0, 0, 0, 0, 0], [4, 0, 0, 0, 0, 0, 0], [5, 0, 0, 0, 0, 0, 0], [6, 0, 0, 0, 0, 0, 0], [7, 0, 0, 0, 0, 0, 0], [8, 0, 0, 0, 0, 0, 0], [9, 0, 0, 0, 0, 0, 0], [10, 0, 0, 0, 0, 0, 0], [11, 0, 0, 0, 0, 0, 0], [12, 0, 0, 0, 0, 0, 0]]

	def tweet_data():
		if volume_tweet == []:
			year_array = copy.deepcopy(year)
			for month in year_array:
				if month[0] == int(tweet_time[i][5:7]):
					if str(is_retweet[i]) == 'False' or str(is_retweet[i]) == 'false':
						month[1] += 1
					else:
						month[2] += 1
					if str(reply_count[i]) != 'nan' and str(reply_count[i]) != 'NaN':
						month[3] += int(reply_count[i])
					if str(like_count[i]) != 'nan' and str(like_count[i]) != 'NaN':
						month[4] += int(like_count[i])
					if str(retweet_count[i]) != 'nan' and str(retweet_count[i]) != 'NaN':
						month[5] += int(retweet_count[i])
					if str(quote_count[i]) != 'nan' and str(quote_count[i]) != 'NaN':
						month[6] += int(quote_count[i])
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
								if str(reply_count[i]) != 'nan' and str(reply_count[i]) != 'NaN':
									month[3] += int(reply_count[i])
								if str(like_count[i]) != 'nan' and str(like_count[i]) != 'NaN':
									month[4] += int(like_count[i])
								if str(retweet_count[i]) != 'nan' and str(retweet_count[i]) != 'NaN':
									month[5] += int(retweet_count[i])
								if str(quote_count[i]) != 'nan' and str(quote_count[i]) != 'NaN':
									month[6] += int(quote_count[i])
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
						if str(reply_count[i]) != 'nan' and str(reply_count[i]) != 'NaN':
							month[3] += int(reply_count[i])
						if str(like_count[i]) != 'nan' and str(like_count[i]) != 'NaN':
							month[4] += int(like_count[i])
						if str(retweet_count[i]) != 'nan' and str(retweet_count[i]) != 'NaN':
							month[5] += int(retweet_count[i])
						if str(quote_count[i]) != 'nan' and str(quote_count[i]) != 'NaN':
							month[6] += int(quote_count[i])
						break
				volume_tweet.append([int(tweet_time[i][:4]), year_array])

	i = 0
	while i < len(user_screen_name):
		if language == 'all':
			tweet_data()
		else:
			if str(tweet_language[i]) == language:
				tweet_data()
		i += 1
	if volume_tweet != []:
		volume_tweet = sorted(volume_tweet, key=operator.itemgetter(0))
		j = 0
		while j+1 < len(volume_tweet):
			if volume_tweet[j+1][0] - volume_tweet[j][0] > 1:
				year_array = copy.deepcopy(year)
				volume_tweet = volume_tweet[:j+1] + [[volume_tweet[j][0]+1, year_array]] + volume_tweet[j+1:]
			j += 1
	return(volume_tweet)

def volume_tweet_plot(volume, language):
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
	plt.savefig(language + '_volume_tweet.png', bbox_inches='tight', dpi=200)
	plt.close()

def volume_inreaction_plot(volume, language):
	y1 = []
	y2 = []
	y3 = []
	y4 = []
	x_label = []
	for element in volume:
		for elem in element[1]:
			if elem[0] % 3 == 1:
				x_label.append(calendar.month_abbr[elem[0]] + ' \'' + str(element[0])[2:])
			y1.append(elem[6])
			y2.append(elem[3])
			y3.append(elem[5])
			y4.append(elem[4])
	x = np.arange(len(y1))
	plt.plot(x, y1, label='quote', color='purple', markersize=2)
	plt.plot(x, y2, label='reply', color='skyblue', markersize=2)
	plt.plot(x, y3, label='retweet', color='green', markersize=2)
	plt.plot(x, y4, label='heart', color='red', markersize=2)
	plt.xticks(np.arange(0, len(y1), 3), x_label, rotation=45, fontsize=5)
	plt.legend()
	plt.savefig(language + '_volume_interactions.png', bbox_inches='tight', dpi=200)
	plt.close()

parser = argparse.ArgumentParser(description='Twitter dataset tweets\' analysis')
parser.add_argument('path', type=str, help='Path of Twitter dataset')
parser.add_argument('--lang', default='all', help='username of account to analyse')
args = parser.parse_args()
try:
	print("\x1b[1;34;49m" + "\n\n                 ./oss+:    -\n /d:           .hMMMMMMMNydm/`\n hMMd+`       `NMMMMMMMMMMNdy-\n /MMMMMds/-`  /MMMMMMMMMMMN-         \n .+mMMMMMMMMNmmMMMMMMMMMMMm\n sMNMMMMMMMMMMMMMMMMMMMMMMs\n  sMMMMMMMMMMMMMMMMMMMMMMN.\n   -smMMMMMMMMMMMMMMMMMMM/\n   .dMMMMMMMMMMMMMMMMMMN:\n     :ydNMMMMMMMMMMMMMh.\n     `:omMMMMMMMMMMMy-\n./ymNMMMMMMMMMMMmy/`\n   `-/+ssssso/-`\n" + "\x1b[0m")
	print("\x1b[1;39;49m" + "  Made with" + "\x1b[0m" + "\x1b[1;31;49m" + " ❤" + "\x1b[0m" + "\x1b[1;39;49m" + " - https://www.github.com/luigigubello" + "\x1b[0m\n\n")
	print('\x1b[1;39;49m' + 'Wait...' + '\x1b[0m')
	vector = tweet_analysis(args.lang, args.path)
	if vector != []:
		volume_tweet_plot(vector, args.lang)
		volume_inreaction_plot(vector, args.lang)
	else:
		print('\x1b[1;39;49m' + 'This language is not in the dataset' + '\x1b[0m')
	print('\x1b[1;39;49m' + 'Done!' + '\x1b[0m')
except KeyboardInterrupt:
	print('\x1b[1;39;49m' + '\n\nGoodbye\n' + '\x1b[0m')
	exit(0)

	


				
			
			
