import pandas as pd
import plotly.express as px
import numpy as np
import streamlit as st
import altair as alt

from utils import get_ev_table, fix_names


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

dg_key = st.secrets.dg_key

market_type = st.selectbox(
    'Choose Betting Market',
    ('win','top_5','top_10','top_20')
)

def main():
    
    df = get_ev_table(market_type)

    # fix names and column headers
    df['player_name'] = fix_names(df)
    df.columns = ['Player','Real Odds','Agg Line','EV']

    styled_df = df.style.background_gradient(cmap="gist_heat", subset=['EV']).format(precision=2)
    return styled_df

st.dataframe(main(), hide_index=True, height=3000,use_container_width=True, column_config='Agg Line':False)