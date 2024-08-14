import pandas as pd
import plotly.express as px
import numpy as np
import streamlit as st
import secrets

dg_key = st.secrets.dg_key

LIVE_ODDS = f"https://feeds.datagolf.com/preds/in-play?tour=pga&dead_heat=no&odds_format=percent&file_format=csv&key={dg_key}"

names_dict = {'Matt Fitzpatrick': 'Matthew Fitzpatrick',
    'Si Kim': 'Si Woo Kim',
    'Min Lee': 'Min Woo Lee',
    'Byeong An': 'Byeong Hun An',
    'Rooyen Van': 'Erik Van Rooyen',
    'Vince Whaley': 'Vincent Whaley',
    'kevin Yu': 'Kevin Yu',
    'Kyounghoon Lee': 'Kyoung-Hoon Lee',
    'Jr Hale': 'Blane Hale Jr',
    'de Dumont': 'Adrien Dumont de Chassart'
             }

def implied_probability(moneyline_odds):
    """
    Input: moneyline odds
    Output: implied probability
    """
    if moneyline_odds < 0:
        implied_prob = abs(moneyline_odds) / (abs(moneyline_odds) + 100)
    else:
        implied_prob = 100 / (moneyline_odds + 100)
    return implied_prob

def fix_names(list_of_player_names):
    """
    Inputs: list of player names in lastName, firstName format
    Outputs: list of clean player names in firstName lastName format
    """
    names = list_of_player_names.str.split(expand=True)                  
    names[0] = names[0].str.rstrip(",")
    names[1] = names[1].str.rstrip(",")
    names['player_name'] = names[1].str[0] + " " + names[0]

    # uses dictionary to correct known problem names
    # ie "Jr" or "Si Woo Kim")
    for incorrect_name, correct_name in names_dict.items():
        names['player_name'] = np.where(names['player_name'] == incorrect_name, correct_name, names['player_name'])

    return names.player_name

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
    
def get_our_plays_table(our_plays):
    try:
        # read in live odds
        df = pd.read_csv(LIVE_ODDS).convert_dtypes()
        df = df[['player_name', 'current_score', 'current_pos', 'win', 'top_10']]

        # format percentages
        df['win'] = ((df['win'] * 100).round()).astype(int)#.astype(str) + '%'
        # df['top_5'] = ((df['top_5'] * 100).round()).astype(int)#.astype(str) + '%'
        df['top_10'] = ((df['top_10'] * 100).round()).astype(int)#.astype(str) + '%'
        # df['top_20'] = ((df['top_20'] * 100).round()).astype(int)#.astype(str) + '%'

        # filter to selected plays and needed columns
        our_plays_table = df[df['player_name'].isin(our_plays)].round(2).reset_index(drop=True)
        our_plays_table['player_name'] = fix_names(our_plays_table['player_name'])
        our_plays_table['current_score'] = np.where(our_plays_table['current_score'] == 0, " E", our_plays_table['current_score']).astype(str)
        our_plays_table = our_plays_table.sort_values('current_score')
        our_plays_table.columns = ['Player', 'Tot', 'Pos','% Win','% T10']

        return our_plays_table

    except Exception as e:
        print("An error occurred:", e)
        return None
    
def get_update_stamp(live_odds):
    time_stamp = pd.read_csv(live_odds, usecols=['last_update'])
    time_stamp['last_update'] = pd.to_datetime(time_stamp['last_update']).dt.strftime('%H:%M')
    return time_stamp
        

def get_ev_table(market_type):

    # api calls
    dg_american = pd.read_csv(f"https://feeds.datagolf.com/betting-tools/outrights?tour=pga&market={market_type}&odds_format=american&file_format=csv&key={dg_key}")
    dg_decimal = pd.read_csv(f"https://feeds.datagolf.com/betting-tools/outrights?tour=pga&market={market_type}&odds_format=decimal&file_format=csv&key={dg_key}")

    # grab american and euro DataGolf odds for each player and combine
    am_odds = dg_american[['player_name','datagolf_base_history_fit']].rename(columns={'datagolf_base_history_fit':'am_odds_dg'})
    dec_odds = dg_decimal[['player_name','datagolf_base_history_fit']].rename(columns={'datagolf_base_history_fit':'dec_odds_dg'})
    dg_odds = pd.merge(am_odds,dec_odds, on='player_name')

    # get best sportbooks line for each player in american and euro formats
    # agg_am = dg_american.drop(columns=['player_name','dg_id','datagolf_baseline','datagolf_base_history_fit','last_updated','event_name','market']).T.max().to_frame()
    # agg_dec = dg_decimal.drop(columns=['player_name','dg_id','datagolf_baseline','datagolf_base_history_fit','last_updated','event_name','market']).T.max().to_frame()

    agg_am = dg_american[['unibet']].rename(columns={'unibet':0})
    agg_dec = dg_decimal[['unibet']].rename(columns={'unibet':0})

    df = pd.merge(dg_odds, agg_am, left_index=True, right_index=True)
    df = pd.merge(df,agg_dec,left_index=True, right_index=True).T.drop_duplicates().T
    df.columns = ['player_name', 'dg_american','dg_decimal','books_mean_american','books_mean_decimal']

    df['market_type'] = market_type
    df['market_target'] = df['market_type'].map(market_target_dict)
    df['target_decimal'] = (df['dg_decimal'] * df['market_target']).astype(float)
    df['target_american'] = df['target_decimal'].apply(lambda x: convert_euro_to_american(x))


    # add expected value column (for color)
    df['ev'] = ((1 / df['dg_decimal']) * df['books_mean_decimal'] -1)

    return df