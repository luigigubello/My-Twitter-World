import os
from glob import glob
import time
import functools
from datetime import datetime
from ast import literal_eval
from itertools import chain

from memory_profiler import profile

import click
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import langcodes
from wordcloud import WordCloud
from PIL import Image

# suppress Pandas Warnings, sometimes they are annoying false positives. Comment this out while developing
pd.options.mode.chained_assignment = None

VERBOSE = False


def timer(func):
    # Decorator to print runtime of function

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()  # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()  # 2
        run_time = end_time - start_time
        # Convert to hours, minutes, seconds
        m, s = divmod(int(run_time), 60)
        h, m = divmod(m, 60)
        if VERBOSE:
            print(f"Finished {func.__name__!r} in {h:d} h, {m:02d} m, {s:02d} s")
        return value

    return wrapper_timer


def find_csv(path):
    if not os.path.exists(path):
        raise FileNotFoundError('The specified path does not exists. Please check your path argument')

    if os.path.isdir(path):
        # it's a directory so we read all csv files inside
        fname_list = glob(path + '/*.csv')

        if len(fname_list) == 0:
            # no csv found in the folder. Return with error
            raise FileNotFoundError("This directory does not contain any CSV file")

        return fname_list

    else:
        # it's a single file
        # simply return path enclosed in a list with one-element so it can be passed to the function "read_list_of_csv"
        return [path]


@timer
# @profile
def read_list_of_csv(fname_list, chunksize):
    df_list = []
    # to read a list of files: create a list with one DataFrame per single file, then use pd.concat on the list
    for f in fname_list:
        df_list.append(pd.read_csv(
            f,
            parse_dates=['tweet_time', 'account_creation_date'],
            usecols=['user_screen_name', 'tweetid', 'tweet_time', 'account_creation_date', 'tweet_language',
                     'account_language', 'is_retweet', 'quote_count', 'like_count', 'retweet_count', 'reply_count',
                     'tweet_client_name', 'tweet_text', 'hashtags'],
            dtype={
                'user_screen_name': 'category',
                'tweet_language': 'category',
                'account_language': 'category',
                'tweet_client_name': 'category',
                'tweet_text': str,
                'hashtags': str,
                'tweetid': np.float32,
                'quote_count': np.float32,
                'like_count': np.float32,
                'retweet_count': np.float32,
                'reply_count': np.float32
            },
            iterator=True,
            chunksize=chunksize
            # converters={'hashtags': literal_eval}  # lambda x: x.strip("[]").split(", ")}
        ))

    df_iter = chain.from_iterable(df_list)

    return df_iter


@timer
# @profile
def extract_datetime_feature(df):
    # Extract datetime informations from the "tweet_time" column

    df['hour'] = df['tweet_time'].dt.hour.astype('category')  # Extract hour of the day (i.e. 6, 23, ...)
    df['weekday'] = df['tweet_time'].dt.weekday_name.astype('category')  # Extract weekday (i.e. Monday, Friday)
    df['month'] = df['tweet_time'].dt.month_name().astype('category')  # Extract month
    df['year'] = df['tweet_time'].dt.year  # Extract year
    # Combine abbreviated month and year, i.e. Feb 2010
    df['month_year'] = (df['month'].astype(str).str[:3] + ' ' + df['year'].astype(str)).astype('category')

    return df


@timer
# @profile
def clean_hashtags(df):
    # take dataframe in input and return list of hashtags to be used in wordcloud

    # first, remove rows where hashtag column is empty
    df = df.loc[pd.notna(df['hashtags'])]

    df['hashtags_clean'] = df['hashtags'].str.lower()
    # replace punctuation with ''
    df['hashtags_clean'] = df['hashtags_clean'].str.replace(r'[^\w\s]', '')

    # now hashtags are separated by a whitespace ' '
    # ll is a list of list (because for each row of the dataset there might be multiple hashtags
    ll = [str(d).split(' ') for d in df['hashtags_clean'] if pd.notna(d)]
    # flatten list of lists
    flat_l = [htag for sublist in ll for htag in sublist]

    # this is possibly faster but to explore better
    # converters={"Col3": lambda x: x.strip("[]").split(", ")})

    return flat_l


