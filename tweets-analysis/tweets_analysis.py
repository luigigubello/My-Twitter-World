import os
from pathlib import Path
from glob import glob
import time
import sys
import functools
from datetime import datetime
from itertools import chain
import csv

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
from tqdm import tqdm

# Matplotlib general settings
plt.rcParams['figure.figsize'] = (21, 9)

# suppress Pandas Warnings, sometimes they are annoying false positives. Comment this out while developing
pd.options.mode.chained_assignment = None

VERBOSE = False
CHUNKSIZE = 1000000


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

        print(f'Found {len(fname_list)} files:')
        print('\n'.join([Path(f).resolve().name for f in fname_list]))
        return fname_list

    else:
        # it's a single file
        # simply return path enclosed in a list with one-element so it can be passed to the function "read_list_of_csv"
        print(f"Found file: {Path(path).resolve().name}")
        return [path]


def row_count(file):
    with open(file, encoding='utf-8') as csv_file:
        file_obj = csv.reader((l.replace('\0', '') for l in csv_file))
        n_rows = sum(1 for line in file_obj) - 1  # discard header as we are usually dealing with CSVs here
    return n_rows


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


def extract_datetime_feature(df):
    # Extract datetime informations from the "tweet_time" column

    df['hour'] = df['tweet_time'].dt.hour.astype('category')  # Extract hour of the day (i.e. 6, 23, ...)
    df['weekday'] = df['tweet_time'].dt.weekday_name.astype('category')  # Extract weekday (i.e. Monday, Friday)
    df['month'] = df['tweet_time'].dt.month_name().astype('category')  # Extract month
    df['year'] = df['tweet_time'].dt.year  # Extract year
    # Combine abbreviated month and year, i.e. Feb 2010
    df['month_year'] = (df['month'].astype(str).str[:3] + ' ' + df['year'].astype(str)).astype('category')

    return df


def filter_user_and_langs(df, user, tlang, ulang):
    if user is not None:
        df = df.loc[df['user_screen_name'] == user]

    if tlang is not None:
        df = df.loc[df['tweet_language'] == tlang]

    if ulang is not None:
        df = df.loc[df['account_language'] == ulang]

    return df


# @timer
def process_one_chunk(df, user, tlang, ulang):
    """ Process a single DataFrame (subset of the entire one of size=CHUNKSIZE"""

    # first filter by user of lang, if specified
    ##############################################
    df = filter_user_and_langs(df, user=user, tlang=tlang, ulang=ulang)

    # add additional columns enriching date information
    ##################
    df = extract_datetime_feature(df)

    # groupby month-year and retweet, and sum all the statistics about interactions and number of tweets
    ##################
    tweets_stats = df.groupby(['month_year', 'is_retweet']).agg({
        'tweetid': 'size',
        'quote_count': 'sum',
        'like_count': 'sum',
        'retweet_count': 'sum',
        'reply_count': 'sum',
        'tweet_time': 'first'
    }).rename(columns={'tweetid': 'n_tweets'}).reset_index().sort_values('tweet_time')

    # create part of heatmap
    ##################
    heatmap_df = df.groupby(['hour', 'weekday'], observed=True).size().reset_index().rename(columns={0: 'n_tweets'})

    # histogram of client names
    ##################
    client_hist = df.groupby('tweet_client_name').size().reset_index().rename(columns={0: '# tweets'})

    # histogram of tweet languages
    ##################
    lang_hist = df.groupby('tweet_language').size().reset_index().rename(columns={0: '# tweets'})

    # account created per date (just saving list of unique users here, will process later in another function)
    ##################
    users_creation_dates = df.groupby('user_screen_name')['account_creation_date'].first().reset_index()

    # extract username of retweeted users
    ##################
    df['rtw_extraction'] = df['tweet_text'].str.extract(r'(RT @[a-zA-Z-_\d]+:)')
    rtw_usernames = [str(v)[4:-1] for v in df['rtw_extraction'] if str(v)[4:-1] != '']

    # extract all hashtags
    ##################
    df_ht = df.loc[pd.notna(df['hashtags'])]

    df_ht['hashtags_clean'] = df_ht['hashtags'].str.lower()
    # replace punctuation with ''
    df_ht['hashtags_clean'] = df_ht['hashtags_clean'].str.replace(r'[^\w\s]', '')

    # now hashtags are separated by a whitespace ' '
    # ll is a list of list (because for each row of the dataset there might be multiple hashtags
    ll = [str(d).split(' ') for d in df_ht['hashtags_clean'] if pd.notna(d)]
    # flatten list of lists
    hashtags = [htag for sublist in ll for htag in sublist if htag != '']

    return tweets_stats, heatmap_df, client_hist, lang_hist, users_creation_dates, rtw_usernames, hashtags


