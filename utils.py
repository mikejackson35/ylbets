import pandas as pd
import plotly.express as px
import numpy as np
import streamlit as st

dg_key = st.secrets.dg_key

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
        moneyline_odds = abs(moneyline_odds) + 100
    
    # Calculate implied probability
    implied_prob = 100 / (moneyline_odds + 100)
    
    # Return implied probability as percentage
    return implied_prob

def fix_names(df):
    
    # swaps last/first into first/last name
    names = df['player_name'].str.split(expand=True)                  
    names[0] = names[0].str.rstrip(",")
    names[1] = names[1].str.rstrip(",")
    names['player_name'] = names[1] + " " + names[0]

    # uses dictionary to correct known problem names
    # ie "Jr" or "Si Woo Kim")
    for incorrect_name, correct_name in names_dict.items():
        names['player_name'] = np.where(names['player_name'] == incorrect_name, correct_name, names['player_name'])

    return names.player_name

def plus_prefix(a):
    if a > 0:
        return f"+{a}"
    return a

def get_ev_table(market_type):

    books = ['betmgm', 'betfair', 'fanduel', 'draftkings', 'bovada','williamhill', 'betonline', 'unibet', 'bet365','betway', 'skybet', 'pointsbet']

    # get dg and aggregate book lines for each golfer
    url_am = f"https://feeds.datagolf.com/betting-tools/outrights?tour=pga&market={market_type}&odds_format=american&file_format=csv&key={dg_key}"
    dg_odds = pd.read_csv(url_am,usecols=['player_name','datagolf_base_history_fit']).dropna()

    dg_odds_ = dg_odds[books].T.mean().to_frame() 

    # aggregate book lines
    # books = ['betmgm', 'betfair', 'fanduel', 'draftkings', 'bovada','williamhill', 'betonline', 'unibet', 'bet365','betway', 'skybet', 'pointsbet']
    # dg_odds_ = pd.read_csv(url_am,usecols=books).T.mean().to_frame()                                # gets aggregate book lines
    dg_odds = dg_odds.merge(dg_odds_,left_index=True, right_index=True) 


    url_dec = f"https://feeds.datagolf.com/betting-tools/outrights?tour=pga&market={market_type}&odds_format=decimal&file_format=csv&key={dg_key}"
    books = ['betmgm', 'betfair', 'fanduel', 'draftkings', 'bovada','williamhill', 'betonline', 'unibet', 'bet365','betway', 'skybet', 'pointsbet']
    dec_odds = pd.read_csv(url_dec,usecols=books).T.mean().to_frame()

    df = dg_odds.merge(dec_odds,left_index=True, right_index=True).rename(
                columns={
                    # 'player_name':'player',
                    'datagolf_base_history_fit':'real_odds',
                    '0_x':'agg_line',
                    '0_y':'agg_dec'
                    }
                    )
    
    df['implied_prob'] = df['real_odds'].apply(implied_probability)
    df['ev'] = df['implied_prob'] * df['agg_dec'] -1
    df = df[['player_name','real_odds','agg_line','ev']].convert_dtypes().round(2)

    df['agg_line'] = df['agg_line'].astype(int)

    df['real_odds'] = df['real_odds'].dropna().apply(plus_prefix)
    df['agg_line'] = df['agg_line'].dropna().apply(plus_prefix)

    return df