def extend_month_year_values(df, for_chart):
    assert for_chart in ['interactions', 'volume'], "for_chart argument should be one of 'interactions' or 'volume'"

    years = df['tweet_time'].dt.year.unique()
    max_year, min_year = years.max(), years.min()
    month_year_extended = pd.date_range(datetime(min_year, 1, 1), datetime(max_year, 12, 31), freq='MS').strftime(
        '%b %Y')

    if for_chart == 'volume':
        column_to_index = ['is_retweet', 'month_year']
        first_level_index = [True, False]
    else:  # for_chart == 'interactions':
        column_to_index = ['interaction', 'month_year']
        first_level_index = ['quote_count', 'like_count', 'retweet_count', 'reply_count']

    df = df.set_index(pd.MultiIndex.from_frame(df[column_to_index], names=column_to_index), drop=True) \
        .drop(columns=column_to_index).reindex(
        pd.MultiIndex.from_product([first_level_index, month_year_extended], names=column_to_index)).reset_index()

    df = df.fillna(value={
        'n_tweets': 0,
        'value': 0
    })

    return df


def create_heatmap_df(df):
    # group by hour and weekday and count the number of tweets in each group
    heatmap_df = df.groupby(['hour', 'weekday'], observed=True).size().reset_index().rename(columns={0: 'n_tweets'})

    # transform the column "weekday" in an ordered Pandas Categorical, so y-axis on the heatmap will be ordered
    heatmap_df['weekday'] = pd.Categorical(
        heatmap_df['weekday'],
        categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        ordered=True)

    return heatmap_df


def plot_density(heatmap_df, title_prefix, fname_prefix, results_folder):
    plt.figure(figsize=(10, 5))
    sns.heatmap(heatmap_df.pivot('weekday', 'hour', 'n_tweets').fillna(0), annot=False,
                linewidths=.5)  # pivot is used to make the DF rectangular
    plt.title(f"{title_prefix} - Tweets daily rhythm", fontsize=15)
    plt.savefig(f'{results_folder}/{fname_prefix}_density.png', bbox_inches='tight', dpi=200)
    plt.close()


def create_tweet_date_list_df(df):
    # group by month_year and is_retweet column and count tweets per group
    # also take first value of tweet_time. it's a utility column that will be only used for ordering
    # in fact, ordering on month_year column does not work because it is now a string, and sorting is based on alphabet, not calendar
    tweets_per_date = df.groupby(['month_year', 'is_retweet'], observed=True).agg(
        {
            'tweet_time': 'first',
            'tweetid': 'size'
        }
    ).reset_index().rename(columns={'tweetid': 'n_tweets'})
    tweets_per_date = tweets_per_date.sort_values('tweet_time')
    tweets_per_date = extend_month_year_values(tweets_per_date, 'volume')

    return tweets_per_date


def plot_tweet_date_list(tweets_per_date, title_prefix, fname_prefix, results_folder):
    plt.figure(figsize=(10, 5))
    tweets_per_date['month_year'] = tweets_per_date['month_year'].astype(str)
    ax = sns.lineplot(data=tweets_per_date, x='month_year', y='n_tweets', hue='is_retweet', sort=False)
    ax.xaxis.set_major_locator(ticker.AutoLocator())
    plt.xticks(rotation=45, fontsize=5)
    # x_ticks = tweets_per_date['month_year'].drop_duplicates().reset_index(drop=True)
    # plt.xticks(np.arange(0, len(x_ticks), 3), x_ticks, rotation=45, fontsize=5)
    plt.title(f'{title_prefix} - Tweets volume', fontsize=10)
    plt.savefig(f'{results_folder}/{fname_prefix}_volume_tweet.png', bbox_inches='tight', dpi=250)
    plt.close()


def create_interactions_per_date(df):
    # group by month_year and sum all different interactions
    # again, take "tweet_time first" for ordering purposes
    interactions_per_date = df.groupby(['month_year']).agg(
        {
            'quote_count': 'sum',
            'like_count': 'sum',
            'retweet_count': 'sum',
            'reply_count': 'sum',
            'tweet_time': 'first'
        }
    ).reset_index().rename(columns={0: 'n_tweets'}).sort_values('tweet_time')

    # melt unpivots the dataframe in so-called "tidy" format, it is useful when working with Seaborn library
    # see https://seaborn.pydata.org/introduction.html#intro-tidy-data
    interactions_per_date = interactions_per_date.melt(id_vars=['month_year', 'tweet_time'], var_name='interaction')
    interactions_per_date = extend_month_year_values(interactions_per_date, 'interactions')
    return interactions_per_date