def extend_month_year_values(df, for_chart):
    assert for_chart in ['interactions', 'volume'], "for_chart argument should be one of 'interactions' or 'volume'"

    years = df['tweet_time'].dt.year.unique()
    years = years[~np.isnan(years)]  # remove NaNs, otherwise max and min do not work
    max_year, min_year = int(years.max()), int(years.min())

    month_year_extended = pd.date_range(datetime(min_year, 1, 1), datetime(max_year, 12, 31), freq='MS')
    month_year_extended = month_year_extended.month_name().str[:3] + ' ' + month_year_extended.year.astype(str)

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
        'value': 0,
        'n interactions': 0
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


def create_hist_account_creations(df_users_creation_dates):

    df_users_creation_dates = pd.concat(df_users_creation_dates)

    df_users_creation_dates = df_users_creation_dates.groupby('user_screen_name')['account_creation_date'].first().reset_index()

    df_users_creation_dates['month_year_account'] = df_users_creation_dates['account_creation_date'].dt.month_name().str[:3] + ' ' + df_users_creation_dates['account_creation_date'].dt.year.astype(str)
    accounts_created_per_month = df_users_creation_dates.groupby('month_year_account').size()
    years = df_users_creation_dates['account_creation_date'].dt.year.unique()
    max_year, min_year = years.max(), years.min()

    month_year_extended = pd.date_range(datetime(min_year, 1, 1), datetime(max_year, 12, 31), freq='MS')
    month_year_extended = month_year_extended.month_name().str[:3] + ' ' + month_year_extended.year.astype(str)

    accounts_created_per_month = accounts_created_per_month.reindex(month_year_extended).fillna(0)

    return accounts_created_per_month


def plot_density(heatmap_df, fname_prefix='', results_folder='', show_chart=False):
    plt.figure()
    ax = sns.heatmap(heatmap_df.pivot('weekday', 'hour', 'n_tweets').fillna(0), annot=False,
                     linewidths=.5)  # pivot is used to make the DF rectangular
    plt.title(f"Tweets daily rhythm", fontsize=18)
    if not show_chart:
        plt.savefig(f'{results_folder}/{fname_prefix}_density.png', bbox_inches='tight', dpi=200)
        plt.close()
    else:
        return ax


def plot_tweets_vs_retweets(df_tweets_stats, results_folder='', fname_prefix='', csv_out=False, show_chart=False):
    df_rtw = df_tweets_stats.groupby(['month_year', 'is_retweet']).agg({
        'n_tweets': 'sum',
        'tweet_time': 'first'
    }).reset_index().sort_values('tweet_time')

    df_rtw = extend_month_year_values(df_rtw, 'volume')

    if csv_out:
        df_rtw.drop(columns=['tweet_time']).to_csv(os.path.join(results_folder, 'Tweet vs Retweets.csv'))

    ax = sns.lineplot(data=df_rtw, x='month_year', y='n_tweets', hue='is_retweet', sort=False)
    ax.xaxis.set_major_locator(ticker.AutoLocator())
    plt.xticks(rotation=45, fontsize=15)
    plt.title(f'Tweets vs Retweets', fontsize=18)
    if not show_chart:
        plt.savefig(f'{results_folder}/{fname_prefix}_tweets_vs_retweets.png', bbox_inches='tight', dpi=200)
        plt.close()
    else:
        return ax


