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
import langcodes
import time

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

# volume_creation = { year : { month : number_of_created_accounts } } <-- ONLY ACTIVE ACCOUNTS
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
# language_tweet = { language : number_of_tweet }
language_dictionary = {}

# It is a only a counter
account_count = []

def tweet_analysis(language_tweet, language_user, verbose, path_csv, volume_tweet, daily_rhytm, volume_creation, user_agent, retweeted_user, hashtag, language_dictionary, account_count):
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
	reply_count = list(data.reply_count)
	like_count = list(data.like_count)
	retweet_count = list(data.retweet_count)
	quote_count = list(data.quote_count)
	language_count = {}
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
			if str(tweet_language[i]).lower() != 'nan' and str(tweet_language[i]).lower() != 'und': # Remove unclassified languages
				if str(tweet_language[i]) in language_count:
					language_count[str(tweet_language[i])] += 1
				else:
					language_count[str(tweet_language[i])] = 1

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
			var_list = list(set(var_list)) # Remove duplicates
			for element in var_list:
				if element != '':
					if str(element) in hashtag:
						hashtag[str(element)] += 1
					else:
						hashtag[str(element)] = 1

	i = 0
	if verbose == True:
		print('\x1b[1;39;49m' + 'Analysing the dataset {}, be patient...'.format(path_csv.split('/')[-1]) + '\x1b[0m')	
	while i < len(user_screen_name):
		if language_tweet != 'all':
			if str(tweet_language[i]) == language_tweet:
				tweet_data()
		elif language_user != 'all':
			if str(account_language[i]) == language_user:
				tweet_data()
		else:
			tweet_data()
		if verbose == True:
			if i%100000 == 0 and i != 0:
				print('\x1b[1;39;49m' + 'Analysed {} tweets'.format(i) + '\x1b[0m')
			if i == len(user_screen_name) - 1:
				print('\x1b[1;39;49m' + 'Analysed {} tweets'.format(i+1) + '\x1b[0m')				
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
	if language_count != {}:
		lang_keys = list(language_count)
		for item in lang_keys:
			lang_tw = langcodes.standardize_tag(item)
			new_key = langcodes.Language.make(language=lang_tw).language_name()
			language_count[new_key] = language_count[item]
			del language_count[item]
		lang_keys = list(language_count)
		for item in lang_keys:
			if item in language_dictionary:
				language_dictionary[item] += language_count[item]
			else:
				language_dictionary[item] = language_count[item]
	return([volume_tweet, daily_rhytm, volume_creation, user_agent, retweeted_user, hashtag, language_dictionary, account_count])

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

def barplot(dictionary, language, x_label, title):
	sorted_dictionary = sorted(dictionary.items(), key=operator.itemgetter(1))[::-1]
	height = [] # values of dict
	bars = [] # keys of dict
	barWidth = 0.5
	if len(sorted_dictionary) <= 30:
		for item in sorted_dictionary:
			height.append(item[1])
			bars.append(item[0])
	else:
		for item in sorted_dictionary[:30]:
			height.append(item[1])
			if len(item[0]) < 30:
				bars.append(item[0])
			else:
				bars.append(item[0][:30] + '[...]')
		k = 0
		for item in sorted_dictionary[30:]:
			k += item[1]
		height.append(k)
		bars.append('Others: {}'.format(str(k)))
	y_pos = np.arange(len(bars))
	plt.bar(y_pos, height, color='#2196f3', edgecolor='#64b5f6', width=barWidth)
	plt.xticks(y_pos, bars, rotation=90, fontsize=5)
	plt.xlabel(x_label)
	plt.ylabel('# Tweets')
	plt.tight_layout()
	plt.savefig(language + '_' + title + '.png', bbox_inches='tight', dpi=200)
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

def split(filename, dirname, number, v):
	if v == True:
		print('\x1b[1;39;49m' + 'Splitting the dataset, be patient...' + '\x1b[0m')
	cost = number
	first_line = ''
	k = 1
	i = number
	while (i == cost):
		with open(filename, newline='') as csvfilename:
			reader = csv.reader(csvfilename, delimiter=',', quotechar='"')
			i = 0
			allrows = []
			j = 0
			for row in reader:
				if i == number:
					break
				else:
					if j >= (k-1)*number:
						if first_line == '':
							first_line = row
						else:
							allrows.append(row)
						i += 1
				j += 1

		f = open(dirname + '/' + str(filename.split('/')[-1])+ str(k) + '.csv', 'w+', newline='')
		csvwriter = csv.writer(f)
		csvwriter.writerow(first_line)
		csvwriter.writerows(allrows)
		if v == True:
			if i == number:
				print('\x1b[1;39;49m' + 'Loading {} tweets'.format(k*number) + '\x1b[0m')
			else:
				print('\x1b[1;39;49m' + 'Loading {} tweets'.format((k-1)*number+i) + '\x1b[0m')
		k += 1

