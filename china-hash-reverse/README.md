# How to find the User ID of some hashed accounts in the Chinese Twitter dataset 🦆

<a href="https://twitter.com/intent/follow?screen_name=evaristegal0is"><img src="https://img.shields.io/twitter/follow/evaristegal0is?style=social" alt="Follow @evaristegal0is"></a>


### ℹ️ About

In August, 2019, Twitter have published a large dataset - splitted in two CSV files - about a [_state-backed information operation focused on the situation in Hong Kong_](https://blog.twitter.com/en_us/topics/company/2019/information_operations_directed_at_Hong_Kong.html). This is a important data collection about a new state: China. The first analysis shows many differences between this dataset and the Internet Research Agency one, but there is a particular difference between these two datasets: how Twitter have built them.

In the Internet Research Agency dataset there are all the accounts of the Russian network, and the privacy of each account with less than 5000 followers is protected by an hash. Moreover Twitter have published an archive of all multimedia files shared by Internet Research Agency accounts. _The dataset about Hong Kong disinformation seems to have been built faster_, there are 936 accounts but Twitter have suspended 200.000 accounts circa, so many quoted accounts in the dataset's tweets are suspended but we have no information about them. Also we haven no information about the multimedia files shared by these accounts. Another difference is the column **user_mentions** where no user ID is hashed, so it is possible to associate some hashes with some user IDs.</br>

If you want to support me you can offer me a coffee ☕</br></br>
<a href="https://www.buymeacoffee.com/gubello" target="_blank"><img src="https://bmc-cdn.nyc3.digitaloceanspaces.com/BMC-button-images/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: auto !important;width: auto !important;" ></a>


### ⚙️ How To Use

1. Install the module **pandas**: `sudo pip3 install pandas`
2. Edit the path of the file `china_082019_[x]_tweets_csv_hashed.csv` at line 6
3. Launch the script: `python3 china_hash_reverse.py`
4. Wait the output

### Reversed hashes

#### china_082019_1_tweets_csv_hashed.csv

| **Hash**  | **User ID**  |
|---|---|
| 2l1eDka0eiClBUYoDXlwYaKcUaeelnz44aDM9OJRM= | 916297908357554178 |
| 7lx09UkfLQ9VhHAb5KHsSg1tZ4lif1UaEtW5f2OZkU= | 33123699 |
| XzJ77H5S5n8swKL1MkirmKrsIWzbthBk0tOWMjBP0= | 888030317117751296 |
| QVr+qYj7OTUbWgxNe8gbFgqkfnPKR6KZQFkt3pOmA= | 2381868864 |
| iImZZDnNc6o6KVy8Ps9iPdVHvQMfDSbN0eNagUcXG0= | 788333692682895360 |
| PgyTbaP5VxfSvhFfuUZbxtfNs06PFBGfJu18zPZp28= | 870957478489534464 |
| LQV+YJdIxi7pAp7BI7eISH4TYv5hv0d8U5k4DwD0wLs= | 902780657616773120 |
| OGJHxWo1EkGP0YHTT+Rcjp9sDiut92h2hbPXZJ8RYWU= | 1005232100 |
| srYbMEaGLGlpw0K8OumGM4zoURjHaR9+gxs6xxsX14= | 918004408989782016 |
| bQORtjPyE2vvAP3vJ5UgrH9q+rx1qFJgpgVyZ98nUY= | 944917444958793728 |
| nXJwGmcG71Ho3srqnXTSnyEokZXke8tkdISrrycI= | 1011660564 |
| gUmfLNlOJlPQoL0dE6kRoCQQ9ZS+wodMV7J2YY67zA= | 979186863964610561 |
| e7NU0+z7PopcH79Yg++htske2Ke5RBcNSLfDkyhhFVw= | 1010738701 |
| bF6Az7sj3D1jYDAYT8IqkBBeRtuTbUsIvjJVpXZ8hA= | 910185551948476416 |
| uSeViCRXvlKQSSTLmiXtHlH9jQbLI+diQQ6vZeoylk= | 920541688551981056 |
| OrIp16w11sCkQPw0hO4jhfjIQ+SqteLTl0hyi9tYJGI= | 924426505832185856 |
| yBASA80W0uLbb5O8p87m6sK+HauWaEO5DDHiSNWpM= | 898929850047660032 |
| T4iBtjiHQDoj7f6cdYiVsUawuaMqEV2GsqttlBaCkI= | 979184325236109314 |
| ueV2dN3HOL24gOeDeNDZzDn0LU+68V9kby+jDR2pm4= | 923384722020900864 |
| 9BjRs2fwA0ZI7+XDZ7am8ybzCzZPXifEIWzv1K4kLY= | 898929649987854336 |
| 4pfgkNwEiZfzJpXxGtiKeGdMzBoUnttFPzEb2SPN6wI= | 902779689026162688 |

#### china_082019_2_tweets_csv_hashed.csv

| **Hash**  | **User ID**  |
|---|---|
| ZTUhI030WiV97FLuXgAU427wsJ1TtqtTBMXjKgShnU= | 1109204197 |
| uLSmkkw6KZIAxPjvCOUOlquZLetiOxTnHOc7JkAkgsM= | 87521624 |
| Y5fylbnjj18F8K62fmujEA3JAVSTxxtKYQW2kY6CoJg= | 1311202902 |
| 3n0xdqzYtFlDcc3AfvuOPP2jSfmlhy7ASmQaywDOI= | 2989619897 |
| F3uvEL4yBGKljlONEbUqJ8jOLfwMtIbebQZ8+3lhM0M= | 4566153013 |
| 4FPZlgWoWQ5TbJrTKbemUkVCWjyOj1cRuI0syvxUNtI= | 39066713 |
| ydaRmRIG6EQ+ksNz+n+K+1mwjePEuMuWSgZP1RQPjeo= | 422403967 |
| QRcBY8D5EinWF+pp4Qx1UoK9Sqfs1qm0ZaFjrOiEwd0= | 3357417580 |
| ULFpHNFQoxV0dhQqlzSbKCos+Yq8Ac3sekpiNz9mbkI= | 19639625 |
| UBahKf20Yori5eaWPg+MrcxaSZV5Q8AcbzpbF3Q4o4= | 1247225640 |
