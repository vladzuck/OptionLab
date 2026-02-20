import streamlit as st
import numpy as np
import pandas as pd
import math
from matplotlib import pyplot as plt

st.set_page_config(layout="wide")
st.markdown(
    "<h1 style='text-align: center;'>Option Pricing</h1>",
    unsafe_allow_html=True
)

def norm_cdf(x:float):
    return 0.5 * (1.0 + math.erf(x/math.sqrt(2)))

def black_scholes_european(
    S:float, #spot
    K:float, #strike
    r: float, #risk-free rate
    sigma: float, #volatility
    T: float, #time to expiration
    option_type: str, #call/put
):
    if S<=0 or K<=0:
        raise ValueError("S and K must be positive")
    if T <= 0:
        if option_type.lower() == "call":
            return max(S - K, 0.0)
        if option_type.lower() == "put":
            return max(K - S, 0.0)
        raise ValueError("option_type must be 'call' or 'put'.")
    if sigma <= 0:
        forward = S * math.exp(r * T)
        if option_type.lower() == "call":
            return math.exp(-r * T) * max(forward - K, 0.0)
        if option_type.lower() == "put":
            return math.exp(-r * T) * max(K - forward, 0.0)
        raise ValueError("option_type must be 'call' or 'put'.")

    sqrtT = math.sqrt(T)
    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / (sigma * sqrtT)
    d2 = d1 - sigma * sqrtT

    Nd1 = norm_cdf(d1)
    Nd2 = norm_cdf(d2)
    discK = K * math.exp(-r * T)

    opt = option_type.lower()
    if opt == "call":
        # C = S*N(d1) - K*e^{-rT}*N(d2)
        return S * Nd1 - discK * Nd2
    if opt == "put":
        # P = K*e^{-rT}*N(-d2) - S*N(-d1)
        return discK * norm_cdf(-d2) - S * norm_cdf(-d1)

    raise ValueError("option_type must be 'call' or 'put'.")

def american_option(
    S:float, #spot
    K:float, #strike
    r:float, #risk-free rate
    sigma:float, #volatility
    T:float, #time to expiration
    option_type: str, #call/put
    steps:int #binomial steps
):
    if S <= 0 or K <= 0:
        raise ValueError("S and K must be positive.")

    if steps < 1:
        raise ValueError("steps must be >= 1")

    if T <= 0:
        if option_type.lower() == "call":
            return max(S - K, 0.0)
        elif option_type.lower() == "put":
            return max(K - S, 0.0)
        else:
            raise ValueError("option_type must be 'call' or 'put'.")

    dt = T / steps

    if sigma <= 0:
        forward = S * math.exp(r * T)
        if option_type.lower() == "call":
            return math.exp(-r * T) * max(forward - K, 0.0)
        elif option_type.lower() == "put":
            return math.exp(-r * T) * max(K - forward, 0.0)
        else:
            raise ValueError("option_type must be 'call' or 'put'.")

    u = math.exp(sigma * math.sqrt(dt))
    d = 1.0 / u

    disc = math.exp(-r * dt)
    growth = math.exp(r * dt)
    p = (growth - d) / (u - d)


    if p < 0.0 or p > 1.0:
        raise ValueError("Risk-neutral probability not in [0,1].")

    opt = option_type.lower()
    if opt not in ("call", "put"):
        raise ValueError("option_type must be 'call' or 'put'.")

    stock_prices = [S * (u ** i) * (d ** (steps - i)) for i in range(steps + 1)]

    if opt == "call":
        values = [max(s - K, 0.0) for s in stock_prices]
    else:
        values = [max(K - s, 0.0) for s in stock_prices]

    for t in range(steps - 1, -1, -1):
        new_values = []
        for i in range(t + 1):
            cont = disc * (p * values[i + 1] + (1.0 - p) * values[i])
            s_node = S * (u ** i) * (d ** (t - i))
            if opt == "call":
                ex = max(s_node - K, 0.0)
            else:
                ex = max(K - s_node, 0.0)
            new_values.append(max(cont, ex))
        values = new_values

    return values[0]