def plot_interactions(df_tweets_stats, results_folder='', fname_prefix='', csv_out=False, show_chart=False):
    interactions_per_date = df_tweets_stats.groupby(['month_year']).agg({
        'quote_count': 'sum',
        'like_count': 'sum',
        'retweet_count': 'sum',
        'reply_count': 'sum',
        'tweet_time': 'first'
    }).reset_index().sort_values('tweet_time')

    interactions_per_date = interactions_per_date.melt(
        id_vars=['month_year', 'tweet_time'],
        var_name='interaction',
        value_name='n interactions'
    )
    interactions_per_date = extend_month_year_values(interactions_per_date, 'interactions')

    if csv_out:
        interactions_per_date.to_csv(os.path.join(results_folder, 'Interactions.csv'))

    plt.figure(figsize=(15, 8))
    ax = sns.lineplot(data=interactions_per_date, x='month_year', y='n interactions',
                      hue='interaction', sort=False)
    # x_ticks = interactions_per_date['month_year'].drop_duplicates().reset_index(drop=True)
    # plt.xticks(np.arange(0, len(x_ticks), 3), x_ticks, rotation=45, fontsize=5)
    plt.xticks(rotation=45, fontsize=15)
    ax.xaxis.set_major_locator(ticker.AutoLocator())
    plt.title(f'Volume per interaction', fontsize=18)
    if not show_chart:
        plt.savefig(f'{results_folder}/{fname_prefix}_volume_interactions.png', bbox_inches='tight', dpi=250)
        plt.close()
    else:
        return ax


def plot_heatmap(df_heatmaps, results_folder='', fname_prefix='', csv_out=False, show_chart=False):
    df_heatmaps = df_heatmaps.groupby(['hour', 'weekday']).sum().reset_index()

    df_heatmaps['weekday'] = pd.Categorical(
        df_heatmaps['weekday'],
        categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        ordered=True)

    if csv_out:
        df_heatmaps.to_csv(os.path.join(results_folder, 'heatmap.csv'))

    # plot
    ax = sns.heatmap(df_heatmaps.pivot('weekday', 'hour', 'n_tweets').fillna(0), annot=False,
                     linewidths=.5)  # pivot is used to make the DF rectangular
    plt.title(f"Tweets daily rhythm", fontsize=15)
    if not show_chart:
        plt.savefig(f'{results_folder}/{fname_prefix}_density.png', bbox_inches='tight', dpi=200)
        plt.close()
    else:
        return ax


def plot_client_histogram(df_client_hist, results_folder='', fname_prefix='', csv_out=False, show_chart=False):
    client_hist = df_client_hist.groupby('tweet_client_name').sum().sort_values('# tweets',
                                                                                ascending=False).reset_index()

    hist_short = client_hist[:30].copy()
    hist_short = hist_short.append(
        {'tweet_client_name': 'Others', '# tweets': client_hist[30:].sum()['# tweets']},  # last row with "Others"
        ignore_index=True)

    if csv_out:
        hist_short.to_csv(os.path.join(results_folder, 'client_histograms.csv'))

    # plot
    plt.xticks(rotation='vertical', fontsize=15)
    ax = plt.bar(x=hist_short['tweet_client_name'], height=hist_short['# tweets'],
                 color='#2196f3', edgecolor='#64b5f6', width=0.5)
    plt.title(f'Tweets per client', fontsize=18)
    if not show_chart:
        plt.savefig(f'{results_folder}/{fname_prefix}_tweets_per_client.png', bbox_inches='tight', dpi=250)
        plt.close()
    else:
        return ax


def plot_language_histogram(df_lang_hist, results_folder='', fname_prefix='', csv_out=False, show_chart=False):
    lang_hist = df_lang_hist.groupby('tweet_language').sum().sort_values('# tweets', ascending=False).reset_index()

    hist_short = lang_hist[:30].copy()
    hist_short = hist_short.append(
        {'tweet_language': 'Others', '# tweets': lang_hist[30:].sum()['# tweets']},  # last row with "Others"
        ignore_index=True)

    hist_short['tweet_language'] = hist_short['tweet_language'].apply(
        lambda x: langcodes.Language.make(language=x).language_name())

    if csv_out:
        hist_short.to_csv(os.path.join(results_folder, 'language_histograms.csv'))

    # plot
    plt.xticks(rotation='vertical', fontsize=15)
    ax = plt.bar(x=hist_short['tweet_language'], height=hist_short['# tweets'],
                 color='#2196f3', edgecolor='#64b5f6', width=0.5)

    plt.title(f'Tweets per language', fontsize=10)
    if not show_chart:
        plt.savefig(f'{results_folder}/{fname_prefix}_tweets_per_lang.png', bbox_inches='tight', dpi=250)
        plt.close()
    else:
        return ax


