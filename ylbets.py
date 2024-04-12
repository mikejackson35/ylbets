import pandas as pd
import plotly.express as px
import numpy as np
import streamlit as st
import altair as alt

from utils import get_ev_table, plus_prefix

# Streamlit configs
st.set_page_config(
    page_title='ylbets',
    # page_icon='assets/Nevil.png',
    layout='centered'
    )

#plotly configs
config = {'displayModeBar': False}

# dg_key = st.secrets.dg_key
ph1 = st.empty()

market_type = st.selectbox(
    'Choose Market',
    ('win','top_5','top_10','top_20')
)

with st.expander('detail'):
    ph2 = st.empty()
    ph3 = st.empty()
    ph4 = st.empty()
    st.write("#")
    ph5 = st.empty()

def main():
    
    # makes EV table for user selected market ('win', 'top5', 'top10', or 'top20')
    df = get_ev_table(market_type)

    # fix column headers
    df.columns = ['Player','Odds','Agg','EV']

    # add styling  (ie. plus prefixes in front of integers and color 'ev' column)
    df['Odds'] = df['Odds'].apply(plus_prefix)
    df['Agg'] = df['Agg'].apply(plus_prefix)

    styled_df = df.style.background_gradient(
        cmap="cividis", subset=['EV'], vmin=-.2#, gmap= -df['EV']
        ).format(precision=2)

    return styled_df

ph1.header('ylbets')
ph2.write("Odds = real odds per datagolf.com")
ph3.write("Agg = average line being offered across all sportsbooks")
ph4.write("EV = expected value (ie. expected net profit on a 1-unit bet placed many times)")
ph5.write("Expected Value Example - Consider the example of betting on coin flips (which, really, is not so different from betting on golf). The probability of flipping Heads or Tails is equal to 50%. Suppose a bookmaker offers +100 American odds, which implies a probability of 1/2 or 50%. Given that the implied probability is equal to the true probability of Heads, the expected value from betting on Heads is zero. If a bookmaker offered odds of -110, the expected value would be negative (-5%, or -0.05 per unit bet); if a dumb bookmaker offered odds of +110, the expected value would then be positive (+5%), and in theory a bet worth taking.")

st.dataframe(main(), hide_index=True, height=3000 ,use_container_width=True)#, column_config={'Agg Line':None})