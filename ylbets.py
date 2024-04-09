import pandas as pd
import plotly.express as px
import numpy as np
import streamlit as st
import altair as alt

#streamlit configs
st.set_page_config(page_title='ylBets',
                   page_icon='assets/Nevil.png',
                   layout='centered')

#plotly configs
config = {'displayModeBar': False}

#altair configs
alt.themes.enable("dark")

usecols = ['market','player_name','datagolf_base_history_fit','draftkings','fanduel','betmgm']

# get american odds

win_path = r"https://feeds.datagolf.com/betting-tools/outrights?tour=pga&market=win&odds_format=american&file_format=csv&key=e297e933c3ad47d71ec1626c299e"
win = round(pd.read_csv(win_path, usecols=usecols),2)

top5_path = r"https://feeds.datagolf.com/betting-tools/outrights?tour=pga&market=top_5&odds_format=american&file_format=csv&key=e297e933c3ad47d71ec1626c299e"
top5 = round(pd.read_csv(top5_path, usecols=usecols),2)

top10_path = r"https://feeds.datagolf.com/betting-tools/outrights?tour=pga&market=top_10&odds_format=american&file_format=csv&key=e297e933c3ad47d71ec1626c299e"
top10 = round(pd.read_csv(top10_path, usecols=usecols),2)

top20_path = r"https://feeds.datagolf.com/betting-tools/outrights?tour=pga&market=top_20&odds_format=american&file_format=csv&key=e297e933c3ad47d71ec1626c299e"
top20 = round(pd.read_csv(top20_path, usecols=usecols),2)

american_odds = pd.concat([win,top5,top10,top20])
american_odds = american_odds[['market','player_name','datagolf_base_history_fit','fanduel','draftkings','betmgm']].convert_dtypes()

# get decimal odds - make expected values

win_path = r"https://feeds.datagolf.com/betting-tools/outrights?tour=pga&market=win&odds_format=percent&file_format=csv&key=e297e933c3ad47d71ec1626c299e"
win = round(pd.read_csv(win_path, usecols=usecols),3)

top5_path = r"https://feeds.datagolf.com/betting-tools/outrights?tour=pga&market=top_5&odds_format=percent&file_format=csv&key=e297e933c3ad47d71ec1626c299e"
top5 = round(pd.read_csv(top5_path, usecols=usecols),3)

top10_path = r"https://feeds.datagolf.com/betting-tools/outrights?tour=pga&market=top_10&odds_format=percent&file_format=csv&key=e297e933c3ad47d71ec1626c299e"
top10 = round(pd.read_csv(top10_path, usecols=usecols),3)

top20_path = r"https://feeds.datagolf.com/betting-tools/outrights?tour=pga&market=top_20&odds_format=percent&file_format=csv&key=e297e933c3ad47d71ec1626c299e"
top20 = round(pd.read_csv(top20_path, usecols=usecols),3)

dec_odds = pd.concat([win,top5,top10,top20])
dec_odds = dec_odds[['market','player_name','datagolf_base_history_fit','fanduel','draftkings','betmgm']]

dec_odds['fanduel_ev'] = round(dec_odds['datagolf_base_history_fit'] * (1/dec_odds['fanduel']) - 1,2)
dec_odds['draftkings_ev'] = round(dec_odds['datagolf_base_history_fit'] * (1/dec_odds['draftkings']) - 1,2)
dec_odds['betmgm_ev'] = round(dec_odds['datagolf_base_history_fit'] * (1/dec_odds['betmgm']) - 1,2)

ev = dec_odds[['market','player_name','fanduel_ev','draftkings_ev','betmgm_ev']]


# merge

odds = pd.merge(american_odds,ev,how='left',on=['market','player_name']).round(2)
odds = odds[['market','player_name','datagolf_base_history_fit','fanduel','fanduel_ev','draftkings','draftkings_ev','betmgm','betmgm_ev']]
odds.rename(columns={'datagolf_base_history_fit':'real_odds'}, inplace=True)

def plus_prefix(a):
    if a > 0:
        b = f"+{a}"
    else:
        b = a
    return b

odds['real_odds'] = odds['real_odds'].dropna().apply(plus_prefix)
odds['fanduel'] = odds['fanduel'].dropna().apply(plus_prefix)
odds['draftkings'] = odds['draftkings'].dropna().apply(plus_prefix)
odds['betmgm'] = odds['betmgm'].dropna().apply(plus_prefix)

odds_dict = {
    'win':'Win',
    'top_5':'Top 5',
    'top_10':'Top 10',
    'top_20':'Top 20'
}
odds['market'] = odds['market'].map(odds_dict)

def fix_names(df):
    """
    Takes in live datagolf scoring, cleans names, outputs list of active players this week
    """
    names = df['player_name'].str.split(expand=True)                  
    names[0] = names[0].str.rstrip(",")
    names[1] = names[1].str.rstrip(",")
    names['player'] = names[1] + " " + names[0]

    return names.player

odds['player_name'] = fix_names(odds)

odds.columns = ['Market','Player','Odds','FD','FD EV','DK','DK EV','BetMGM','BetMGM EV']

market = st.selectbox(
    'Choose Betting Market',
    ('Win','Top 5','Top 10','Top 20')
)

odds = odds[odds.Market==market].dropna()

def df_style(val):
    return "font-weight: bold"



styled_odds = odds.style.background_gradient(cmap="gist_heat", subset=['FD EV','DK EV','BetMGM EV']).format(precision=2)#.applymap(df_style,subset=['Odds'])

st.dataframe(styled_odds, hide_index=True, height=2000,use_container_width=True, column_config={'Market':None})