def plot_accounts_created_per_month(df_accounts_per_month, results_folder='', fname_prefix='',
                                    csv_out=False, show_chart=False):
    if csv_out:
        df_accounts_per_month.to_csv(os.path.join(results_folder, 'accounts_created_monthly.csv'), header=True)

    ax = plt.bar(x=df_accounts_per_month.index,
                 height=df_accounts_per_month,
                 color='#2196f3',
                 edgecolor='#64b5f6',
                 width=0.5)

    x_ticks = df_accounts_per_month.index
    plt.xticks(np.arange(0, len(x_ticks), 4), x_ticks[np.arange(0, len(x_ticks), 4)], rotation=60, fontsize=12)

    plt.title(f'Accounts created per month', fontsize=18)
    if not show_chart:
        plt.savefig(f'{results_folder}/{fname_prefix}_accounts_created.png', bbox_inches='tight', dpi=250)
        plt.close()
    else:
        return ax


def plot_wordcloud_retweets(list_rtw_usernames, results_folder='', fname_prefix='', show_chart=False):
    twitter_mask = np.array(Image.open('twitter_mask.png'))

    wcloud = WordCloud(
        background_color="white",
        colormap=matplotlib.cm.winter,
        collocations=False,
        mask=twitter_mask).generate(list_rtw_usernames)

    # plot
    ax = plt.imshow(wcloud, interpolation="bilinear")
    plt.axis('off')
    plt.title(f'Wordcloud of retweeted users', fontsize=18)
    plt.tight_layout()
    if not show_chart:
        plt.savefig(f'{results_folder}/{fname_prefix}_wordcloud_rw_users.png')
        plt.close()
    else:
        return ax


def plot_wordcloud_hashtags(list_hashtags, results_folder='', fname_prefix='', show_chart=False):
    twitter_mask = np.array(Image.open('twitter_mask.png'))

    wcloud = WordCloud(
        background_color="white",
        colormap=matplotlib.cm.winter,
        collocations=False,
        mask=twitter_mask).generate(list_hashtags)

    # plot
    # plt.figure(figsize=(12.8, 9.6), dpi=100)
    ax = plt.imshow(wcloud, interpolation="bilinear")
    plt.axis('off')
    plt.title(f'Wordcloud of hashtags', fontsize=18)
    plt.tight_layout()
    if not show_chart:
        plt.savefig(f'{results_folder}/{fname_prefix}_wordcloud_hashtags.png')
        plt.close()
    else:
        return ax


@click.command()
@click.option('--path', help='Path of the Twitter Dataset. Can be a single CSV file '
                             'or a directory containing multiple CSVs', required=True)
