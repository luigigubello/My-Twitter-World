# Twitter Search 🦆

<a href="https://twitter.com/intent/follow?screen_name=evaristegal0is"><img src="https://img.shields.io/twitter/follow/evaristegal0is?style=social" alt="Follow @evaristegal0is"></a>

### ℹ️ About

**`ŧwitter_search.py`** is a little Python script to collect Twitter data into a CSV file. The script finds the tweets or retweets with particular hashtags or keyworlds and collect the data via Twitter API, until 7000 tweets/hour circa. So you have to have your own Twitter API keys (tokens) to use it.
The script is tested on **Ubuntu 18.04** with **Python 3.6.8**.

### ⚙️ How To Use

1. Go to [Twitter Developer page](https://developer.twitter.com/en/docs/basics/developer-portal/overview)  and [follow these steps](https://developer.twitter.com/en/docs/basics/authentication/guides/access-tokens.html) to obtain the access tokens
2. Install the module [TwitterAPI](https://github.com/geduldig/TwitterAPI): `sudo pip3 install TwitterAPI`
3. Edit `twitter_search.py` at the lines 13-16 and paste your Twitter API keys
4. Launch the script: `python3 twitter_search.py`
5. Type the hashtag or the keywords you want to search and press `Enter`
