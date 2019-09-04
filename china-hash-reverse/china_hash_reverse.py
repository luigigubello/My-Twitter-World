import pandas as pd
import os
import csv

# Tweets CSV
path_csv = 'YOUR/PATH/HERE/china_082019_2_tweets_csv_hashed.csv' # edit this with your path

try:
	print("\x1b[1;34;49m" + "\n\n                 ./oss+:    -\n /d:           .hMMMMMMMNydm/`\n hMMd+`       `NMMMMMMMMMMNdy-\n /MMMMMds/-`  /MMMMMMMMMMMN-         \n .+mMMMMMMMMNmmMMMMMMMMMMMm\n sMNMMMMMMMMMMMMMMMMMMMMMMs\n  sMMMMMMMMMMMMMMMMMMMMMMN.\n   -smMMMMMMMMMMMMMMMMMMM/\n   .dMMMMMMMMMMMMMMMMMMN:\n     :ydNMMMMMMMMMMMMMh.\n     `:omMMMMMMMMMMMy-\n./ymNMMMMMMMMMMMmy/`\n   `-/+ssssso/-`\n" + "\x1b[0m")
	print("\x1b[1;39;49m" + "  Made with" + "\x1b[0m" + "\x1b[1;31;49m" + " ❤" + "\x1b[0m" + "\x1b[1;39;49m" + " - https://www.github.com/luigigubello" + "\x1b[0m\n\n")

	print('\x1b[1;39;49m' + 'Wait...\n' + '\x1b[0m')
	count = []
	count2 = []
	user_h = []

	data = pd.read_csv(path_csv, header=0)
	user_screen_name = list(data.user_screen_name)
	userid = list(data.userid)
	follower = list(data.follower_count)
	tweet_text = list(data.tweet_text)
	user_mentions = list(data.user_mentions)

	i = 0
	while i < len(user_screen_name):
		if int(follower[i]) < 5000 and str(user_screen_name[i]) not in count:
			if '@'+str(user_screen_name[i]) in str(tweet_text[i]):
				if str(user_screen_name[i]) in count2:
					for item in user_h:
						if item[0] == str(user_screen_name[i]):
							if isinstance(user_mentions[i], str):
								user_mentions[i] = user_mentions[i][1:-1]
								array = user_mentions[i].split(', ')
								k = 1
								for element in array:
									if str(element) == 'nan' or str(element) == 'NaN' or str(element) == '0' or str(element) == '':
										k = 0
								if k == 1:
									item.append(array)
									count.append(str(user_screen_name[i]))
									break
				else:
					if isinstance(user_mentions[i], str):
						user_mentions[i] = user_mentions[i][1:-1]
						array = user_mentions[i].split(', ')
						k = 1
						for element in array:
							if str(element) == 'nan' or str(element) == 'NaN' or str(element) == '0' or str(element) == '':
								k = 0
							if k != 0 and len(array) == 1:
								k = 2
						if k == 1:
							user_h.append([str(user_screen_name[i]), array])
							count2.append(str(user_screen_name[i]))
						if k == 2:
							user_h.append([str(user_screen_name[i]), array])
							count2.append(str(user_screen_name[i]))
							count.append(str(user_screen_name[i]))	
		i += 1
		#print(i)
	final = []
	for item in user_h:
		if len(item) == 3:
			idu = []
			for element in item[1]:
				i = 0
				while i < len(item[2]):
					if element == item[2][i]:
						idu.append(element)
						break
					i += 1
			if idu != []:
				final.append([item[0], idu])
		else:
			if len(item) == 2 and len(item[1]) == 1:
				final.append([item[0], item[1]])
	for element in final:
		if len(element[1]) == 1:
			print('\x1b[1;39;49m' + 'User hash: '  + '\x1b[0m' + '{}'.format(element[0]))
			print('\x1b[1;39;49m' + 'User ID: ' + '\x1b[0m' + '{}'.format(element[1][0]))
except KeyboardInterrupt:
	print('\x1b[1;39;49m' + '\n\nGoodbye\n' + '\x1b[0m')
	exit(0)
