import csv
import sys
import os
import time
import re

from datetime import datetime, timedelta
from TwitterAPI import TwitterAPI, TwitterError


# Token per le API Twitter
api = TwitterAPI( \
        consumer_key='#### CHIAVE QUI ####', \
        consumer_secret='#### CHIAVE QUI ####', \
        access_token_key='#### CHIAVE QUI ####', \
        access_token_secret='#### CHIAVE QUI ####' \
        )

def hashtag_analisys(api, directory, input_id):

	day_story = datetime.today().strftime('%Y-%m-%d') # Oggi

	fullpathname = os.path.abspath(os.path.dirname(sys.argv[0]))
	fullpathname = fullpathname + '/' + directory

	# Seleziona i 100 tweets più recenti e salva info su CSV
	if not os.path.exists(fullpathname + '/' + search_word + '_' + day_story + '.csv'):
		last_id = 0
	else:
		with open(os.path.join(fullpathname, search_word + '_' + day_story + '.csv'), 'r') as csvfile:
			reader = csv.reader(csvfile)
			row_count = len(list(reader))

			if row_count != 1:
				with open(os.path.join(fullpathname, search_word + '_' + day_story + '.csv'), 'r') as csvfile:
					reader = csv.reader(csvfile)
					reader = list(reader)
					last_id = reader[row_count-1][1]

			else:
				last_id = 1

	if not os.path.exists(fullpathname + '/' + search_word + '_' + day_story + '.csv'):
		with open(os.path.join(fullpathname, search_word + '_' + day_story + '.csv'), 'w') as csvfile:
			filewriter = csv.writer(csvfile, sys.stdout, lineterminator='\n', delimiter=',',quotechar='"', quoting=csv.QUOTE_ALL)
			filewriter.writerow(['tweet_date', 'tweetid', 'tweet_text', 'retweet_count', 'favorite_count', 'truncated', 'tweet_client_name', 'user_country_code', 'userid', 'user_screen_name', 'user_display_name', 'user_profile_description', 'follower_count', 'following_count', 'account_creation_date', 'statues_count', 'profile_image_url', 'default_profile_image'])
				
	# Lista di features estratte da ogni tweets
	if last_id == 0:
		search = api.request('search/tweets', {'q': search_word, 'count':'100', 'result_type':'recent'})
		# '-filter:retweets' esclude i retweets
		#search = api.request('search/tweets', {'q': search_word + ' -filter:retweets', 'count':'100', 'result_type':'recent'})
	elif last_id == 1:
		print('\x1b[1;39;49m' + 'Tweets not found' + '\x1b[0m')
		exit(0)
	else: 

		if input_id[1] != 0:
			max_id = int(last_id)-1
			input_id[0] = max_id
		else:
			max_id = input_id[0] - 100 #puoi cambiare questo numero, default = 100
			input_id[0] = max_id
		search = api.request('search/tweets', {'q': search_word, 'count':'100', 'result_type':'recent', 'max_id':max_id})
		# '-filter:retweets' esclude i retweets
		#search = api.request('search/tweets', {'q': search_word + ' -filter:retweets', 'count':'100', 'result_type':'recent', 'max_id':max_id})

	t_tweet_date = (list(post['created_at'] for post in search))
	t_tweet_id = (list(post['id'] for post in search))
	print('\x1b[1;39;49m' + 'Tweet IDs: '+ '\x1b[0m' + '{}'.format(t_tweet_id))
	input_id[1] = len(t_tweet_id)
	t_tweet_truncated = (list(post['truncated'] for post in search))
	t_tweet_text = (list(post['text'] for post in search))
	t_tweet_retweet = (list(post['retweet_count'] for post in search))
	t_tweet_favorite = (list(post['favorite_count'] for post in search))
	t_tweet_regex = []
	for tweext in t_tweet_text:
		tweext = re.sub('"', '\\"', tweext)
		tweext = '"' + tweext + '"'
		t_tweet_regex.append(tweext)
	t_tweet_source = (list(post['source'] for post in search))
	t_tweet_ua = []
	for source in t_tweet_source:
		source = re.sub('<[^>]+>', '', str(source))
		t_tweet_ua.append(source)
	t_tweet_place = (list(post['place'] for post in search))
	t_tweet_country = []
	for place in t_tweet_place:
		try:
			text = str(place['country_code'])
		except TypeError:
			text = 'NULL'
		t_tweet_country.append(text)		
	t_user_id = (list(post['user']['id'] for post in search))		
	t_screen_name = (list(post['user']['screen_name'] for post in search))
	t_name = (list(post['user']['name'] for post in search))
	t_description = (list(post['user']['description'] for post in search))
	t_follower_count = (list(post['user']['followers_count'] for post in search))
	t_following_count = (list(post['user']['friends_count'] for post in search))
	t_created_at = (list(post['user']['created_at'] for post in search))
	t_statuses_count = (list(post['user']['statuses_count'] for post in search))
	t_profile_image_url = (list(post['user']['profile_image_url_https'] for post in search))
	t_default_image = (list(post['user']['default_profile_image'] for post in search))
	
	i = 0
	while i < len(t_screen_name):

		with open(os.path.join(fullpathname, search_word + '_' + day_story + '.csv'), 'a') as csvfile:
			filewriter = csv.writer(csvfile, sys.stdout, lineterminator='\n', delimiter=',',quotechar='"', quoting=csv.QUOTE_ALL)
			filewriter.writerow([t_tweet_date[i], t_tweet_id[i], t_tweet_text[i], t_tweet_retweet[i], t_tweet_favorite[i], t_tweet_truncated[i], t_tweet_ua[i], t_tweet_country[i], t_user_id[i], t_screen_name[i], t_name[i], t_description[i], t_follower_count[i], t_following_count[i], t_created_at[i], t_statuses_count[i], t_profile_image_url[i], t_default_image[i]])		
		i += 1

	return(input_id)


