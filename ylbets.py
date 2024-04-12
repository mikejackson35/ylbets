import pandas as pd
import plotly.express as px
import numpy as np
import streamlit as st
import altair as alt

from utils import get_ev_table, plus_prefix

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

# dg_key = st.secrets.dg_key
title_placeholder = st.empty()

market_type = st.selectbox(
    'Choose Betting Market',
    ('win','top_5','top_10','top_20')
)

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

with title_placeholder:
    st.subheader('ylbets')

st.dataframe(main(), hide_index=True, height=3000,use_container_width=True)#, column_config={'Agg Line':None})