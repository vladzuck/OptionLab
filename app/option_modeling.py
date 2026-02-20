import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.markdown(
    "<h1 style='text-align: center;'>Strategy Modeling</h1>",
    unsafe_allow_html=True
)
strategy = st.selectbox(
    "Choose strategy",
    ["Long Call", "Long Put", "Long Butterfly", "Short Butterfly"]
)

if strategy == "Long Call":
    S0 = st.number_input("Current underlying price (S₀)", value=100.0, step=1.0)
    K = st.number_input("Strike (K)", value=S0 + 5, step=1.0)
    premium = st.number_input("Premium paid (p)", value=5.0, min_value=0.0, step=0.5)
    iv = st.number_input("Implied vol (annual, %)", value=20.0, min_value=0.0, step=1.0)
    dte = st.number_input("Days to expiry", value=30, min_value=1)
    k = st.slider("k (number of sigmas)", 1.0, 3.0, 2.0)
    sigma = iv / 100.0
    T = dte / 365.0
    band_low = S0 * np.exp(-k * sigma * np.sqrt(T))
    band_high = S0 * np.exp(k * sigma * np.sqrt(T))
    n_points = 5000
    S = np.linspace(band_low, band_high, n_points)
    profit = np.maximum(S - K, 0.0) - premium
    breakeven = K + premium

elif strategy == "Long Put":
    S0 = st.number_input("Current underlying price (S₀)", value=100.0, step=1.0)
    K = st.number_input("Strike (K)", value=S0 + 5, step=1.0)
    premium = st.number_input("Premium paid (p)", value=5.0, min_value=0.0, step=0.5)
    iv = st.number_input("Implied vol (annual, %)", value=20.0, min_value=0.0, step=1.0)
    dte = st.number_input("Days to expiry", value=30, min_value=1)
    k = st.slider("k (number of sigmas)", 1.0, 3.0, 2.0)
    sigma = iv / 100.0
    T = dte / 365.0
    band_low = S0 * np.exp(-k * sigma * np.sqrt(T))
    band_high = S0 * np.exp(k * sigma * np.sqrt(T))
    n_points = 5000
    S = np.linspace(band_low, band_high, n_points)
    profit = np.maximum(K - S, 0.0) - premium
    breakeven = K - premium

elif strategy == "Long Butterfly":
    S0 = st.number_input("Current underlying price (S₀)", value=100.0, step=1.0)
    K2 = st.number_input("Center strike (K2)", value=float(round(S0)), step=1.0)
    w = st.number_input("Wing width", value=10.0, step=1.0, min_value=1.0)
    K1 = K2 - w
    K3 = K2 + w
    premium1 = st.number_input(f"Premium Call for ${K1} option", value=12.0, step=0.5)
    premium2 = st.number_input(f"Premium Call for ${K2} option", value=6.0, step=0.5)
    premium3 = st.number_input(f"Premium Call for ${K3} option", value=2.0, step=0.5)
    premium = premium1 - 2 * premium2 + premium3
    iv = st.number_input("Implied vol (annual, %)", value=20.0, min_value=0.0, step=1.0)
    dte = st.number_input("Days to expiry", value=30, min_value=1)
    k = st.slider("k (number of sigmas)", 1.0, 3.0, 2.0)
    sigma = iv / 100.0
    T = dte / 365.0
    band_low = S0 * np.exp(-k * sigma * np.sqrt(T))
    band_high = S0 * np.exp(k * sigma * np.sqrt(T))
    n_points = 5000
    S = np.linspace(band_low, band_high, n_points)
    payoff_K1 = np.maximum(S - K1, 0.0)
    payoff_K2 = np.maximum(S - K2, 0.0)
    payoff_K3 = np.maximum(S - K3, 0.0)
    profit = payoff_K1 - 2 * payoff_K2 + payoff_K3 - premium
    breakeven_low = K1+premium
    breakeven_high = K3-premium

