import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
import os
import calendar
import copy
import sys
import argparse
import datetime
import operator
import re
import csv

from wordcloud import WordCloud
from PIL import Image

# volume_tweet = { year : { month : [number_of_tweets, number_of_retweets, replies, hearts, retweets, quotes] } }
volume_tweet = {}
year = {}
for k in range(12):
	year[k+1] = [0, 0, 0, 0, 0, 0]

# daily_rhytm = { day : { hour: number_of_tweets } }
day = {}
for k in range(24):
	day[k] = 0
daily_rhytm = {}
for k in range(7):
	daily_rhytm[k] = copy.deepcopy(day)

# volume_creation = { year : { month : number_of_created_accounts } }
volume_creation = {}
creation_year = {}
for k in range(12):
	creation_year[k+1] = 0

# user_agent = { client : number }
user_agent = {}
# retweeted_user = { retweeted user : number }
retweeted_user = {}
# hashtag = { hashtag : number }
hashtag = {}

# It is a only a counter
account_count = []

def tweet_analysis(language_tweet, language_user, path_csv, volume_tweet, daily_rhytm, volume_creation, user_agent, retweeted_user, hashtag, account_count):
	data = pd.read_csv(path_csv, header=0, low_memory=False)
	user_screen_name = list(data.user_screen_name)
	account_creation_date = list(data.account_creation_date)
	account_language = list(data.account_language)
	tweet_language = list(data.tweet_language)
	tweet_time = list(data.tweet_time)
	tweet_text = list(data.tweet_text)
	is_retweet = list(data.is_retweet)
	hashtags = list(data.hashtags)
	tweet_client_name = list(data.tweet_client_name)
	is_retweet = list(data.is_retweet)
	account_creation_date = list(data.account_creation_date)
	reply_count = list(data.reply_count)
	like_count = list(data.like_count)
	retweet_count = list(data.retweet_count)
	quote_count = list(data.quote_count)

	def tweet_data():
		if int(tweet_time[i][:4]) in volume_tweet:
			if str(is_retweet[i]).lower() == 'false':
				volume_tweet[int(tweet_time[i][:4])][int(tweet_time[i][5:7])][0] += 1
			else:
				volume_tweet[int(tweet_time[i][:4])][int(tweet_time[i][5:7])][1] += 1
			if str(reply_count[i]).lower() != 'nan':
				volume_tweet[int(tweet_time[i][:4])][int(tweet_time[i][5:7])][2] += int(reply_count[i])
			if str(like_count[i]).lower() != 'nan':
				volume_tweet[int(tweet_time[i][:4])][int(tweet_time[i][5:7])][3] += int(like_count[i])
			if str(retweet_count[i]).lower() != 'nan':
				volume_tweet[int(tweet_time[i][:4])][int(tweet_time[i][5:7])][4] += int(retweet_count[i])
			if str(quote_count[i]).lower() != 'nan':
				volume_tweet[int(tweet_time[i][:4])][int(tweet_time[i][5:7])][5] += int(quote_count[i])
		else:
			year_array = copy.deepcopy(year)
			if str(is_retweet[i]).lower() == 'false':
				year_array[int(tweet_time[i][5:7])][0] += 1
			else:
				year_array[int(tweet_time[i][5:7])][1] += 1
			if str(reply_count[i]).lower() != 'nan':
				year_array[int(tweet_time[i][5:7])][2] += int(reply_count[i])
			if str(like_count[i]).lower() != 'nan':
				year_array[int(tweet_time[i][5:7])][3] += int(like_count[i])
			if str(retweet_count[i]).lower() != 'nan':
				year_array[int(tweet_time[i][5:7])][4] += int(retweet_count[i])
			if str(quote_count[i]).lower() != 'nan':
				year_array[int(tweet_time[i][5:7])][5] += int(quote_count[i])
			volume_tweet[int(tweet_time[i][:4])] = year_array

		dt = str(tweet_time[i][:10])
		year_t, month_t, day_t = (int(x) for x in dt.split('-'))
		tweet_day = datetime.datetime(year_t, month_t, day_t).weekday()
		daily_rhytm[tweet_day][int(tweet_time[i][11:13])] += 1

		if language_tweet == 'all':
			if str(user_screen_name[i]) not in account_count:
				if int(account_creation_date[i][:4]) in volume_creation:
					volume_creation[int(account_creation_date[i][:4])][int(account_creation_date[i][5:7])] += 1
				else:
					creation_array = copy.deepcopy(creation_year)
					creation_array[int(account_creation_date[i][5:7])] += 1
					volume_creation[int(account_creation_date[i][:4])] = creation_array
				account_count.append(str(user_screen_name[i]))

		if str(tweet_client_name[i]) in user_agent:
			user_agent[str(tweet_client_name[i])] += 1
		else:
			user_agent[str(tweet_client_name[i])] = 1
		
		if str(is_retweet[i]).lower() == 'true':
			position = tweet_text[i].find(':')
			user_original = str(tweet_text[i][4:position])
			if user_original in retweeted_user:
				retweeted_user[user_original] += 1
			else:
				retweeted_user[user_original] = 1

		punct = set(['[',']','#','\''])
		if str(hashtags[i]).lower() != 'nan':
			var = ''.join(x.lower() for x in str(hashtags[i]) if x not in punct)
			var_list = var.split(', ')
			var_list = list(set(var_list)) ## Remove duplicates
			for element in var_list:
				if element != '':
					if str(element) in hashtag:
						hashtag[str(element)] += 1
					else:
						hashtag[str(element)] = 1

	i = 0
	while i < len(user_screen_name):
		if language_tweet != 'all':
			if str(tweet_language[i]) == language_tweet:
				tweet_data()
		elif language_user != 'all':
			if str(account_language[i]) == language_user:
				tweet_data()
		else:
			tweet_data()
		i += 1

	if volume_tweet != {}:
		volume_years = sorted(volume_tweet.keys())
		j = 0
		while j+1 < len(volume_years):
			if volume_years[j+1] - volume_years[j] > 1:
				year_array = copy.deepcopy(year)
				volume_tweet[volume_years[j]+1] = year_array
			j += 1
	if volume_creation != {}:
		volume_years = sorted(volume_creation.keys())
		j = 0
		while j+1 < len(volume_years):
			if volume_years[j+1] - volume_years[j] > 1:
				year_array = copy.deepcopy(creation_year)
				volume_creation[volume_years[j]+1] = year_array
			j += 1
	return([volume_tweet, daily_rhytm, volume_creation, user_agent, retweeted_user, hashtag, account_count])

