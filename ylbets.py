import pandas as pd
import plotly.express as px
import numpy as np
import streamlit as st
import altair as alt

from streamlit_extras.stoggle import stoggle
from utils import get_ev_table, get_our_plays_table, LIVE_ODDS, fix_names, get_update_stamp

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
def main():
    """
    inputs user selection and outputs un-styled dataframe with live odds and ev's
    """
    df = get_ev_table(market_type)

    df = (
        df[['player_name','target_american','target_decimal','ev']].dropna()
        .assign(player_name=lambda x: fix_names(x['player_name']))
    ).rename(columns={'player_name':'Player','target_american':'Target US','target_decimal':'Target Euro','ev':'EV'})

    df = df.dropna()
    # add styling  ("+" prefixes and color)
    df['Target US'] = df['Target US'].round(-2).astype(int).apply(lambda x: x if x <= 0 else f"+{x}")
    df['Target Euro'] = df['Target Euro'].astype(int).apply(lambda x: f"{x}-1")
    

    styled_df = df.style.format(precision=2).background_gradient(
        cmap="cividis", subset=['EV'], vmin=-.1)

    return styled_df


## USER INTERFACE

# details dropdown
stoggle('about',
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
our_plays = [
    'Horschel, Billy',
    'Poston, J.T.',
    'McCarthy, Denny',
    ]

# st.markdown(" ")
# st.markdown(f"<h4>Live Plays</h4>", unsafe_allow_html=True)

# expander = st.expander("CLICK to see our lines")
# with expander:
#     st.write("McCarthy<br><small>win +5000<br> T5 +1000<br> T10 +450",unsafe_allow_html=True)
#     st.write(" ")
#     st.write("Horschel<br><small>T5 +1100<br>T10 +530",unsafe_allow_html=True)
#     st.write(" ")
#     st.write("Poston<br><small>T5  +1400<br>T10 +600",unsafe_allow_html=True)
#     st.write(" ")


# st.caption(f"last update: {get_update_stamp(LIVE_ODDS)['last_update'][0]}", unsafe_allow_html=True)
# our_plays_table = get_our_plays_table(our_plays)

# st.dataframe(
#     our_plays_table.style.background_gradient(cmap='cividis', subset=['% T10','% T5']),#,'% Win']), 
#     hide_index=True,
#     # use_container_width=True
#     )

# "---"
# USER SELECTBOX
st.markdown(" ")
market_type = st.selectbox('Choose Market',
                           ('win','top_5','top_10','top_20'))

# for TITLE placeholder above
with title_placeholder:
    st.header('ylbets :eggplant:')
    # st.write(get_update_stamp)

on = st.toggle("american / euro")

if on:
    odds_type_selection = 'Target US'
else:
    odds_type_selection = 'Target Euro'

# TARGET EV TABLE
st.dataframe(
    main(),
    hide_index=True,
    height=6000,
    use_container_width=True,
    column_config={
        # 'Odds':None,
        odds_type_selection:None
        }
        )