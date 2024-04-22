import pandas as pd
import plotly.express as px
import numpy as np
import streamlit as st
import altair as alt

from streamlit_extras.stoggle import stoggle
from utils import get_ev_table, plus_prefix, get_our_plays

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


## MAIN FUNCTION TO RUN THE APP
# takes user selection of market and displays the corresponding styled dataframe
def main():

    # inputs user selection and outputs un-styled dataframe with live odds and ev's
    df = get_ev_table(market_type)

    # fix column headers
    # df.columns = ['Player','Odds','EV','Agg']
    df.columns = ['Player','Target','EV','Odds','Books']

    # add styling  ("+" prefixes and color)
    df['Odds'] = df['Odds'].apply(plus_prefix)
    df['Target'] = df['Target'].apply(plus_prefix)

    styled_df = df.style.format(precision=2).background_gradient(
        cmap="cividis", subset=['EV'], vmin=-.1#, gmap= -df['EV']
        )#.format(precision=2)

    return styled_df


## USER INTERFACE

# details dropdown
stoggle('info',
        """<br>
        TARGET = datagolf real odds + the ev target. Example, the datagolf model has real odds on Scottie Scheffler to Win at +550. As a general rule, we're looking for 15% expected value on a Win bet. Therefore we want +650 or better (the Target). If made many times at +650, this wager has an expected net profit of 15%.<br><br>
        EV = the expected value for the best line found across all sportsbooks. Use this to help find value. The better values across these books should be fairly similiar to the value at yours. 
        """)
# targets dropdown
stoggle('ev targets',
    """<br>
    Top  1 > .15<br>
    Top  5 > .10<br>
    Top 10 > .10<br>
    Top 20 > .05<br>
    """)


# placeholder for title
title_placeholder = st.empty()

# user selectbox
market_type = st.selectbox('Choose Market',
                           ('win','top_5','top_10','top_20'))

# title
title_placeholder.header('ylbets :eggplant:')

# Example usage:
# our_plays = ['Hodges, Lee','Kirk, Chris','Putnam, Andrew','Eckroat, Austin']  # Your list of player names
# url = "https://feeds.datagolf.com/preds/in-play?tour=pga&dead_heat=no&odds_format=percent&file_format=csv&key=e297e933c3ad47d71ec1626c299e"
# columns = ['player_name', 'top_10']

# st.dataframe(get_our_plays(our_plays, url, columns), hide_index=True,use_container_width=True)

# display dataframe
st.dataframe(main(), hide_index=True, height=3000 ,use_container_width=True, column_config={'Odds':None,
                                                                                            'Books':None})