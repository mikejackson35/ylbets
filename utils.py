import pandas as pd
import plotly.express as px
import numpy as np
import streamlit as st
import constants as c

dg_key = st.secrets.dg_key

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
    """
    Swaps names to first,last and cleans multi-word names
    """
    names = df['player_name'].str.split(expand=True)                  
    names[0] = names[0].str.rstrip(",")
    names[1] = names[1].str.rstrip(",")
    names['player'] = names[1] + " " + names[0]

    corrections = {
    'Matt Fitzpatrick': 'Matthew Fitzpatrick',
    'Si Kim': 'Si Woo Kim',
    'Min Lee': 'Min Woo Lee',
    'Byeong An': 'Byeong Hun An',
    'Rooyen Van': 'Erik Van Rooyen',
    'Vince Whaley': 'Vincent Whaley',
    'Kevin Yu': 'Kevin Yu',
    'Kyounghoon Lee': 'Kyoung-Hoon Lee'
}

    for incorrect_name, correct_name in corrections.items():
        names['player_name'] = np.where(names['player_name'] == incorrect_name, correct_name, names['player'])

    # names['player_name'] = np.where(names['player_name']=='Matt Fitzpatrick', 'Matthew Fitzpatrick', names['player'])
    # names['player_name'] = np.where(names['player_name']=='Si Kim', 'Si Woo Kim', names['player'])
    # names['player_name'] = np.where(names['player_name']=='Min Lee', 'Min Woo Lee', names['player'])
    # names['player_name'] = np.where(names['player_name']=='Byeong An', 'Byeong Hun An', names['player'])
    # names['player_name'] = np.where(names['player_name']=='Rooyen Van', 'Erik Van Rooyen', names['player'])
    # names['player_name'] = np.where(names['player_name']=='Vince Whaley', 'Vincent Whaley', names['player'])
    # names['player_name'] = np.where(names['player_name']=='Kevin Yu', 'kevin Yu', names['player'])
    # names['player_name'] = np.where(names['player_name']=='Kyounghoon Lee', 'Kyoung-Hoon Lee', names['player'])

    return names.player_name

def plus_prefix(a):
    if a > 0:
        return f"+{a}"
    return a

def get_ev_table(market_type):
    # get datagolf line for each golfer
    url = c.URL_AM
    dg_odds = pd.read_csv(url,usecols=['player_name','datagolf_base_history_fit']).dropna()

    books = ['betmgm', 'betfair', 'fanduel', 'draftkings', 'bovada',
        'williamhill', 'betonline', 'unibet', 'bet365',
        'betway', 'skybet', 'pointsbet']

    url = c.URL_AM
    am_odds = pd.read_csv(url,usecols=books).T.mean().to_frame()

    dg_odds = dg_odds.merge(am_odds,left_index=True, right_index=True)

    url = c.URL_DEC
    dec_odds = pd.read_csv(url,usecols=books).T.mean().to_frame()

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
    df['ev'] = df['ev'].dropna().apply(plus_prefix)

    return df