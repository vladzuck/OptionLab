import base64
import streamlit as st

def load_logo(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_base64 = load_logo("app/assets/logo.png")

st.markdown(f"""
<div style="text-align:center; margin-top:20px;">
    <img src="data:image/png;base64,{logo_base64}" width="200">
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="
    text-align: center;
    margin-top: 10px;
    font-size: 15px;
    opacity: 0.85;
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
">
    OptionLab is a lightweight dashboard for option pricing,
    volatility analysis, and basic risk management.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.wrapper {
  max-width: 700px;
  margin: 0 auto;
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 22px;
  margin-top: 30px;
}
.card {
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 20px;
  padding: 22px;
  background: rgba(255,255,255,0.04);
  transition: 0.2s ease;
}

.card:hover {
  border: 1px solid rgba(255,255,255,0.25);
  background: rgba(255,255,255,0.06);
}

.card-title {
  font-size: 26px;
  font-weight: 800;
  margin-bottom: 10px;
}

.card-desc {
  font-size: 14px;
  opacity: 0.75;
  line-height: 1.5;
  margin-bottom: 14px;
}

.badges {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.badge {
  padding: 5px 12px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.06);
  font-size: 12px;
}
</style>

<div class="wrapper">
 <div class="grid">

  <div class="card">
    <div class="card-title">Market Overview</div>
    <div class="card-desc">
      Quick context using major ETFs (SPY / QQQ / IWM / VXX / TLT / GLD).
    </div>
    <div class="badges">
      <div class="badge">Regime</div>
      <div class="badge">1D Move</div>
      <div class="badge">Volatility</div>
    </div>
  </div>

  <div class="card">
    <div class="card-title">Volatility Scanner</div>
    <div class="card-desc">
      Compare implied volatility across strikes and detect IV-rich regions.
    </div>
    <div class="badges">
      <div class="badge">IV Surface</div>
      <div class="badge">ATM Reference</div>
      <div class="badge">Anomalies</div>
    </div>
  </div>

  <div class="card">
    <div class="card-title">Option Pricing</div>
    <div class="card-desc">
      Price European (Black–Scholes) and American (CRR Binomial) options.
    </div>
    <div class="badges">
      <div class="badge">Black–Scholes</div>
      <div class="badge">CRR Tree</div>
      <div class="badge">Graphs</div>
    </div>
  </div>

  <div class="card">
    <div class="card-title">Risk & Hedge Engine</div>
    <div class="card-desc">
      Use Greeks and contract multipliers to estimate hedge quantities.
    </div>
    <div class="badges">
      <div class="badge">Delta</div>
      <div class="badge">Gamma</div>
      <div class="badge">Vega</div>
    </div>
  </div>

 </div>
</div>
""", unsafe_allow_html=True)