def plot_volume_interactions(interactions_per_date, title_prefix, fname_prefix, results_folder):
    plt.figure(figsize=(10, 5))
    ax = sns.lineplot(data=interactions_per_date, x='month_year', y='value', hue='interaction', sort=False)
    # x_ticks = interactions_per_date['month_year'].drop_duplicates().reset_index(drop=True)
    # plt.xticks(np.arange(0, len(x_ticks), 3), x_ticks, rotation=45, fontsize=5)
    ax.xaxis.set_major_locator(ticker.AutoLocator())
    plt.xticks(rotation=45, fontsize=5)
    plt.title(f'{title_prefix} - Volume per interaction', fontsize=10)
    plt.savefig(f'{results_folder}/{fname_prefix}_volume_interactions.png', bbox_inches='tight', dpi=250)
    plt.close()


def create_client_histogram(df):
    # this create the whole histogram for each client
    hist = df.groupby('tweet_client_name').size().reset_index().rename(columns={0: '# tweets'})
    return hist


def plot_clients_histogram(hist, title_prefix, fname_prefix, results_folder):

    hist = hist.sort_values('# tweets', ascending=False)
    # since the tail it's very long, cut it after 30 elements, and create one last element with "other clients"
    hist_short = hist[:30].copy()
    hist_short = hist_short.append(
        {'tweet_client_name': 'Others', '# tweets': hist[30:].sum()['# tweets']},  # last row with "Others"
        ignore_index=True)

    # plot
    plt.xticks(rotation='vertical')
    plt.bar(x=hist_short['tweet_client_name'], height=hist_short['# tweets'], color='#2196f3', edgecolor='#64b5f6',
            width=0.5)
    plt.title(f'{title_prefix} - Tweets per client', fontsize=10)
    plt.savefig(f'{results_folder}/{fname_prefix}_tweets_per_client.png', bbox_inches='tight', dpi=250)
    plt.close()


def create_lang_hist(df):
    # this create the whole histogram for each client
    hist = df.groupby('tweet_language').size().reset_index().rename(columns={0: '# tweets'})
    return hist


def plot_lang_histogram(hist, title_prefix, fname_prefix, results_folder, remove_undefined_lang=True):
    hist = hist.sort_values('# tweets', ascending=False)
    # since the tail it's very long, cut it after 30 elements, and create one last element with "other clients"
    hist_short = hist[:30].copy()
    if len(hist) > 30:
        hist_short = hist_short.append(
            {'tweet_language': 'Others', '# tweets': hist[30:].sum()['# tweets']},  # last row with "Others"
            ignore_index=True)

    hist_short['tweet_language'] = hist_short['tweet_language'].apply(
        lambda x: langcodes.Language.make(language=x).language_name())

    if remove_undefined_lang:
        hist_short = hist_short.loc[hist_short['tweet_language'] != 'Unknown language']

    # plot
    plt.xticks(rotation='vertical')
    plt.bar(x=hist_short['tweet_language'], height=hist_short['# tweets'], color='#2196f3', edgecolor='#64b5f6',
            width=0.5)
    plt.title(f'{title_prefix} - Tweets per language', fontsize=10)
    plt.savefig(f'{results_folder}/{fname_prefix}_tweets_per_lang.png', bbox_inches='tight', dpi=250)
    plt.close()


def create_accounts_created_df(df):
    # get unique users and their account_creation_date
    account_per_date = df.groupby(['account_creation_date'])['user_screen_name'].nunique().reset_index()

    account_per_date['month_year_account'] = account_per_date['account_creation_date'].dt.month_name().str[:3] + ' ' + \
                                             account_per_date['account_creation_date'].dt.year.astype(str)

    account_per_date = account_per_date.groupby('month_year_account').sum()

    years = df['account_creation_date'].dt.year.unique()
    max_year, min_year = years.max(), years.min()
    month_year_extended = pd.date_range(datetime(min_year, 1, 1), datetime(max_year, 12, 31), freq='MS').strftime(
        '%b %Y')

    account_per_date = account_per_date.reindex(month_year_extended).fillna(0)
    return account_per_date


