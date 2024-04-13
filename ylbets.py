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
"#"

def main():
    """
    INPUT:  users choice of betting market from st.selectbox
    OUTPUT: styled DataFrame with columns 'Player', 'Odds', 'EV', & 'Agg'    
    """
    
    # takes user selection and outputs un-styled dataframe with odds and ev's
    df = get_ev_table(market_type)

    # fix column headers
    df.columns = ['Player','Odds','EV','Agg']

    # add styling  (ie. plus prefixes in front of integers and color 'ev' column)
    df['Odds'] = df['Odds'].apply(plus_prefix)
    df['Agg'] = df['Agg'].apply(plus_prefix)

    styled_df = df.style.background_gradient(
        cmap="cividis", subset=['EV'], vmin=-.2#, gmap= -df['EV']
        ).format(precision=2)

    return styled_df

## USER INTERFACE
# details dropdown
stoggle('click for details',
        """<br>
        ODDS<br> player odds based on the datagolf.com<br> model<br><br>
        AGG<br> avg player odds across all sportsbooks<br><br>
        EV<br> expected net profit on a 1-unit bet placed<br> many many times.<br><br>=================================<br>GENERAL EV TARGETS<br> Win over .15<br> Top 5 over.10<br> Top 10 over .10<br> Top 20 over .05<br>
        =================================
        """)
        # EV Example - Consider the classic betting on coin flips (which is not so different from betting on golf). The probability of flipping Heads or Tails is equal to 50%. Suppose a bookmaker offers +100 American odds. This implies a probability of 1/2 or 50%. Given that the 'implied' probability is equal to the 'true' probability of Heads, the Expected Value from betting on Heads is zero. If a bookmaker offered odds of -110, the expected value would be negative (-5%, or -0.05 per unit bet). In reverse, if a bad bookmaker offered odds of +110, the expected value would be positive (+5%), and in theory, a bet worth taking.
        # """)

# 'ylbets title'
title_placeholder = st.empty()

# user selectbox
market_type = st.selectbox('Choose Market',
                           ('win','top_5','top_10','top_20'))

title_placeholder.header('ylbets :eggplant:')
st.dataframe(main(), hide_index=True, height=3000 ,use_container_width=True)#, column_config={'Agg Line':None})