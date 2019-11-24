# Analysis tool of Twitter dataset tweets 🦆

<a href="https://twitter.com/intent/follow?screen_name=evaristegal0is"><img src="https://img.shields.io/twitter/follow/evaristegal0is?style=social" alt="Follow @evaristegal0is"></a>

### ℹ️ About

Twitter [are continuing to release datasets](https://blog.twitter.com/en_us/topics/company/2019/info-ops-disclosure-data-september-2019.html) about disinformation campaigns on the social network. The CSV files of these datasets have always the same structure, so I have written a little script to create some graphs to better understand the data. I have used this code [in my analysis](https://www.gubello.me/blog/about-iran-and-ira-twitter-datasets-for-fun-part-iii/) about Internet Research Agency propaganda.</br>
The script is tested on **Ubuntu 19.04** with **Python 3.7.3**.</br>
⚠️ **Important:** there is a [bug](https://stackoverflow.com/a/58165593) in Matplotlib 3.1.1, so you have to use Matplotlib < 3.1.1.</br>

If you want to support me you can offer me a coffee ☕</br></br>
<a href="https://www.buymeacoffee.com/gubello" target="_blank"><img src="https://bmc-cdn.nyc3.digitaloceanspaces.com/BMC-button-images/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>

### ⚙️ How To Use

```
Usage: tweet-analysis.py [OPTIONS]

Options:
  --path TEXT     Path of the Twitter Dataset. Can be a single CSV file or a
                  directory containing multiple CSVs  [required]
  -w              Include WordCloud in the analysis.
  --user TEXT     Optional argument. Run the analysis only for the selected user
  --tlang TEXT    Optional argument. Language of tweets to analyze
  --ulang TEXT    Optional argument. Language of accounts to analyze
  --chunksize INT Optional argument. Default is 1000000. Decrease if you run into memory issues
  -v              Optional argument. Verbose mode that print more information
  --help          Show this message and exit.

  ```

### 📝 Examples

The script requires only the `--path` argument. You can pass either a single CSV file, or a folder (in which case, all the CSV inside will be read and concatenated for the analysis)

##### Example

Analysing the dataset *china_082019_1_tweets_csv_hashed.csv*

`$ python3 tweets_analysis.py --path china_082019_1_tweets_csv_hashed.csv`

Mergering and analysing the datasets *china_082019_1_tweets_csv_hashed.csv* and *china_082019_1_tweets_csv_hashed.csv*:
Assuming these files are in a folder called "china_dataset":

`python3 tweets_analysis.py --path china_dataset`

The data is read in chunks thanks to pandas's read_csv functionalities. Memory should not be a problem, but if you run into memory issues, please try to decrease the default chunksize (defauls is 1000000, something below 500000 should run on pretty much any hardware)
`python3 tweets_analysis.py --path china_082019_1_tweets_csv_hashed --chunksize 250000`

You can analyse data subsets by dividing them by language. Setting the parameter `--tlang LANG` the script analyses only tweets that have the value `LANG` in the column `tweet_language`, setting the parameter `--ulang LANG` the script analyses all the tweets published by the accounts that have the value `LANG` in the column `account_language`. In the columns `tweet_language` and `account_language` Twitter have formated the values as *ISO 639-1 alpha-2*, *ISO 639-3 alpha-3* or *ISO 639-1 alpha-2* combined with an *ISO 3166-1 alpha-2* localization, so you have to use these formats to set the arguments.

If `ulang`, `tlang`, or `user` are not specified, no filtering is performed.

##### Example

Analysing all the English tweets (`en`) in the dataset *china_082019_1_tweets_csv_hashed.csv*

`$ python3 tweets_analysis.py --path china_082019_1_tweets_csv_hashed.csv --tlang en`

Analysing all the tweets in the dataset *china_082019_1_tweets_csv_hashed.csv* written by English accounts

`$ python3 tweets_analysis.py --path china_082019_1_tweets_csv_hashed.csv --ulang en`

### 📊 How to read the graphs

It is important to understand the graphs to read the data right. So I try to explain how to do by using the [Spanish dataset linked to Partido Popular](https://blog.twitter.com/en_us/topics/company/2019/info-ops-disclosure-data-september-2019.html) as case study.

#### Case study: Spain 🇪🇸

`$ python3 tweets_analysis.py --path spain_082019_tweets_csv_hashed.csv -w`

##### Interactive example
You can see an interactive example in this [jupyter notebook](./Tweets analysis - interactive.ipynb)

###### Generated graphs

<img src="https://www.gubello.me/blog/wp-content/uploads/2019/10/tutorial_all_volume_tweet.png" width="600">

**Tweets volume:** we can see that tweets and retweets started in February, 2019, and finished in April, 2019. So there are only three months of activities: Febraury, March and April. March is the month with the higgest number of tweets and retweets (16.000 tweets and 18.500 retweets circa, but you can read the correct data in the text file generated by tweets_analysis.py). From May, 2019, there are no tweets because Twitter suspended this network.</br></br>

<img src="https://www.gubello.me/blog/wp-content/uploads/2019/10/tutorial_all_volume_interactions.png" width="600">

**Interactions volume by month:** this graph shows the volume of interactions generated by all tweets - *both tweets and retweets* - in the dataset. The first interactions started in February, 2019, and they finished in April, 2019, like the previous graph. There is a spike of all interactions in March.</br></br>

<img src="https://www.gubello.me/blog/wp-content/uploads/2019/10/tutorial_all_density.png" width="600">

**Tweets daily rhythm:** this graph shows the daily rhythm of all accounts. It is useful to understand when the network was more active. If a network has many accounts can be useful divided the accounts by language and check this graph for each group to see if there are different patterns (e.g. the accounts with the value `it` in the column `account_language` maybe are more active during the Italian time zone). The Spanish accounts were more active between 11 am and 01 pm (🇪🇸 TZ), especially on Wednesdays, Thursdays and Fridays. During the weekend the accounts were inactive except for the night.</br></br>

<img src="https://www.gubello.me/blog/wp-content/uploads/2019/10/tutorial_all_creation_date.png" width="600">

**Number of created accounts by month:** the barplot shows the number of created **accounts\*** by month. The first accounts were created in February, 2019, the last ones in April.</br>

**\***: this graph shows the creation dates of active accounts (i.e. they published at least one tweet or retweet) and they are all the accounts contained the dataset *NAME_DATASET_tweets_csv_hashed.csv*. These accounts can be less than the accounts contained in the dataset *NAME_DATASET_users_csv_hashed.csv* because it is possible that some accounts have no written any tweets or retweets.</br></br>

<img src="https://www.gubello.me/blog/wp-content/uploads/2019/10/tutorial_all_user_agent.png" width="600">

**Twitter clients:** this barplot shows the most used Twitter clients to create tweets and retweets. We can see that TweetDeck and Twitter Web Client are used to publish many tweets, probabily because it is easy to schedule contents with these two clients, but there are also some tweets posted via Android and iPhone. *The barplot shows at most the thirty most frequent clients*.</br></br>

<img src="https://www.gubello.me/blog/wp-content/uploads/2019/10/tutorial_all_tweets_language.png" width="600">

**Languages of tweets:** this graph shows how many tweets are written in a particular language. It can give many information about the network's targets. In the Spanish case almost all tweets are classified by Twitter as *Spanish*, so the target of the campaign are Spanish people living in Spain. *The barplot shows at most the thirty most used languages*.</br></br>

<img src="https://www.gubello.me/blog/wp-content/uploads/2019/10/tutorial_all_retweeted_user.png" width="600">

**Retweeted users:** this is the wordcloud of the most retweeted users. There are at most the top 100 retweeted users, because in the command line I have choosen the arguments `-w -top`. In this case it is easy to see many accounts linked to Partido Populares like @populares, @pablocasado_, @PPopular and many others, so - maybe - this network supported Pardido Populares as Twitter say.

<img src="https://www.gubello.me/blog/wp-content/uploads/2019/10/tutorial_all_hashtag.png" width="600">

**Hashtags:** this is the wordcloud of the most frequent hashtags. There are at most 100 most frequent hashtags. The Spanish hashtags concerned the Spanish political situation and many were used by Partido Popular.
