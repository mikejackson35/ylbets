import pandas as pd
import plotly.express as px
import numpy as np
import streamlit as st
import altair as alt

from streamlit_extras.stoggle import stoggle
from utils import get_ev_table, plus_prefix

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
    df.columns = ['Player','Odds','Books','EV','Target']

    # add styling  ("+" prefixes and color)
    df['Odds'] = df['Odds'].apply(plus_prefix)
    df['Target'] = df['Target'].apply(plus_prefix)

    styled_df = df.style.background_gradient(
        cmap="cividis", subset=['EV'], vmin=-.2#, gmap= -df['EV']
        ).format(precision=2)

    return styled_df


## USER INTERFACE

# details dropdown
stoggle('info',
        """<br>
        TARGET = the line you want, or better, in order to be considered a value by datagolf.com<br><br>
        EV = use this column to sort when looking for value. On average, the most yellow players are the undervalued most across all sportsbooks. It's likely that yours is similar.
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

# display dataframe
st.dataframe(main(), hide_index=True, height=3000 ,use_container_width=True, column_config={'Odds':None,
                                                                                            'Books':None})