import pandas as pd
import plotly.express as px
import numpy as np
import streamlit as st
import altair as alt

from streamlit_extras.stoggle import stoggle
from utils import get_ev_table, get_our_plays, LIVE_ODDS

import secrets

## DISPLAY CONFIGS
# Streamlit
st.set_page_config(
    page_title='ylbets',
    page_icon=':eggplant:',
    layout='centered'
    )
# css
with open(r"styles/main.css") as f:                                          
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True) 
#plotly
config = {'displayModeBar': False}

dg_key = st.secrets.dg_key


## MAIN FUNCTION TO RUN THE APP
# takes user selection of market and displays the corresponding styled dataframe
def main():

    # inputs user selection and outputs un-styled dataframe with live odds and ev's
    df = get_ev_table(market_type)

    # fix column headers
    df.columns = ['Player','Target','EV','Odds','Books']

    # add styling  ("+" prefixes and color)
    df['Odds'] = df['Odds'].apply(lambda x: x if x < 0 else f"+{x}")
    df['Target'] = df['Target'].apply(lambda x: x if x < 0 else f"+{x}")

    styled_df = df.style.format(precision=2).background_gradient(
        cmap="cividis", subset=['EV'], vmin=-.1)

    return styled_df


## USER INTERFACE

# details dropdown
stoggle('info',
        """
        ----------------------------------------------------------------------------------------------------------------------------
        <br>
        TARGET - real odds + the ev target<br>
        <br>
        i.e. the datagolf model has real odds on Scottie Scheffler to Win at +550. As a general rule,<br>
        we're looking for 15% expected value on a Win bet. Therefore we want +650 or better <br>
        (the Target). If placed many times at +650, this wager has an expected net profit of 15%.<br>
        -----------------------------------------------------------------------------------------------------------------------------
        <br>
        EV - expected value for the best line found across all sportsbooks.<br>
        <br>
        Use this column to sort and find the best values at your book<br>
        ----------------------------------------------------------------------------------------------------------------------------
        <br>""")
# targets dropdown
stoggle('ev targets',
    """<br>
    Top  1 > .15<br>
    Top  5 > .10<br>
    Top 10 > .10<br>
    Top 20 > .05<br>
    """)


# TITLE
title_placeholder = st.empty()

# OUR PLAYS TABLE
list_of_our_plays = [
    'Meissner, Mac',
    'Endycott, Harrison',
    'Hubbard, Mark',
    'Schenk, Adam',
    'Sigg, Greyson',
    'Cummins, Quade']

live_odds = LIVE_ODDS

st.markdown(" ")
st.markdown("Our Plays", unsafe_allow_html=True)
our_plays_table = get_our_plays(list_of_our_plays, LIVE_ODDS)

st.dataframe(
    our_plays_table, 
    hide_index=True,
    # use_container_width=True
    )

# USER SELECTBOX
st.markdown(" ")
market_type = st.selectbox('Choose Market',
                           ('win','top_5','top_10','top_20'))

# for TITLE placeholder above
with title_placeholder:
    st.header('ylbets :eggplant:')

# TARGET EV TABLE
st.dataframe(
    main(),
    hide_index=True,
    height=4000,
    use_container_width=True,
    column_config={
        'Odds':None,
        'Books':None
        }
        )