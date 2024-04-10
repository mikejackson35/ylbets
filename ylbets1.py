import pandas as pd
import plotly.express as px
import numpy as np
import streamlit as st
import altair as alt
from utils import fetch_odds, calculate_ev, plus_prefix, fix_names

dg_key = "e297e933c3ad47d71ec1626c299e"

# Streamlit configs
st.set_page_config(
    page_title='ylBets',
    # page_icon='assets/Nevil.png',
    layout='centered'
    )

#plotly configs
config = {'displayModeBar': False}

#altair configs
alt.themes.enable("dark")

odds = fetch_odds('win')
odds = pd.concat([odds, fetch_odds('top_5'), fetch_odds('top_10'), fetch_odds('top_20')]).dropna()

odds.rename(columns={'datagolf_base_history_fit':'real_odds'},inplace=True)
odds['player_name'] = fix_names(odds)

odds = calculate_ev(odds)

odds = odds[['market', 'player_name', 'real_odds', 'fanduel','fanduel_ev', 'draftkings','draftkings_ev', 'betmgm','betmgm_ev']].convert_dtypes()

odds['real_odds'] = odds['real_odds'].dropna().apply(plus_prefix)
odds['fanduel'] = odds['fanduel'].dropna().apply(plus_prefix)
odds['draftkings'] = odds['draftkings'].dropna().apply(plus_prefix)
odds['betmgm'] = odds['betmgm'].dropna().apply(plus_prefix)

odds['market'] = odds['market'].replace({'win': 'Win', 'top_5': 'Top 5', 'top_10': 'Top 10', 'top_20': 'Top 20'})

odds.columns = ['Market','Player','True Odds','FD','FD EV','DK','DK EV','MGM','MGM EV']

# Display
market = st.selectbox('Choose Betting Market', ('Win', 'Top 5', 'Top 10', 'Top 20'))

odds = odds[odds.Market==market].dropna()
styled_odds = odds.style.background_gradient(cmap="gist_heat", subset=['FD EV', 'DK EV', 'MGM EV']).format(precision=2)

st.dataframe(styled_odds, hide_index=True, height=2000, use_container_width=True, column_config={'Market': None})