parser = argparse.ArgumentParser(description='Twitter disinformation datasets\' analysis')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--path', nargs='*', help='path of Twitter dataset')
group.add_argument('--dirpath', help='path of the directory cotaining Twitter dataset(s)')
group.add_argument('--split', nargs='*', help='split a CSV file in smaller CSV files, it can be slow')
parser.add_argument('--index', required=False, type=int, default=1000000, help='number of rows of each splitted CSV files')
group1 = parser.add_mutually_exclusive_group()
group1.add_argument('--tlang', default='all', help='language of tweets to analyse')
group1.add_argument('--ulang', default='all', help='language of accounts to analyse')
parser.add_argument('-w', required=False, action='store_true', help='large wordclouds are slow to build, so active this parameter only if you are patient')
parser.add_argument('-csv', required=False, action='store_true', help='save info into csv files')
parser.add_argument('-txt', required=False, action='store_true', help='save all details into txt files')
parser.add_argument('-v', required=False, action='store_true', help='verbose mode')
args = parser.parse_args()
try:
	print("\x1b[1;34;49m" + "\n\n                 ./oss+:    -\n /d:           .hMMMMMMMNydm/`\n hMMd+`       `NMMMMMMMMMMNdy-\n /MMMMMds/-`  /MMMMMMMMMMMN-         \n .+mMMMMMMMMNmmMMMMMMMMMMMm\n sMNMMMMMMMMMMMMMMMMMMMMMMs\n  sMMMMMMMMMMMMMMMMMMMMMMN.\n   -smMMMMMMMMMMMMMMMMMMM/\n   .dMMMMMMMMMMMMMMMMMMN:\n     :ydNMMMMMMMMMMMMMh.\n     `:omMMMMMMMMMMMy-\n./ymNMMMMMMMMMMMmy/`\n   `-/+ssssso/-`\n" + "\x1b[0m")
	print("\x1b[1;39;49m" + "  Made with" + "\x1b[0m" + "\x1b[1;31;49m" + " ❤" + "\x1b[0m" + "\x1b[1;39;49m" + " - https://www.github.com/luigigubello" + "\x1b[0m\n\n")
	print('\x1b[1;39;49m' + 'Wait...' + '\x1b[0m')
	if args.dirpath is not None:
		pwd = os.path.abspath(os.path.dirname(sys.argv[0]))
		if not os.path.exists(pwd + '/' + args.dirpath) and not os.path.exists(args.dirpath):
			print('\x1b[1;39;49m' + 'One or more files don\'t exist, check the path.' + '\x1b[0m')
			exit(0)
		else:
			if os.path.exists(pwd + '/' + args.dirpath) == True:
				fulldirname = pwd + '/' + args.dirpath
			else:
				fulldirname = args.dirpath
			list_csv = os.listdir(fulldirname)
			for item in list_csv:
				vector = tweet_analysis(args.tlang, args.ulang, args.v, fulldirname + '/' + item, volume_tweet, daily_rhytm, volume_creation, user_agent, retweeted_user, hashtag, language_dictionary, account_count)
				volume_tweet = vector[0]
				daily_rhytm = vector[1]
				volume_creation = vector[2]
				user_agent = vector[3]
				retweeted_user = vector[4]
				hashtag = vector[5]
				language_dictionary = vector[6]
				account_count = vector[7]
	if args.split is not None:
		pwd = os.path.abspath(os.path.dirname(sys.argv[0]))
		fulldirname = pwd + '/data_' + str(int(time.mktime(datetime.datetime.now().timetuple())))
		os.makedirs(fulldirname)
		for item in args.split:
			if not os.path.exists(pwd + '/' + item) and not os.path.exists(item):
				print('\x1b[1;39;49m' + 'One or more files don\'t exist, check the path.' + '\x1b[0m')	
				exit(0)
		for element in args.split:
			split(element, fulldirname, args.index, args.v)
		list_csv = os.listdir(fulldirname)
		for item in list_csv:
			vector = tweet_analysis(args.tlang, args.ulang, args.v, fulldirname + '/' + item, volume_tweet, daily_rhytm, volume_creation, user_agent, retweeted_user, hashtag, language_dictionary, account_count)
			volume_tweet = vector[0]
			daily_rhytm = vector[1]
			volume_creation = vector[2]
			user_agent = vector[3]
			retweeted_user = vector[4]
			hashtag = vector[5]
			language_dictionary = vector[6]
			account_count = vector[7]
	if args.path is not None:
		pwd = os.path.abspath(os.path.dirname(sys.argv[0]))
		for item in args.path:
			if not os.path.exists(pwd + '/' + item) and not os.path.exists(item):
				print('\x1b[1;39;49m' + 'One or more files don\'t exist, check the path.' + '\x1b[0m')	
				exit(0)
		for item in args.path:	
			vector = tweet_analysis(args.tlang, args.ulang, args.v, item, volume_tweet, daily_rhytm, volume_creation, user_agent, retweeted_user, hashtag, language_dictionary, account_count)
			volume_tweet = vector[0]
			daily_rhytm = vector[1]
			volume_creation = vector[2]
			user_agent = vector[3]
			retweeted_user = vector[4]
			hashtag = vector[5]
			language_dictionary = vector[6]
			account_count = vector[7]

	if volume_tweet != {}:
		if args.v == True:
			print('\x1b[1;39;49m' + 'Creating the graphs, the end is near!' + '\x1b[0m')
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
		barplot(user_agent, lang, 'Twitter clients', 'user_agent')
		if args.tlang == 'all':
			barplot(language_dictionary, lang, 'Tweets languages', 'tweets_language')
		
		if args.w == True:
			if args.v == True:
				print('\x1b[1;39;49m' + 'Creating the wordclouds, it is slow, be very patient...' + '\x1b[0m')
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
			sorted_language_tweet = sorted(language_dictionary.items(), key=operator.itemgetter(1))[::-1]
			with open('language_tweet.csv','wt') as out:
				csv_out=csv.writer(out)
				csv_out.writerow(['language_tweet','times'])
				for item in sorted_language_tweet:	
					csv_out.writerow(item)
		
		if args.txt == True:
			volume_tweet_interaction_txt = open('volume_tweet_interaction.txt','w+')
			volume_tweet_interaction_txt.write('Volume of tweets and interactions\n\n')
			volume_tweet_interaction_txt.write('# volume_tweet = { year : { month : [number_of_tweets, number_of_retweets, replies, hearts, retweets, quotes] } }\n\n')
			volume_tweet_interaction_txt.write(str(sorted(volume_tweet.items(), key=operator.itemgetter(0))))
			daily_rhythm_txt = open('daily_rhythm.txt', 'w+')
			daily_rhythm_txt.write('Daily rhythm\n\n')
			daily_rhythm_txt.write('# daily_rhytm = { day : { hour: number_of_tweets } }\n\n')
			daily_rhythm_txt.write(str(daily_rhytm))
			volume_creation_txt = open('volume_creation.txt','w+')
			volume_creation_txt.write('Created accounts by month\n\n')
			volume_creation_txt.write('# volume_creation = { year : { month : number_of_created_accounts } }\n\n')
			volume_creation_txt.write(str(sorted(volume_creation.items(), key=operator.itemgetter(0))))
			user_agent_txt = open('clients.txt','w+')
			user_agent_txt.write('Twitter clients\n\n')
			user_agent_txt.write('# user_agent = { client : number }\n\n')
			user_agent_txt.write(str(sorted(user_agent.items(), key=operator.itemgetter(1))[::-1]))
			retweeted_user_txt = open('retweeted_user.txt','w+')
			retweeted_user_txt.write('Retweeted users\n\n')
			retweeted_user_txt.write('# retweeted_user = { retweeted user : number }\n\n')
			retweeted_user_txt.write(str(sorted(retweeted_user.items(), key=operator.itemgetter(1))[::-1]))
			hashtag_txt = open('hashtag.txt','w+')
			hashtag_txt.write('Hashtags\n\n')
			hashtag_txt.write('# hashtag = { hashtag : number }\n\n')
			hashtag_txt.write(str(sorted(hashtag.items(), key=operator.itemgetter(1))[::-1]))
			language_tweet_txt = open('language_tweet.txt','w+')
			language_tweet_txt.write('Tweets language\n\n')
			language_tweet_txt.write('# language_tweet = { language : number_of_tweet }\n\n')
			language_tweet_txt.write(str(sorted(language_dictionary.items(), key=operator.itemgetter(1))[::-1]))
	else:
		print('\x1b[1;39;49m' + 'This language is not in the dataset' + '\x1b[0m')
	print('\x1b[1;39;49m' + 'Done!' + '\x1b[0m')
except KeyboardInterrupt:
	print('\x1b[1;39;49m' + '\n\nGoodbye\n' + '\x1b[0m')
	exit(0)
