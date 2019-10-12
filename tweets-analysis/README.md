# Analysis tool of Twitter dataset tweets 🦆

<a href="https://twitter.com/intent/follow?screen_name=evaristegal0is"><img src="https://img.shields.io/twitter/follow/evaristegal0is?style=social" alt="Follow @evaristegal0is"></a>

### ℹ️ About

Twitter [are continuing to release datasets](https://blog.twitter.com/en_us/topics/company/2019/info-ops-disclosure-data-september-2019.html) about disinformation campaigns on the social network. The CSV files of these datasets have always the same structure, so I have written a little script to create some graphs to better understand the data. I have used this code [in my analysis](https://www.gubello.me/blog/about-iran-and-ira-twitter-datasets-for-fun-part-iii/) about Internet Research Agency propaganda.</br>
The script is tested on **Ubuntu 19.04** with **Python 3.7.3**.</br>

### ⚙️ How To Use

```
usage: tweets_analysis.py [-h]
                           (--path [PATH [PATH ...]] | --dirpath DIRPATH | --split [SPLIT [SPLIT ...]])
                           [--index INDEX] [--tlang TLANG | --ulang ULANG]
                           [-w] [-top] [-csv] [-txt] [-v]

Twitter disinformation datasets' analysis

optional arguments:
  -h, --help            show this help message and exit
  --path [PATH [PATH ...]]
                        path of Twitter dataset
  --dirpath DIRPATH     path of the directory containing Twitter dataset(s)
  --split [SPLIT [SPLIT ...]]
                        split a CSV file in smaller CSV files, it can be slow
  --index INDEX         number of rows of each splitted CSV files [default:
                        --index=1000000]
  --tlang TLANG         language of tweets to analyse [default: --tlang=all]
  --ulang ULANG         language of accounts to analyse [default: --ulang=all]
  -w                    large wordclouds are slow to build, so active this
                        parameter only if you are patient
  -top                  generate wordclouds with at most the 100 most frequent
                        words, saving your time
  -csv                  save info into csv files
  -txt                  save all details into txt files
  -v                    verbose mode
