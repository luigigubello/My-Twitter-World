# Analysis tool of Twitter dataset tweets 🦆

<a href="https://twitter.com/intent/follow?screen_name=evaristegal0is"><img src="https://img.shields.io/twitter/follow/evaristegal0is?style=social" alt="Follow @evaristegal0is"></a>

### ℹ️ About

Twitter [are continuing to release datasets](https://blog.twitter.com/en_us/topics/company/2019/info-ops-disclosure-data-september-2019.html) about disinformation campaigns on the social network. The CSV files of these datasets have always the same structure, so I have written a little script to create the graphs of tweet volume and interactions volume. The script can analyze all tweets in the dataset or tweets subsets divided by language. I have used this code [in my analysis](https://www.gubello.me/blog/about-iran-and-ira-twitter-datasets-for-fun-part-iii/) about Internet Research Agency propaganda.</br>
The script is tested on **Ubuntu 19.04** with **Python 3.7.3**.</br>

### ⚙️ How To Use

1. Install the requirements: `sudo pip3 install -r requirements.txt`
2. Launch the script: `python3 tweets_analysis.py path --lang=language`. The argument `--lang` is optional, the default value is **all**, you can change it to analyze only tweets written in a particular language.
3. Wait the output
