import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
st.set_page_config(layout="wide")
st.markdown(
    "<h1 style='text-align: center;'>Volatility Scanner</h1>",
    unsafe_allow_html=True
)

st.markdown("""
<style>
.card {
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 16px;
  padding: 14px;
  margin: 14px;
  background: rgba(255,255,255,0.04);
  height: 200px;
  display: flex;
  flex-direction: column;
}
.badge{
  display:inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.06);
  font-weight: 800;
  font-size: 14px;
  margin-top: 6px;
}
.scenario{
  margin-top: 5px;
  color: rgba(255,255,255,0.72);
  font-size: 14px;
  line-height: 1.55;
  max-width: 700px;
}
.small-label{
  color: rgba(255,255,255,0.6);
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-top: 14px;
}
</style>
""", unsafe_allow_html=True)

def change_step(x:float, small: float = 0.20):
    if x>small:
        return 1
    elif x<-small:
        return -1
    return 0

@st.cache_data(ttl=300)
def fetch_tile_yf(symbol: str, period="10d", interval="1d"):
    t = yf.Ticker(symbol)
    hist = t.history(period=period, interval=interval)
    if hist is None or hist.empty:
        return 0.0, 0.0, 0.0, np.array([0.0, 0.0])
    closes = hist["Close"].dropna()
    last = float(closes.iloc[-1])
    if len(closes) >= 2:
        prev = float(closes.iloc[-2])
    else:
        prev = last
    change = last - prev
    pct = (change / prev * 100.0) if prev else 0.0
    series = closes.to_numpy()[-80:]
    return last, change, pct, series

@st.cache_data(ttl=300)
def check_market_regime(
        pct_spy: float, pct_qqq: float, pct_iwm: float,
        pct_vxx: float, pct_tlt: float, pct_gld: float,
        eps: float = 0.20
):
    SPY = change_step(pct_spy, eps)
    QQQ = change_step(pct_qqq, eps)
    IWM = change_step(pct_iwm, eps)
    VXX = change_step(pct_vxx, eps)
    TLT = change_step(pct_tlt, eps)
    GLD = change_step(pct_gld, eps)

    equities_up = (SPY == +1 and QQQ==+1)
    equities_down = (SPY == -1 and QQQ==-1)

    volatility_up = (VXX == +1)
    volatility_down = (VXX == -1)

    participation_up = (IWM == +1)
    participation_down = (IWM == -1)

    safety_bid = (TLT == +1)
    macro_hedging = (GLD == +1)

    if pct_gld>2.0:
        regime = "Macro Hedge Rotation"
        scenario = "Capital is rotating into macro hedges. Strong gold inflows indicate rising demand for protection, outweighing short-term equity dispersion and signaling a defensive market posture."
        return regime, scenario
    if equities_up and volatility_down:
        regime = "Equity Expansion and Risk Acceptance"
        if participation_up and not safety_bid:
            scenario = "Broad-based risk appetite: equities are advancing with declining implied volatility and limited demand for defensive duration."
        elif participation_down:
            scenario = "Concentrated leadership: large caps are driving gains while small caps lag, suggesting narrower participation and a more fragile uptrend."
        else:
            scenario = "Risk-on with mixed cross-asset confirmation: trend remains constructive, but monitoring for volatility re-expansion is warranted."
        return regime, scenario

    if equities_up and volatility_up:
        regime = "Risk acceptance with Elevated Volatility"
        if safety_bid or macro_hedging:
            scenario = "Risk assets are higher, but hedging demand persists: volatility is rising alongside a defensive bid, indicating elevated uncertainty beneath the rally."
        else:
            scenario = "Uptrend with volatility expansion: price action is positive, but risk premia are rising, consistent with an unstable or news-driven advance."
        return regime, scenario

    if equities_down and volatility_up:
        regime = "Deleveraging Phase"
        if safety_bid and macro_hedging:
            scenario = "Systemic risk-off: equities are repricing lower as volatility spikes, accompanied by broad demand for safe-haven duration and macro hedges."
        elif safety_bid:
            scenario = "Classic flight-to-quality: equities are weakening while volatility rises and Treasuries rally, consistent with risk aversion and capital preservation."
        else:
            scenario = "Equity drawdown with limited duration support: volatility is rising without a meaningful Treasury bid, suggesting a rates/inflation-driven shock risk."
        return regime, scenario

    if equities_down and volatility_down:
        regime = "Controlled De-risking"
        if safety_bid:
            scenario = "Orderly de-risking: equities are drifting lower with contained volatility and supportive duration, consistent with a controlled rotation into safety."
        else:
            scenario = "Low-vol weakness: equities are softer without a volatility spike, indicating complacent selling pressure that can transition quickly if a catalyst emerges."
        return regime, scenario

    regime = "Mixed Signals"
    if (SPY != QQQ):
        scenario = "Divergent leadership: SPY and QQQ are sending conflicting signals, implying an unsettled tape and reduced directional conviction."
    elif VXX == 0:
        scenario = "Volatility is broadly unchanged: markets are awaiting information, and near-term regime classification remains low confidence."
    else:
        scenario = "Cross-asset signals are mixed: confirmation is limited across risk and defensive assets, indicating a transitional environment."
    return regime, scenario