def volume_tweet_plot(volume, language):
	volume_years = sorted(volume.keys())
	y1 = [] # retweets
	y2 = [] # tweets
	x_label = []
	for key in volume_years:
		for k in range(12):
			if (k+1) % 3 == 1:
				x_label.append(calendar.month_abbr[k+1] + ' \'' + str(key)[2:])
			y1.append(volume[key][k+1][1])
			y2.append(volume[key][k+1][0])
	x = np.arange(len(y1))
	plt.plot(x, y1, label='retweet', color='green', markersize=2)
	plt.plot(x, y2, label='tweet', color='skyblue', markersize=2)
	plt.xticks(np.arange(0, len(y1), 3), x_label, rotation=45, fontsize=5)
	plt.legend()
	plt.savefig(language + '_volume_tweet.png', bbox_inches='tight', dpi=250)
	plt.close()

def volume_interaction_plot(volume, language):
	volume_years = sorted(volume.keys())
	y1 = [] # quotes
	y2 = [] # replies
	y3 = [] # retweets
	y4 = [] # hearts
	x_label = []
	for key in volume_years:
		for k in range(12):
			if (k+1) % 3 == 1:
				x_label.append(calendar.month_abbr[k+1] + ' \'' + str(key)[2:])
			y1.append(volume[key][k+1][5])
			y2.append(volume[key][k+1][2])
			y3.append(volume[key][k+1][4])
			y4.append(volume[key][k+1][3])
	x = np.arange(len(y1))
	plt.plot(x, y1, label='quote', color='purple', markersize=2)
	plt.plot(x, y2, label='reply', color='skyblue', markersize=2)
	plt.plot(x, y3, label='retweet', color='green', markersize=2)
	plt.plot(x, y4, label='heart', color='red', markersize=2)
	plt.xticks(np.arange(0, len(y1), 3), x_label, rotation=45, fontsize=5)
	plt.legend()
	plt.savefig(language + '_volume_interactions.png', bbox_inches='tight', dpi=250)
	plt.close()