def plot_accounts_created(accounts_per_date, title_prefix, fname_prefix, results_folder):
    fig = plt.figure(figsize=(10, 5))
    ax = fig.add_subplot()
    ax.xaxis.set_major_locator(ticker.AutoLocator())
    plt.bar(x=accounts_per_date.index, height=accounts_per_date['user_screen_name'])
    plt.xticks(rotation=45, fontsize=5)
    plt.title(f'{title_prefix} - Accounts created per month', fontsize=10)
    plt.savefig(f'{results_folder}/{fname_prefix}_accounts_created.png', bbox_inches='tight', dpi=250)
    plt.close()


def create_text_for_retweet_wordcloud(df):
    # first, only select retweets
    df = df.loc[df['is_retweet']]
    # create new column by extracting the "RT xxx:" substring with a regular expression
    df['rtw_extraction'] = df['tweet_text'].str.extract(r'(RT @[a-zA-Z-_\d]+:)')
    # create big text by concatenating all users extracted from the column "tweet_text" in a single string
    text = ' '.join([str(v)[4:-1] for v in df['rtw_extraction']])

    return text


def plot_retweet_wordcloud(text, title_prefix, fname_prefix, results_folder, colormap=matplotlib.cm.winter):
    twitter_mask = np.array(Image.open('twitter_mask.png'))

    wcloud = WordCloud(background_color="white", colormap=colormap, collocations=False, mask=twitter_mask).generate(
        text)

    # plot
    plt.figure(figsize=(12.8, 9.6), dpi=100)
    plt.imshow(wcloud, interpolation="bilinear")
    plt.axis('off')
    plt.title(f'{title_prefix}Wordcloud of retweeted users', fontsize=24)
    plt.tight_layout()
    plt.savefig(f'{results_folder}/{fname_prefix}_wordcloud_rw_users.png')
    plt.close()


def create_text_for_htag_wordcloud(df):
    hashtag_list = clean_hashtags(df)

    # create big text by concatenating all users extracted from the column "tweet_text" in a single string
    text = ' '.join(hashtag_list)

    return text


def plot_hashtag_wordcloud(text, title_prefix, fname_prefix, results_folder, colormap=matplotlib.cm.winter):
    twitter_mask = np.array(Image.open('twitter_mask.png'))
    wcloud = WordCloud(background_color="white", colormap=colormap, collocations=False, mask=twitter_mask).generate(
        text)

    # plot
    plt.figure(figsize=(12.8, 9.6), dpi=100)
    plt.imshow(wcloud, interpolation="bilinear")
    plt.axis('off')
    plt.title(f'{title_prefix}Wordcloud of hashtags', fontsize=24)
    plt.tight_layout()
    plt.savefig(f'{results_folder}/{fname_prefix}_wordcloud_hashtags.png')
    plt.close()


def filter_df_from_args(df, user, tlang, ulang):
    if user is not None:
        df = df.loc[df['user_screen_name'] == user]

    if tlang is not None:
        df = df.loc[df['tweet_language'] == tlang]

    if ulang is not None:
        df = df.loc[df['account_language'] == ulang]

    return df


@click.command()
@click.option('--path', help='Path of the Twitter Dataset. Can be a single CSV file '
                             'or a directory containing multiple CSVs', required=True)
