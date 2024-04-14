import pandas as pd
import plotly.express as px
import numpy as np
import streamlit as st

dg_key = "e297e933c3ad47d71ec1626c299e"
market_type = 'top_20'

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

def get_ev_table(market_type):

    # constants
    dg_outrights_data = pd.read_csv(f"https://feeds.datagolf.com/betting-tools/outrights?tour=pga&market={market_type}&odds_format=american&file_format=csv&key={dg_key}")
    dec_odds = pd.read_csv(f"https://feeds.datagolf.com/betting-tools/outrights?tour=pga&market={market_type}&odds_format=decimal&file_format=csv&key={dg_key}")
    books = ['betmgm', 'draftkings','caesars']

    # get dg 'real' odds, industry aggregate odds in american/moneyline and euro/decimal formats
    real_odds = dg_outrights_data[['player_name','datagolf_base_history_fit']]
    agg_lines = dg_outrights_data[books].T.mean().to_frame()
    agg_dec_lines = dec_odds[books].T.mean().to_frame()

    # merge together, fix headers, drop nulls
    df = pd.merge(real_odds, agg_lines, left_index=True, right_index=True)
    df = pd.merge(df,agg_dec_lines,left_index=True, right_index=True).T.drop_duplicates().T
    df.columns = ['player_name','real_odds','agg_line','agg_dec_line']
    df = df.dropna()

    # add expected value column and clean datatypes
    df['implied_prob'] = df['real_odds'].apply(implied_probability) 
    df['ev'] = df['implied_prob'] * df['agg_dec_line'] -1
    df = df[['player_name','real_odds','ev','agg_line']].convert_dtypes().round(2)
    df['agg_line'] = df['agg_line'].astype(int)

    # flip first/last names
    df['player_name'] = fix_names(df['player_name'])

    return df