# Ripete hashtag_analisys ogni 5 secondi
try:
	print("\x1b[1;34;49m" + "\n\n                 ./oss+:    -\n /d:           .hMMMMMMMNydm/`\n hMMd+`       `NMMMMMMMMMMNdy-\n /MMMMMds/-`  /MMMMMMMMMMMN-         \n .+mMMMMMMMMNmmMMMMMMMMMMMm\n sMNMMMMMMMMMMMMMMMMMMMMMMs\n  sMMMMMMMMMMMMMMMMMMMMMMN.\n   -smMMMMMMMMMMMMMMMMMMM/\n   .dMMMMMMMMMMMMMMMMMMN:\n     :ydNMMMMMMMMMMMMMh.\n     `:omMMMMMMMMMMMy-\n./ymNMMMMMMMMMMMmy/`\n   `-/+ssssso/-`\n" + "\x1b[0m")
	print("\x1b[1;39;49m" + "  Made with" + "\x1b[0m" + "\x1b[1;31;49m" + " ❤" + "\x1b[0m" + "\x1b[1;39;49m" + " - https://www.github.com/luigigubello" + "\x1b[0m\n\n")

	search_word = input('\x1b[1;39;49m' + 'Write an hashtag, a word or a sentence to search: ' + '\x1b[0m')
	fullpathname = os.path.abspath(os.path.dirname(sys.argv[0]))
	dir_time = search_word + '_' + datetime.now().strftime('%d-%m-%Y')
	if not os.path.exists(fullpathname + '/' + dir_time):
		os.makedirs(fullpathname + '/' + dir_time)
	if not os.path.exists(fullpathname + '/' + dir_time + '/log_' + search_word + '.txt'):
		log_txt = open(fullpathname + '/' + dir_time + '/log_' + search_word + '.txt','w+')
		log_txt.write('[[' + datetime.now().strftime('%d-%m-%Y %H:%M:%S') + ']]  |  Start log\n')
	else:
		log_txt = open(fullpathname + '/' + dir_time + '/log_' + search_word + '.txt','a+')
		log_txt.write('[[' + datetime.now().strftime('%d-%m-%Y %H:%M:%S') + ']]  |  Start log\n')
	log_txt.close()
	input_id = [0, 200]
	while True:
		start_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
		log_txt = open(fullpathname + '/' + dir_time + '/log_' + search_word + '.txt','a+')
		log_txt.write('[[' + start_time + ']]  |  CSV Updated\n')
		log_txt.close()
		print('\x1b[1;39;49m' + '\nTime: {}'.format(start_time) + '\n' + '\x1b[0m')
		hashtag_pre = hashtag_analisys(api, dir_time, input_id)
		input_id = hashtag_pre
		print('\x1b[1;39;49m' + '\nPause\n...\nWait...\n' + '\x1b[0m')
		time.sleep(5)

except KeyboardInterrupt:
	log_txt = open(fullpathname + '/' + dir_time + '/log_' + search_word + '.txt','a+')
	log_txt.write('[[' + datetime.now().strftime('%d-%m-%Y %H:%M:%S') + ']]  |  Stop log\n')
	log_txt.close()
	print('\x1b[1;39;49m' + '\n\nGoodbye\n' + '\x1b[0m')
	exit(0)
