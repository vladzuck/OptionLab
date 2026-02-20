from bs4 import BeautifulSoup
import streamlit as st
import finnhub
import pandas as pd
import html
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

st.set_page_config(layout="wide")

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

.row {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: 12px;
}

.tag {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 100px;
  border: 1px solid rgba(255,255,255,0.2);
  font-size: 12px;
  margin-bottom: 6px;
}

.title {
  font-weight: 800;
  font-size: 16px;
  line-height: 1.2;
}

.muted {
  font-size: 12px;
  color: rgba(255,255,255,0.6);
  margin-top: 6px;
}

.summary {
  margin-top: 10px;
  font-size: 13px;
  color: rgba(255,255,255,0.75);

  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.title a {
  text-decoration: none;
  color: rgba(255,255,255,0.92);
}
.title a:hover {
  text-decoration: underline;
}
.tile {
  background: #141a22;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 14px 14px 10px 14px;
  height: 150px;
}
.tile-title {
  font-size: 18px;
  font-weight: 700;
  color: #9ad0ff;
  margin-bottom: 4px;
}
.tile-price {
  font-size: 28px;
  font-weight: 800;
  color: #ffffff;
  line-height: 1.0;
  margin-bottom: 6px;
}
.tile-change {
  font-size: 18px;
  font-weight: 700;
  margin-top: 6px;
}
.pos {
  color: #22c55e;
}
.neg {
  color: #ef4444;
}
.neutral {
  color: #9ca3af;
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
.metrics-grid{
  display:grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px 40px;
  margin-top: 6px;
}
.metric{
  display:flex;
  justify-content: space-between;
  font-size: 16px;
  font-weight: 650;
}

</style>
""", unsafe_allow_html=True)

client = finnhub.Client(api_key=st.secrets["FINNHUB_API_KEY"])


#functions for news
def html_to_text(s: str) -> str:
    if not s:
        return ""
    s = html.unescape(s)              # turns &lt;div&gt; into <div>
    soup = BeautifulSoup(s, "html.parser")
    return soup.get_text(" ", strip=True)

@st.cache_data(ttl=300)
def get_news(category: str, limit: int) -> list[dict]:
    items = client.general_news(category, min_id=0) or []
    return items[:limit]

#functions for markets
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

def sparkline(series: np.ndarray, change):
    line_color = "#22c55e" if change >= 0 else "#ef4444"
    fig, ax = plt.subplots(figsize=(3.2, 0.85))
    ax.plot(series, linewidth=2.0, color=line_color)
    ax.fill_between(np.arange(len(series)), series, np.min(series), alpha=0.18, color = line_color)
    ax.set_axis_off()
    fig.tight_layout(pad=0)
    fig.patch.set_facecolor("#0E1117")
    return fig

def render_tile(title: str, symbol: str):
    last, change, pct, series = fetch_tile_yf(symbol)
    if change > 0:
        cls, sign = "pos", "+"
    elif change < 0:
        cls, sign = "neg", ""
    else:
        cls, sign = "neutral", ""
    with st.container(border=True):
        left, right = st.columns([2, 3], vertical_alignment="center")
        with left:
            st.markdown(f"**{title}**")
            st.markdown(
                f"<span style='font-size:34px; font-weight:800'>{last:,.2f}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<span class='{cls}' style='font-size:18px; font-weight:700'>"
                f"{sign}{change:,.2f} ({sign}{pct:.2f}%)</span>",
                unsafe_allow_html=True,
            )
        with right:
            fig = sparkline(series, change)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

def change_step(x:float, small: float = 0.20):
    if x>small:
        return 1
    elif x<-small:
        return -1
    return 0

def text_info_color(pct_change):
    if pct_change > 0:
        color = "#22c55e"
    elif pct_change < 0:
        color = "#ef4444"
    else:
        color = "#0E1117"
    return color

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


general_news = get_news("general", 2)
crypto_news  = get_news("crypto", 2)
merger_news = get_news("merger", 2)

general1 = general_news[0]
general2 = general_news[1]
merger1 = merger_news[0]
crypto1  = crypto_news[0]


st.markdown(
    "<h1 style='text-align: center;'>Market Overview</h1>",
    unsafe_allow_html=True
)
row1 = st.columns(3)
row2 = st.columns(3)
market_regime = st.container()
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

tiles = [
    ("S&P 500 (SPY)", "SPY"),
    ("Nasdaq 100 (QQQ)", "QQQ"),
    ("Russell 2000 (IWM)", "IWM"),
    ("Volatility (VXX)", "VXX"),
    ("US Bonds (TLT)", "TLT"),
    ("Gold (GLD)", "GLD"),
]

for i, (title, sym) in enumerate(tiles[:3]):
    with row1[i]:
        render_tile(title, sym)

for i, (title, sym) in enumerate(tiles[3:]):
    with row2[i]:
        render_tile(title, sym)


with market_regime:
    left, right = st.columns([1, 1])
    with left:
        last_spy, change_spy, pct_spy, series_spy = fetch_tile_yf("SPY")
        last_qqq, change_qqq, pct_qqq, series_qqq = fetch_tile_yf("QQQ")
        last_iwm, change_iwm, pct_iwm, series_iwm = fetch_tile_yf("IWM")
        last_vxx, change_vxx, pct_vxx, series_vxx = fetch_tile_yf("VXX")
        last_tlt, change_tlt, pct_tlt, series_tlt = fetch_tile_yf("TLT")
        last_gld, change_gld, pct_gld, series_gld = fetch_tile_yf("GLD")
        regime, scenario = check_market_regime(pct_spy,pct_qqq,pct_iwm,pct_vxx,pct_tlt,pct_gld)
        color_spy = text_info_color(pct_spy)
        color_qqq = text_info_color(pct_qqq)
        color_iwm = text_info_color(pct_iwm)
        color_vxx = text_info_color(pct_vxx)
        color_tlt = text_info_color(pct_tlt)
        color_gld = text_info_color(pct_gld)
        st.markdown(f"""
        <div class="card">
            <div class="metric-grid">
              <div class="metric">SPY: <span style="color: {color_spy}">{pct_spy:.2f}%</span></div>
              <div class="metric">QQQ: <span style="color: {color_qqq}">{pct_qqq:.2f}%</span></div>
              <div class="metric">IWM: <span style="color: {color_iwm}">{pct_iwm:.2f}%</span></div>
            </div>
            <div class="metric-grid">
              <div class="metric">VXX: <span style="color: {color_vxx}">{pct_vxx:.2f}%</span></div>
              <div class="metric">TLT: <span style="color: {color_tlt}">{pct_tlt:.2f}%</span></div>
              <div class="metric">GLD: <span style="color: {color_gld}">{pct_gld:.2f}%</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with right:
        st.markdown(f"""
        <div class="card">
          <div style="font-size:24px; font-weight:900; margin-bottom:6px;">Market Regime</div>
          <div class="badge">{regime}</div>

          <div class="small-label">Scenario</div>
          <div class="scenario">{scenario}</div>
        </div>
        """, unsafe_allow_html=True)


with col1:
    clean_summary = html.escape(html_to_text(general1.get("summary", "")))
    safe_title = html.escape(general1["headline"])
    safe_url = html.escape(general1["url"], quote=True)

    st.markdown("""
    <div class="card">
      <div class="row">
        <div>
          <div class="tag">GENERAL</div>
          <div class="tag">""" + html.escape(general1["source"].upper()) + """</div>
        </div>
        <div>
          <div class="title">
            <a href=\"""" + safe_url + """\" target="_blank">
            """ + safe_title + """
            </a>
          </div>
          <div class="muted">""" +
            pd.to_datetime(general1["datetime"], unit="s").strftime("%Y-%m-%d %H:%M")
          + """</div>
        </div>
      </div>

      <div class="summary">""" + clean_summary + """</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    clean_summary = html.escape(html_to_text(merger1.get("summary", "")))
    safe_title = html.escape(merger1["headline"])
    safe_url = html.escape(merger1["url"], quote=True)

    st.markdown("""
    <div class="card">
      <div class="row">
        <div>
          <div class="tag">MERGER</div>
          <div class="tag">""" + html.escape(merger1["source"].upper()) + """</div>
        </div>
        <div>
          <div class="title">
            <a href=\"""" + safe_url + """\" target="_blank">
            """ + safe_title + """
            </a>
          </div>
          <div class="muted">""" +
            pd.to_datetime(merger1["datetime"], unit="s").strftime("%Y-%m-%d %H:%M")
          + """</div>
        </div>
      </div>

      <div class="summary">""" + clean_summary + """</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    clean_summary = html.escape(html_to_text(general2.get("summary", "")))
    safe_title = html.escape(general2["headline"])
    safe_url = html.escape(general2["url"], quote=True)

    st.markdown("""
    <div class="card">
      <div class="row">
        <div>
          <div class="tag">GENERAL</div>
          <div class="tag">""" + html.escape(general2["source"].upper()) + """</div>
        </div>
        <div>
          <div class="title">
            <a href=\"""" + safe_url + """\" target="_blank">
            """ + safe_title + """
            </a>
          </div>
          <div class="muted">""" +
            pd.to_datetime(general2["datetime"], unit="s").strftime("%Y-%m-%d %H:%M")
          + """</div>
        </div>
      </div>

      <div class="summary">""" + clean_summary + """</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    clean_summary = html.escape(html_to_text(crypto1.get("summary", "")))
    safe_title = html.escape(crypto1["headline"])
    safe_url = html.escape(crypto1["url"], quote=True)

    st.markdown("""
    <div class="card">
      <div class="row">
        <div>
          <div class="tag">CRYPTO</div>
          <div class="tag">""" + html.escape(crypto1["source"].upper()) + """</div>
        </div>
        <div>
          <div class="title">
            <a href=\"""" + safe_url + """\" target="_blank">
            """ + safe_title + """
            </a>
          </div>
          <div class="muted">""" +
            pd.to_datetime(crypto1["datetime"], unit="s").strftime("%Y-%m-%d %H:%M")
          + """</div>
        </div>
      </div>

      <div class="summary">""" + clean_summary + """</div>
    </div>
    """, unsafe_allow_html=True)