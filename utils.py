import pandas as pd
import plotly.express as px
import numpy as np
import streamlit as st

dg_key = "e297e933c3ad47d71ec1626c299e"
# market_type = 'top_20'

names_dict = {'Matt Fitzpatrick': 'Matthew Fitzpatrick',
    'Si Kim': 'Si Woo Kim',
    'Min Lee': 'Min Woo Lee',
    'Byeong An': 'Byeong Hun An',
    'Rooyen Van': 'Erik Van Rooyen',
    'Vince Whaley': 'Vincent Whaley',
    'Kevin Yu': 'Kevin Yu',
    'Kyounghoon Lee': 'Kyoung-Hoon Lee'
             }

def implied_probability(moneyline_odds):
    """
    Calculate the implied probability from moneyline odds.
    """
    # Convert negative odds to positive for calculation
    if moneyline_odds < 0:
        implied_prob = abs(moneyline_odds) / (abs(moneyline_odds) + 100)
    else:
        implied_prob = 100 / (moneyline_odds + 100)
    
    # Return implied probability as percentage
    return implied_prob

def fix_names(list_of_player_names):
    
    # swaps last/first into first/last name
    names = list_of_player_names.str.split(expand=True)                  
    names[0] = names[0].str.rstrip(",")
    names[1] = names[1].str.rstrip(",")
    names['player_name'] = names[1].str[0] + " " + names[0]

    # uses dictionary to correct known problem names
    # ie "Jr" or "Si Woo Kim")
    for incorrect_name, correct_name in names_dict.items():
        names['player_name'] = np.where(names['player_name'] == incorrect_name, correct_name, names['player_name'])

    return names.player_name

def plus_prefix(a):
    if a > 0:
        return f"+{a}"
    return a

market_target_dict = {
    'win':1.15,
    'top_5': 1.1,
    'top_10': 1.1,
    'top_20': 1.05
    }


def convert_euro_to_american(dec_odds):
    if dec_odds >= 2:
        return (dec_odds - 1) * 100
    else:
        return -100 / (dec_odds-1)
    
def get_our_plays(our_plays, url, columns):
    try:
        # Read CSV from URL, selecting specific columns
        df = pd.read_csv(url, usecols=columns).convert_dtypes()

        # Convert 'last_update' to datetime and extract time component
        # df['updated'] = pd.to_datetime(df['last_update']).dt.strftime('%H:%M')

        # # Drop 'last_update' column
        # df.drop(columns='last_update', inplace=True)

        # Format 'top_10' column as percentage
        df['top_10'] = ((df['top_10'] * 100).round()).astype(int).astype(str) + '%'

        # Filter DataFrame based on 'our_plays'
        plays = df[df['player_name'].isin(our_plays)].round(2)
        return plays

    except Exception as e:
        print("An error occurred:", e)
        return None
        


def get_ev_table(market_type):

    # api calls
    dg_american = pd.read_csv(f"https://feeds.datagolf.com/betting-tools/outrights?tour=pga&market={market_type}&odds_format=american&file_format=csv&key={dg_key}")
    dg_decimal = pd.read_csv(f"https://feeds.datagolf.com/betting-tools/outrights?tour=pga&market={market_type}&odds_format=decimal&file_format=csv&key={dg_key}")
    books = ['fanduel','bet365','pointsbet','draftkings']

    # grab american and euro DataGolf odds for each player and combine
    am_odds = dg_american[['player_name','datagolf_base_history_fit']]#.rename(columns={'datagolf_base_history_fit':'am_odds_dg'})
    dec_odds = dg_decimal[['player_name','datagolf_base_history_fit']]#.rename(columns={'datagolf_base_history_fit':'dec_odds_dg'})
    dg_odds = pd.merge(am_odds,dec_odds, on='player_name')

    # get avg sportbooks line for each player in american and euro formats
    agg_am = dg_american[books].T.max().to_frame()
    agg_dec = dg_decimal[books].T.max().to_frame()

    # combine and fix column names
    df = pd.merge(dg_odds, agg_am, left_index=True, right_index=True)
    df = pd.merge(df,agg_dec,left_index=True, right_index=True).T.drop_duplicates().T
    df.columns = ['player_name', 'am_odds','dec_odds','ag_am','ag_dec']

    # convert target euro odds to american for display
    df['market_type'] = market_type
    df['target_euro'] = df['market_type'].map(market_target_dict) * df['dec_odds']
    df['target_american'] = df['target_euro'].apply(convert_euro_to_american).astype(int)

    # add expected value column (for color)
    df['ev'] = (1 / df['dec_odds']) * df['ag_dec'] -1

    # flip first/last player names
    df['player_name'] = fix_names(df['player_name'])

    # column names
    df = df[['player_name','target_american','ev','am_odds','ag_am']]
    df = df.convert_dtypes().round(2)

    return df