@click.option('-w', help='Include WordCloud in the analysis.', is_flag=True)
@click.option('--user', help='Optional argument. Run the analysis only for the selected user', required=False)
@click.option('--tlang', help='Optional argument. Language of tweets to analyze', required=False)
@click.option('--ulang', help='Optional argument. Language of accounts to analyze', required=False)
@click.option('-v', help='Optional argument. Verbose mode that print more information', required=False, is_flag=True)
@click.option('--split', help='Split the analysis in chunks. For low-memory devices', required=False, is_flag=True)
@timer
def run_analysis(path, w, user, tlang, ulang, v, split):
    if v:
        global VERBOSE
        VERBOSE = True

    if split:
        chunksize = 1000000
    else:
        chunksize = None

    # first, let's read the path and find the file(s)
    csv_fnames = find_csv(path)
    print(f'Found {len(csv_fnames)} files.')
    for fn in csv_fnames:
        print(fn)
    print('Reading files...')
    tw_df = read_list_of_csv(csv_fnames, chunksize=chunksize)
    rows_analysed = 0

    heatmap_df = []
    tweets_per_date = []
    interactions_per_date = []
    client_hist = []
    lang_hist = []
    accounts_per_date = []
    retweets_wcloud_text = []
    htag_wcloud_text = []
    for df in tw_df:

        rows_analysed += len(df)

        # filter user
        df = filter_df_from_args(df, user, tlang, ulang)

        print(f'Analyzed {rows_analysed} tweets')

        # after the filters on user and language, check that the DF is not empty
        if len(df) == 0:
            continue

        df = extract_datetime_feature(df)

        heatmap_df.append(create_heatmap_df(df))
        tweets_per_date.append(create_tweet_date_list_df(df))
        interactions_per_date.append(create_interactions_per_date(df))
        client_hist.append(create_client_histogram(df))
        lang_hist.append(create_lang_hist(df))
        accounts_per_date.append(create_accounts_created_df(df))
        retweets_wcloud_text.append(create_text_for_retweet_wordcloud(df))
        htag_wcloud_text.append(create_text_for_htag_wordcloud(df))

    if user is None:
        # if user is not specified, just name it "all". it will be included in the output filenames
        user = 'all'

    if tlang is not None:
        tlang_title = langcodes.Language.make(language=tlang).language_name()
    else:
        tlang_title = 'all'

    if ulang is not None:
        ulang_title = langcodes.Language.make(language=ulang).language_name()
    else:
        ulang_title = 'all'

    title_prefix = f'User: {user} - TLang: {tlang} - ULang:{ulang}'
    fname_prefix = f'user-{user}__tlang-{tlang}__ulang-{ulang}'
    results_folder = f'results_{user}_{tlang_title}_{ulang_title}'
    os.makedirs(results_folder, exist_ok=True)

    # todo concat all dataframes merging same index together (based on type of DF)
    # for this: a different processing is needed.
    # split read between parallel and all

    # todo readd this filter, after concatenations
    # # after the filters on user and language, check that the DF is not empty
    # if len(df) == 0:
    #     raise ValueError('Combination of user and/or language is not valid. Please check user and lang arguments')

    print('Plotting charts...')
    plot_density(heatmap_df=heatmap_df, title_prefix=title_prefix,
                 fname_prefix=fname_prefix, results_folder=results_folder)
    plot_tweet_date_list(tweets_per_date=tweets_per_date, title_prefix=title_prefix,
                         fname_prefix=fname_prefix, results_folder=results_folder)
    plot_volume_interactions(interactions_per_date=interactions_per_date, title_prefix=title_prefix,
                             fname_prefix=fname_prefix, results_folder=results_folder)
    plot_clients_histogram(hist=client_hist, title_prefix=title_prefix, fname_prefix=fname_prefix,
                           results_folder=results_folder)

    plot_lang_histogram(hist=lang_hist, title_prefix=title_prefix, fname_prefix=fname_prefix, results_folder=results_folder)
    plot_accounts_created(accounts_per_date=accounts_per_date, title_prefix=title_prefix, fname_prefix=fname_prefix, results_folder=results_folder)

    if w:
        print('Plotting wordclouds...')
        plot_retweet_wordcloud(text=retweets_wcloud_text, title_prefix=title_prefix, fname_prefix=fname_prefix,
                               results_folder=results_folder)
        plot_hashtag_wordcloud(text=htag_wcloud_text, title_prefix=title_prefix, fname_prefix=fname_prefix,
                               results_folder=results_folder)


if __name__ == '__main__':
    print(
        "\x1b[1;34;49m" + "\n\n                 ./oss+:    -\n /d:           .hMMMMMMMNydm/`\n hMMd+`       `NMMMMMMMMMMNdy-\n /MMMMMds/-`  /MMMMMMMMMMMN-         \n .+mMMMMMMMMNmmMMMMMMMMMMMm\n sMNMMMMMMMMMMMMMMMMMMMMMMs\n  sMMMMMMMMMMMMMMMMMMMMMMN.\n   -smMMMMMMMMMMMMMMMMMMM/\n   .dMMMMMMMMMMMMMMMMMMN:\n     :ydNMMMMMMMMMMMMMh.\n     `:omMMMMMMMMMMMy-\n./ymNMMMMMMMMMMMmy/`\n   `-/+ssssso/-`\n" + "\x1b[0m")
    print(
        "\x1b[1;39;49m" + "  Made with" + "\x1b[0m" + "\x1b[1;31;49m" + " ❤" + "\x1b[0m" + "\x1b[1;39;49m" + " - https://www.github.com/luigigubello (and https://www.github.com/naikio)" + "\x1b[0m\n\n")
    print('\x1b[1;39;49m' + 'Wait...' + '\x1b[0m')
    run_analysis()
