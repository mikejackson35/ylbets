import pandas as pd
import plotly.express as px
import numpy as np
import streamlit as st

dg_key = "e297e933c3ad47d71ec1626c299e"

# def fetch_odds(market):
#     odds_format = 'american'
#     odds = {}
#     for market_type in ['win', 'top_5', 'top_10', 'top_20']:
#         url = f"https://feeds.datagolf.com/betting-tools/outrights?tour=pga&market={market_type}&odds_format={odds_format}&file_format=csv&key={dg_key}"
#         usecols = ['market', 'player_name', 'datagolf_base_history_fit', 'draftkings', 'fanduel', 'betmgm']
#         data = pd.read_csv(url)#, usecols=usecols)
#         odds[market_type] = round(data, 2)
#     return odds[market]

def fetch_odds(market_type):
    url = f"https://feeds.datagolf.com/betting-tools/outrights?tour=pga&market={market_type}&odds_format=american&file_format=csv&key={dg_key}"
    usecols = ['betmgm', 'betfair', 'fanduel', 'draftkings', 'bovada',
       'williamhill', 'betonline','unibet', 'caesars', 'bet365',
       'betway','skybet', 'pointsbet']
    odds = round(pd.read_csv(url, usecols=usecols),2)
    return odds.dropna()

def calculate_ev(odds):
    odds['fanduel_ev'] = round(odds['real_odds'] * (1 / odds['fanduel']) - 1, 2)
    odds['draftkings_ev'] = round(odds['real_odds'] * (1 / odds['draftkings']) - 1, 2)
    odds['betmgm_ev'] = round(odds['real_odds'] * (1 / odds['betmgm']) - 1, 2)
    return odds#[['fanduel_ev', 'draftkings_ev', 'betmgm_ev']]

def calc_ev(df):
    df['implied_prob'] = 100 / (df['real_odds']+100)
    df['dec_agg_line'] = df['agg_line'] / 100 + 1
    df['ev'] = round(df['implied_prob'] * df['dec_agg_line'] -1,2)

    df.drop(columns = ['implied_prob','dec_agg_line'], inplace=True)

    df[['real_odds','agg_line']] = df[['real_odds','agg_line']].astype(int)
    return df

def plus_prefix(a):
    if a > 0:
        return f"+{a}"
    return a

def fix_names(df):
    """
    Takes in live datagolf scoring, cleans names, outputs list of active players this week
    """
    names = df['player_name'].str.split(expand=True)                  
    names[0] = names[0].str.rstrip(",")
    names[1] = names[1].str.rstrip(",")
    names['player'] = names[1] + " " + names[0]

    return names.player