def daily_rhythm_plot(week_rhythm, language):
	week = []
	for k in range(7):
		day = []
		for j in range(24):
			day.append(week_rhythm[k][j])
		week.append(day)
	df = pd.DataFrame(week, columns=['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23'])
	plt.figure(figsize=(10,5))
	sns.heatmap(df, yticklabels=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], annot=False, linewidths=.5)
	plt.savefig(language + '_density.png', bbox_inches='tight', dpi=200)
	plt.close()

def creation_plot(volume, language):
	volume_years = sorted(volume.keys())
	y1 = []
	x_label = []
	for key in volume_years:
		for k in range(12):
			if (k+1) % 3 == 1:
				x_label.append(calendar.month_abbr[k+1] + ' \'' + str(key)[2:])
			y1.append(volume[key][k+1])
	x = np.arange(len(y1))
	plt.bar(x, y1)
	plt.xticks(np.arange(0, len(y1), 3), x_label, rotation=45, fontsize=5)
	plt.savefig(language + '_creation_date.png', bbox_inches='tight', dpi=250)
	plt.close()

def twitter_user_agent_plot(user_agent, language):
	sorted_user_agent = sorted(user_agent.items(), key=operator.itemgetter(1))[::-1]
	height = [] # numbers
	bars = [] # twitter clients
	barWidth = 0.5
	if len(sorted_user_agent) <= 30:
		for item in sorted_user_agent:
			height.append(item[1])
			bars.append(item[0])
	else:
		for item in sorted_user_agent[:30]:
			height.append(item[1])
			if len(item[0]) < 30:
				bars.append(item[0])
			else:
				bars.append(item[0][:30] + '[...]')
		k = 0
		for item in sorted_user_agent[30:]:
			k += item[1]
		height.append(k)
		bars.append('Others: {}'.format(str(k)))
	y_pos = np.arange(len(bars))
	plt.bar(y_pos, height, color='#2196f3', edgecolor='#64b5f6', width=barWidth)
	plt.xticks(y_pos, bars, rotation=90, fontsize=5)
	plt.xlabel('Twitter clients')
	plt.ylabel('# Tweets')
	plt.tight_layout()
	plt.savefig(language + '_user_agent.png', bbox_inches='tight', dpi=200)
	plt.close()

def wordcloud(words, language, gradient, title):
	twitter_mask = np.array(Image.open('twitter_mask.png'))
	text = ''
	for key in words:
		for item in range(words[key]):
			text = text + str(key) + ' '
	if gradient == 'winter':
		wordcloud = WordCloud(mask=twitter_mask, colormap=matplotlib.cm.winter, background_color="white", collocations=False).generate(text)
	else:
		wordcloud = WordCloud(mask=twitter_mask, colormap=matplotlib.cm.tab10, background_color="white", collocations=False).generate(text)
	plt.figure(figsize=(12.8,9.6), dpi=100)
	plt.imshow(wordcloud, interpolation="bilinear")
	plt.axis('off')
	plt.tight_layout()
	plt.savefig(language + '_' + title + '.png')
	plt.close()