@click.option('-w', help='Include WordCloud in the analysis.', is_flag=True)
@click.option('--user', help='Optional argument. Run the analysis only for the selected user', required=False)
@click.option('--tlang', help='Optional argument. Language of tweets to analyze', required=False)
@click.option('--ulang', help='Optional argument. Language of accounts to analyze', required=False)
@click.option('--chunksize', help='Optional argument. Default is 1000000. Decrease if you run into memory issues', required=False, default=1000000)
@click.option('-v', help='Optional argument. Verbose mode that print more information', required=False, is_flag=True)
@click.option('--csv-out', help='Optional argument. Write output of analysis to CSV files', required=False, is_flag=True)
@timer
def run_analysis(path, w, user, tlang, ulang, chunksize, v, csv_out):
    if v:
        global VERBOSE
        VERBOSE = True

    if chunksize:
        global CHUNKSIZE
        CHUNKSIZE = chunksize

    if user is None:
        # if user is not specified, just name it "all". it will be included in the output filenames
        user_title = 'all'
    else:
        user_title = user

    if tlang is not None:
        tlang_title = langcodes.Language.make(language=tlang).language_name()
    else:
        tlang_title = 'all'

    if ulang is not None:
        ulang_title = langcodes.Language.make(language=ulang).language_name()
    else:
        ulang_title = 'all'

    title_prefix = f'User: {user_title} - TLang: {tlang_title} - ULang:{ulang_title}'
    fname_prefix = f'user-{user_title}__tlang-{tlang}__ulang-{ulang}'
    results_folder = f'{path.split("/")[-1]}_{user_title}_{tlang_title}_{ulang_title}'
    os.makedirs(results_folder, exist_ok=True)

    print('Parameters for this analysis:')
    print(title_prefix)
    print(f'Looking for CSV files based on --path parameter: {path}')

    file_list = find_csv(path)
    lines = [row_count(f) for f in file_list]
    lines = sum(lines)

    df_reader = read_list_of_csv(file_list, chunksize=CHUNKSIZE)

    print(f'Running with CHUNKZISE = {CHUNKSIZE} (default is 1000000). '
          f'If memory errors occur, please decrease chunksize parameter (i.e. --chunksize=250000)')

    # Prepare empty lists that will be progressively filled with data as we read chunks of files
    df_tweets_stats = []
    df_heatmaps = []
    df_client_hist = []
    df_lang_hist = []
    df_users_creation_dates = []
    list_rtw_usernames = ['']
    list_hashtags = ['']

    with tqdm(total=lines, ncols=80, file=sys.stdout) as pbar:  # instantiate TQDM progress bar
        for df in df_reader:
            tweets_stats, heatmap_df, client_hist, lang_hist, \
                users_creation_dates, rtw_usernames, hashtags = process_one_chunk(df, user=user, tlang=tlang, ulang=ulang)

            df_tweets_stats.append(tweets_stats)
            df_heatmaps.append(heatmap_df)
            df_client_hist.append(client_hist)
            df_lang_hist.append(lang_hist)
            df_users_creation_dates.append(users_creation_dates)
            list_rtw_usernames.extend(rtw_usernames)
            list_hashtags.extend(hashtags)
            # update progress bar
            pbar.update(len(df))

    print('Analysing tweets...')
    df_tweets_stats = pd.concat(df_tweets_stats)
    df_heatmaps = pd.concat(df_heatmaps)
    df_client_hist = pd.concat(df_client_hist)
    df_lang_hist = pd.concat(df_lang_hist)
    df_accounts_created_p_month = create_hist_account_creations(df_users_creation_dates)
    list_rtw_usernames = ' '.join(list_rtw_usernames)
    list_hashtags = ' '.join(list_hashtags)

    print('Plotting charts...')
    plot_heatmap(df_heatmaps, results_folder, fname_prefix, csv_out=csv_out)
    plot_tweets_vs_retweets(df_tweets_stats, results_folder, fname_prefix, csv_out=csv_out)
    plot_interactions(df_tweets_stats, results_folder, fname_prefix, csv_out=csv_out)
    plot_accounts_created_per_month(df_accounts_created_p_month, results_folder, fname_prefix, csv_out=csv_out)
    plot_client_histogram(df_client_hist, results_folder, fname_prefix, csv_out=csv_out)
    plot_language_histogram(df_lang_hist, results_folder, fname_prefix, csv_out=csv_out)
    if w:
        plot_wordcloud_retweets(list_rtw_usernames, results_folder, fname_prefix)
        plot_wordcloud_hashtags(list_hashtags, results_folder, fname_prefix)

    print('Done!')


if __name__ == '__main__':
    print(
        "\x1b[1;34;49m" + "\n\n                 ./oss+:    -\n /d:           .hMMMMMMMNydm/`\n hMMd+`       `NMMMMMMMMMMNdy-\n /MMMMMds/-`  /MMMMMMMMMMMN-         \n .+mMMMMMMMMNmmMMMMMMMMMMMm\n sMNMMMMMMMMMMMMMMMMMMMMMMs\n  sMMMMMMMMMMMMMMMMMMMMMMN.\n   -smMMMMMMMMMMMMMMMMMMM/\n   .dMMMMMMMMMMMMMMMMMMN:\n     :ydNMMMMMMMMMMMMMh.\n     `:omMMMMMMMMMMMy-\n./ymNMMMMMMMMMMMmy/`\n   `-/+ssssso/-`\n" + "\x1b[0m")
    print(
        "\x1b[1;39;49m" + "  Made with" + "\x1b[0m" + "\x1b[1;31;49m" + " ❤" + "\x1b[0m" + "\x1b[1;39;49m" + " - https://www.github.com/luigigubello (and https://www.github.com/naikio)" + "\x1b[0m\n\n")
    print('\x1b[1;39;49m' + 'Wait...' + '\x1b[0m')
    print()
    run_analysis()