elif strategy == "Short Butterfly":
    S0 = st.number_input("Current underlying price (S₀)", value=100.0, step=1.0)
    K2 = st.number_input("Center strike (K2)", value=float(round(S0)), step=1.0)
    w = st.number_input("Wing width", value=10.0, step=1.0, min_value=1.0)
    K1 = K2 - w
    K3 = K2 + w
    premium1 = st.number_input(f"Premium Call for ${K1} option", value=8.0, step=0.5)
    premium2 = st.number_input(f"Premium Call for ${K2} option", value=6.0, step=0.5)
    premium3 = st.number_input(f"Premium Call for ${K3} option", value=2.0, step=0.5)
    premium = -premium1 + 2 * premium2 - premium3
    iv = st.number_input("Implied vol (annual, %)", value=20.0, min_value=0.0, step=1.0)
    dte = st.number_input("Days to expiry", value=30, min_value=1)
    k = st.slider("k (number of sigmas)", 1.0, 3.0, 2.0)
    sigma = iv / 100.0
    T = dte / 365.0
    band_low = S0 * np.exp(-k * sigma * np.sqrt(T))
    band_high = S0 * np.exp(k * sigma * np.sqrt(T))
    n_points = 5000
    S = np.linspace(band_low, band_high, n_points)
    payoff_K1 = np.maximum(S-K1, 0.0)
    payoff_K2 = np.maximum(S-K2, 0.0)
    payoff_K3 = np.maximum(S-K3, 0.0)
    profit = (-payoff_K1 + 2 * payoff_K2 - payoff_K3) + premium
    breakeven_low = K1 + premium
    breakeven_high = K3 - premium

max_profit = float(np.max(profit))
max_loss = float(np.min(profit))

plot_col, info_col = st.columns([2, 1])

if strategy == "Long Call" or strategy == "Long Put":
    with plot_col:
        fig, ax = plt.subplots(figsize=(6, 4))

        ax.plot(S, profit)
        ax.axhline(0)
        ax.axvline(K, linestyle="--")
        ax.axvline(breakeven, linestyle="--")
        ax.axvline(band_low, linestyle="--")
        ax.axvline(band_high, linestyle="--")
        ax.axvspan(band_low, band_high, alpha=0.12)

        ax.set_xlabel("Underlying price at expiry (S_T)")
        ax.set_ylabel("Profit")
        ax.set_title(strategy)

        st.pyplot(fig, use_container_width=True)

    with info_col:
        st.subheader("Key metrics")
        st.write(f"Breakeven: {breakeven:.2f}")
        st.write(f"Max profit : {max_profit:.2f}")
        st.write(f"Max loss : {max_loss:.2f}")
        st.write(f"Underlying min price: {band_low:.2f}")
        st.latex(r"S_{\min} = S_0 e^{-k\sigma\sqrt{T}}")
        st.write(f"Underlying max price: {band_high:.2f}")
        st.latex(r"S_{\max} = S_0 e^{k\sigma\sqrt{T}}")
        if max_loss<0:
            rr = max_profit/abs(max_loss)
        else:
            rr = float("inf")
        st.write("Risk-Reward")
        st.latex(r"(\frac{MaxProfit}{MaxLoss}):" + f"{rr:.2f}")

elif strategy == "Long Butterfly" or strategy == "Short Butterfly":
    with plot_col:
        fig, ax = plt.subplots(figsize=(6, 4))

        ax.plot(S, profit)
        ax.axhline(0)

        ax.axvline(K1, linestyle=":", label="Strike K1")
        ax.axvline(K2, linestyle=":", label="Strike K2")
        ax.axvline(K3, linestyle=":", label="Strike K3")

        ax.axvline(breakeven_low, linestyle="--", label="Lower BE", color = "red")
        ax.axvline(breakeven_high, linestyle="--", label="Upper BE", color = "red")

        ax.set_xlabel("Underlying price at expiry $S_T$")
        ax.set_ylabel("Profit")
        ax.set_title(strategy)
        ax.legend()

        st.pyplot(fig, use_container_width=True)

    with info_col:
        st.subheader("Key metrics")
        st.write(f"Breakeven: {breakeven_low:.2f}, {breakeven_high:.2f}")
        st.write(f"Max profit : {max_profit:.2f}")
        if strategy == "Long Butterfly":
            st.write(f"Max loss : {-premium:.2f}")
        elif strategy == "Short Butterfly":
            st.write(f"Max loss : {max_loss:.2f}")
        st.write(f"Underlying min price: {band_low:.2f}")
        st.latex(r"S_{\min} = S_0 e^{-k\sigma\sqrt{T}}")
        st.write(f"Underlying max price: {band_high:.2f}")
        st.latex(r"S_{\max} = S_0 e^{k\sigma\sqrt{T}}")
        st.write(f"Risk-Reward")
        if strategy == "Long Butterfly":
            st.latex(r"(\frac{MaxProfit}{MaxLoss}):" + f"{max_profit/premium:.2f}")
        elif strategy == "Short Butterfly":
            st.latex(r"(\frac{MaxProfit}{MaxLoss}):" + f"{max_profit/abs(max_loss):.2f}")