parser = argparse.ArgumentParser(description='Twitter dataset tweets\' analysis')
parser.add_argument('--path', nargs='*', help='Path of Twitter dataset')
group = parser.add_mutually_exclusive_group()
group.add_argument('--tlang', default='all', help='Language of tweets to analyse')
group.add_argument('--ulang', default='all', help='Language of accounts to analyse')
parser.add_argument('-csv', required=False, action='store_true', help='Save info into csv files')
args = parser.parse_args()
try:
	print("\x1b[1;34;49m" + "\n\n                 ./oss+:    -\n /d:           .hMMMMMMMNydm/`\n hMMd+`       `NMMMMMMMMMMNdy-\n /MMMMMds/-`  /MMMMMMMMMMMN-         \n .+mMMMMMMMMNmmMMMMMMMMMMMm\n sMNMMMMMMMMMMMMMMMMMMMMMMs\n  sMMMMMMMMMMMMMMMMMMMMMMN.\n   -smMMMMMMMMMMMMMMMMMMM/\n   .dMMMMMMMMMMMMMMMMMMN:\n     :ydNMMMMMMMMMMMMMh.\n     `:omMMMMMMMMMMMy-\n./ymNMMMMMMMMMMMmy/`\n   `-/+ssssso/-`\n" + "\x1b[0m")
	print("\x1b[1;39;49m" + "  Made with" + "\x1b[0m" + "\x1b[1;31;49m" + " ❤" + "\x1b[0m" + "\x1b[1;39;49m" + " - https://www.github.com/luigigubello" + "\x1b[0m\n\n")
	print('\x1b[1;39;49m' + 'Wait...' + '\x1b[0m')
	for item in args.path:
		vector = tweet_analysis(args.tlang, args.ulang, item, volume_tweet, daily_rhytm, volume_creation, user_agent, retweeted_user, hashtag, account_count)
		volume_tweet = vector[0]
		daily_rhytm = vector[1]
		volume_creation = vector[2]
		user_agent = vector[3]
		retweeted_user = vector[4]
		hashtag = vector[5]
		account_count = vector[6]

	if volume_tweet != {}:
		lang = ''
		if args.tlang != 'all':
			lang = args.tlang
		else:
			lang = args.ulang
		volume_tweet_plot(volume_tweet, lang)
		volume_interaction_plot(volume_tweet, lang)
		daily_rhythm_plot(daily_rhytm, lang)
		if args.tlang == 'all':
			creation_plot(volume_creation, lang)
		twitter_user_agent_plot(user_agent, lang)
		wordcloud(retweeted_user, lang, 'winter', 'retweeted_user')
		wordcloud(hashtag, lang, 'tab10', 'hashtag')
		
		if args.csv == True:
			sorted_volume = sorted(volume_tweet.items(), key=operator.itemgetter(0))
			with open('volume.csv','wt') as out:
				csv_out=csv.writer(out)
				csv_out.writerow(['year','tweets', 'retweets', 'generated_hearts', 'generated_retweets', 'generated_replies', 'generated_quotes'])
				for item in sorted_volume:
					tweets = 0
					retweets = 0
					generated_hearts = 0
					generated_retweets = 0
					generated_replies = 0
					generated_quotes = 0
					for key in item[1]:
						tweets += item[1][key][0]
						retweets += item[1][key][1]
						generated_hearts += item[1][key][3]
						generated_retweets += item[1][key][4]
						generated_replies += item[1][key][2]
						generated_quotes += item[1][key][5]
					csv_out.writerow([item[0], tweets, retweets, generated_hearts, generated_retweets, generated_replies, generated_quotes])
			sorted_user_agent = sorted(user_agent.items(), key=operator.itemgetter(1))[::-1]
			with open('clients.csv','wt') as out:
				csv_out=csv.writer(out)
				csv_out.writerow(['twitter_client','times'])
				for item in sorted_user_agent:	
					csv_out.writerow(item)
			sorted_retweeted_user = sorted(retweeted_user.items(), key=operator.itemgetter(1))[::-1]
			with open('retweeted_users.csv','wt') as out:
				csv_out=csv.writer(out)
				csv_out.writerow(['retweeted_user','times'])
				for item in sorted_retweeted_user:	
					csv_out.writerow(item)
			sorted_hashtag = sorted(hashtag.items(), key=operator.itemgetter(1))[::-1]
			with open('hashtags.csv','wt') as out:
				csv_out=csv.writer(out)
				csv_out.writerow(['hashtags','times'])
				for item in sorted_hashtag:	
					csv_out.writerow(item)
	else:
		print('\x1b[1;39;49m' + 'This language is not in the dataset' + '\x1b[0m')
	print('\x1b[1;39;49m' + 'Done!' + '\x1b[0m')
except KeyboardInterrupt:
	print('\x1b[1;39;49m' + '\n\nGoodbye\n' + '\x1b[0m')
	exit(0)