col_eu, col_am = st.columns(2)

with col_eu:
    st.subheader("European Option (Black–Scholes)")

    eu_type = st.selectbox("Type", ["Put", "Call"], key="eu_type")

    S_eu = st.number_input("Spot Price (S)", value=100.0, key="S_eu")
    K_eu = st.number_input("Strike (K)", value=120.0, key="K_eu")
    r_eu = st.number_input("Risk-free rate (r, decimal)", value=0.05, key="r_eu")
    sigma_eu = st.number_input("Volatility (σ, decimal)", value=0.2, key="sigma_eu")
    T_eu = st.number_input("Time to Expiration (years)", value=1.0, key="T_eu")

    price_call_eu = black_scholes_european(S_eu,K_eu,r_eu,sigma_eu,T_eu,"call")
    price_put_eu = black_scholes_european(S_eu,K_eu,r_eu,sigma_eu,T_eu,"put")
    if eu_type.lower() == "call":
        st.markdown(
            f"<h5 style='text-align: center;'>Option Price (Call): {price_call_eu:.3f}</h5>",
            unsafe_allow_html=True
        )
    elif eu_type.lower() == "put":
        st.markdown(
            f"<h5 style='text-align: center;'>Option Price (Put): {price_put_eu:.3f}</h5>",
            unsafe_allow_html=True
        )

with col_am:
    st.subheader("American Option (Binomial Tree)")

    am_type = st.selectbox("Type", ["Put", "Call"], key="am_type")

    S_am = st.number_input("Spot Price (S)", value=100.0, key="S_am")
    K_am = st.number_input("Strike (K)", value=120.0, key="K_am")
    r_am = st.number_input("Risk-free rate (r, decimal)", value=0.05, key="r_am")
    sigma_am = st.number_input("Volatility (σ, decimal)", value=0.2, key="sigma_am")
    T_am = st.number_input("Time to Expiration (years)", value=1.0, key="T_am")

    steps = st.number_input("Binomial Steps", value=300, min_value=10, key="steps")

    price_call_am = american_option(S_am, K_am, r_am, sigma_am, T_am, "call", steps)
    price_put_am = american_option(S_am, K_am, r_am, sigma_am, T_am, "put", steps)
    if am_type.lower() == "call":
        st.markdown(
            f"<h5 style='text-align: center;'>Option Price (Call): {price_call_am:.3f}</h5>",
            unsafe_allow_html=True
        )
    elif am_type.lower() == "put":
        st.markdown(
            f"<h5 style='text-align: center;'>Option Price (Put): {price_put_am:.3f}</h5>",
            unsafe_allow_html=True
        )


S_min = 0.5 * min(K_eu, K_am)
S_max = 1.5 * max(K_eu, K_am)

spots = np.linspace(S_min, S_max, 80)
eu_prices = [
    black_scholes_european(
        s,
        K_eu,
        r_eu,
        sigma_eu,
        T_eu,
        eu_type.lower()
    )
    for s in spots
]

am_prices = [
    american_option(
        s,
        K_am,
        r_am,
        sigma_am,
        T_am,
        am_type.lower(),
        steps=int(steps)
    )
    for s in spots
]

st.markdown(
    "<div style='height:50px;'></div>",
    unsafe_allow_html=True
)
st.markdown(
            f"<h3 style='text-align: center;'>European vs American Option Pricing</h3>",
            unsafe_allow_html=True
)
fig, ax = plt.subplots(figsize=(5, 3))
fig.patch.set_facecolor("black")
ax.set_facecolor("black")

ax.plot(spots, eu_prices, label=f"European {eu_type}", color="red")
ax.plot(spots, am_prices, label=f"American {am_type}", color="white")

ax.set_xlabel("Stock Price S", color="white")
ax.set_ylabel("Option Price", color="white")
ax.grid(color="gray", linestyle="--", alpha=0.3)
ax.tick_params(colors="white")

legend = ax.legend(framealpha=0)
for text in legend.get_texts():
    text.set_color("white")
st.pyplot(fig)