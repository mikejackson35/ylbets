import pandas as pd
import plotly.express as px
import numpy as np
import streamlit as st
import altair as alt
from utils import fetch_odds, plus_prefix, fix_names,calc_ev


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

dg_key = "e297e933c3ad47d71ec1626c299e"

market_type = st.selectbox(
    'Choose Betting Market',
    ('win','top_5','top_10','top_20')
)

# get aggregate line for each golfer
books = ['betmgm', 'betfair', 'fanduel', 'draftkings', 'bovada',
       'williamhill', 'betonline', 'betcris', 'unibet', 'caesars', 'bet365',
       'betway', 'pinnacle', 'skybet', 'pointsbet']
agg_odds = fetch_odds(market_type).dropna().T.mean().round(0).to_frame()

# get datagolf line for each golfer
url = f"https://feeds.datagolf.com/betting-tools/outrights?tour=pga&market={market_type}&odds_format=american&file_format=csv&key={dg_key}"
dg_odds = pd.read_csv(url,usecols=['player_name','datagolf_base_history_fit']).dropna()

# merge
df = dg_odds.merge(agg_odds,left_index=True, right_index=True).rename(
            columns={'datagolf_base_history_fit':'real_odds',0:'agg_line'})

# add expected value column
df = calc_ev(df)

# flip names to first,last
df['player_name'] = fix_names(df)

# rename columns
df.columns = ['Player','Real','Books', 'EV']

# style
df['Real'] = df['Real'].apply(plus_prefix)
df['Books'] = df['Books'].apply(plus_prefix)
styled_df = df.style.background_gradient(cmap="gist_heat").format(precision=2)

st.dataframe(styled_df, hide_index=True, height=2000,use_container_width=True)