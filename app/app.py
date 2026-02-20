import streamlit as st

st.logo("app/assets/logo.png")

main_page = st.Page(
    page = "main_page.py",
    title = "Home",
    default = True
)
news = st.Page(
    page = "market_overview.py",
    title = "Market Overview"
)
option_markets = st.Page(
    page = "option_modeling.py",
    title = "Strategy Modeling"
)
hedge = st.Page(
    page = "hedge.py",
    title = "Risk & Hedge Engine"
)
idea = st.Page(
    page = "idea.py",
    title = "Volatility Scanner"
)
pricing = st.Page(
    page = "pricing.py",
    title = "Options Pricing"
)


pg = st.navigation([main_page, news, option_markets, hedge, pricing, idea])
pg.run()