last_spy, change_spy, pct_spy, series_spy = fetch_tile_yf("SPY")
last_qqq, change_qqq, pct_qqq, series_qqq = fetch_tile_yf("QQQ")
last_iwm, change_iwm, pct_iwm, series_iwm = fetch_tile_yf("IWM")
last_vxx, change_vxx, pct_vxx, series_vxx = fetch_tile_yf("VXX")
last_tlt, change_tlt, pct_tlt, series_tlt = fetch_tile_yf("TLT")
last_gld, change_gld, pct_gld, series_gld = fetch_tile_yf("GLD")
regime, scenario = check_market_regime(pct_spy,pct_qqq,pct_iwm,pct_vxx,pct_tlt,pct_gld)
st.markdown(f"""
        <div class="card">
          <div style="font-size:24px; font-weight:900; margin-bottom:6px;">Market Regime</div>
          <div class="badge">{regime}</div>

          <div class="small-label">Scenario</div>
          <div class="scenario">{scenario}</div>
        </div>
        """, unsafe_allow_html=True)
stock = st.selectbox("Choose stock-option chain",
    ["AAPL", "TSLA", "NVDA", "AMD", "META", "QQQ"])
t = yf.Ticker(stock)

try:
    S = float(t.fast_info["last_price"])
except:
    hist = t.history(period="5d")
    S = float(hist["Close"].iloc[-1])

expirations = t.options

exp = st.selectbox("Expiration", expirations)
chain = t.option_chain(exp)

calls = chain.calls
puts  = chain.puts

call_cols = ["lastPrice","bid","ask","volume","openInterest","impliedVolatility","inTheMoney"]
put_cols  = ["lastPrice","bid","ask","volume","openInterest","impliedVolatility","inTheMoney"]

calls_side = calls[["strike"] + call_cols].rename(columns={
    "lastPrice":"C_last",
    "bid":"C_bid",
    "ask":"C_ask",
    "volume":"C_vol",
    "openInterest":"C_OI",
    "impliedVolatility":"C_IV",
    "inTheMoney":"C_ITM",
})

puts_side = puts[["strike"] + put_cols].rename(columns={
    "lastPrice":"P_last",
    "bid":"P_bid",
    "ask":"P_ask",
    "volume":"P_vol",
    "openInterest":"P_OI",
    "impliedVolatility":"P_IV",
    "inTheMoney":"P_ITM",
})

grid = pd.merge(calls_side, puts_side, on="strike", how="outer").sort_values("strike")

grid = grid[[
    "C_last","C_bid","C_ask","C_vol","C_OI","C_IV","C_ITM",
    "strike",
    "P_last","P_bid","P_ask","P_vol","P_OI","P_IV","P_ITM"
]]

grid = grid[
    (grid["C_bid"].notna() & grid["C_ask"].notna()) &
    (grid["P_bid"].notna() & grid["P_ask"].notna())
]

st.subheader("Option Chains")

work = grid.copy()

work["AVG_IV"] = work[["C_IV","P_IV"]].mean(axis=1, skipna=True)
work["DIST"] = (work["strike"] - S).abs()

N_LOCAL = 10
valid = work[work["AVG_IV"].notna()]
local = valid.nsmallest(min(N_LOCAL, len(valid)), "DIST")

ref_iv = float(local["AVG_IV"].median()) if len(local) > 0 else np.nan

if pd.isna(ref_iv) or ref_iv <= 0:
    st.warning("Not enough valid IV data near ATM to compute reference IV.")
    st.stop()

work["IV_SCORE"] = (work["AVG_IV"] - ref_iv) / ref_iv
work["IV_MULTIPLE"] = work["AVG_IV"] / ref_iv

THRESH = 0.20
amount = 15
MULT_THRESH = 1.0 + THRESH

rich = work[
    work["IV_MULTIPLE"].notna() &
    (work["IV_MULTIPLE"] >= MULT_THRESH)
].copy()

rich = rich.sort_values("IV_MULTIPLE", ascending=False).head(amount)

st.dataframe(grid.fillna(""), use_container_width=True, height=600)

st.subheader("Insights: IV-rich strikes (relative to local ATM region)")
st.caption(
    "IV_MULTIPLE compares each strike’s implied volatility to a local ATM reference "
    "computed from nearby strikes of the same expiration. "
    "A value above 1.00 means volatility is priced higher than typical near-ATM options, "
    "while values below 1.00 indicate relatively cheaper volatility. "
    "This is a cross-sectional comparison, not a directional or arbitrage signal."
)

st.dataframe(
    rich[["strike", "AVG_IV", "IV_MULTIPLE", "IV_SCORE", "C_IV", "P_IV"]].fillna(""),
    use_container_width=True
)