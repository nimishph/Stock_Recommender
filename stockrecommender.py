from __future__ import annotations
import streamlit as st
from SUGGESTIONS import getSuggestions

st.set_page_config(layout="wide")
st.session_state.suggestions = []


def showRecommendations(RISK: str, PERIOD: str, sector: list, dividend: bool):
    risk = RISK[0]
    period_dict = dict(zip(("1-2", "3-6", "7-10"), (0, 1, 2)))
    period = period_dict[PERIOD]
    suggestions = getSuggestions(
        risk=risk, period=period, pref_sectors=sector, dividend=dividend)
    suggestions["Large"] = suggestions.pop('L')
    suggestions["Medium"] = suggestions.pop('M')
    suggestions["Small"] = suggestions.pop('S')
    st.session_state.suggestions = suggestions


def render():
    st.write(
        """
  # Welcome to IIITN Stock Recommender 🙏
  *This is a stock recommender based on fundamental data of stocks listed on NSE*
  """
    )

    st.header("Risk Factor*")
    RISK = st.radio("Select risk level*", ("Low", "Medium",
                    "High"), index=0, on_change=None)
    st.header("Investment Tenure*")
    PERIOD = st.radio("Select investment tenure (in years)*",
                      ("1-2", "3-6", "7-10"), index=0, on_change=None)
    st.header("Preferred Sectors [Optional]")
    sectors = st.multiselect('Choose your Preferred Sectors (Atleast 4)', [
                             'Automobile', 'Banking', 'Chemical', 'Finance', 'IT', 'Metals', 'FMCG', 'Telecom', 'Pharma', 'Capital Goods', 'Textile', 'Power', 'Crude oil', 'Reality'])
    # st.write('You selected:', sectors)
    if 1 <= len(sectors) < 4:
        st.warning("Please choose atleast 4 sectors !!")
    st.header("Dividend Compulsory? (Y/N) [Optional]")
    div = st.checkbox("Yes")
    clicked = st.button("Get Recommendations!")
    if clicked:
        showRecommendations(RISK, PERIOD, sectors, div)

    for cap in st.session_state.suggestions:
        f"""#### {cap}Cap Companies"""
        st.table(st.session_state.suggestions[cap])


render()
