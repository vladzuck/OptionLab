import streamlit as st

st.set_page_config(layout="wide")
st.markdown(
    "<h1 style='text-align: center;'>Risk & Hedge Engine</h1>",
    unsafe_allow_html=True
)

greek_choice = st.selectbox(
    "Which risk do you want to hedge?",
    ["Delta", "Gamma", "Vega"]
)

contracts = st.number_input(
    "Your position size (contracts, negative = short)",
    value=1,
    step=1
)

mult = st.number_input(
    "Contract multiplier (US equity options usually do 100)",
    value=100,
    step=1
)


greek_per_share = st.number_input(
    f"{greek_choice} per share (e.g., delta 0.35)",
    value=0.0,
    step=0.001,
    format="%.3f"
)

target_greek = st.number_input(
    "Portfolio target exposure (0 means neutral)",
        value=0.0,
        step=0.001,
        format="%.3f"
)

greek_per_contract = greek_per_share*mult
pos_greek = greek_per_contract*contracts

st.write(f"{greek_choice} per contract = {greek_per_contract:.3f}")
st.write(f"Your total {greek_choice} exposure = {pos_greek:.3f}")

if greek_choice == "Delta":
    st.markdown(
        "<h3 style='text-align: center;'>Delta hedge using stock</h3>",
        unsafe_allow_html=True
    )
    if st.button("Compute hedge"):
        shares = target_greek - pos_greek
        st.success(f"Trade {shares:.3f} shares (negative = sell, positive = buy).")
        st.write(f"New delta ≈ {pos_greek + shares:.3f}")

elif greek_choice == "Gamma":
    st.markdown(
        "<h3 style='text-align: center;'>Gamma hedge using another option</h3>",
        unsafe_allow_html=True
    )

    hedge_gamma_per_share = st.number_input(
        "Hedge option gamma per share",
        value=0.0,
        step=0.001,
        format="%.3f"
    )
    hedge_gamma_per_contract = hedge_gamma_per_share * mult

    if st.button("Compute hedge"):
        if hedge_gamma_per_contract == 0:
            st.error("Hedge option gamma is 0. Choose another option.")
        else:
            hedge_contracts = (target_greek - pos_greek) / hedge_gamma_per_contract
            st.success(f"Trade {hedge_contracts:.3f} hedge option contracts (negative = sell, positive = buy, contract multiplier = {mult}).")
            st.write(f"New gamma ≈ {pos_greek + hedge_contracts*hedge_gamma_per_contract:.3f}")

elif greek_choice == "Vega":
    st.markdown(
        "<h3 style='text-align: center;'>Vega hedge using another option</h3>",
        unsafe_allow_html=True
    )

    hedge_g_per_share = st.number_input(
        "Hedge option vega per share",
        value=0.0,
        step=0.001
    )
    hedge_g_per_contract = hedge_g_per_share * mult

    if st.button("Compute hedge"):
        if hedge_g_per_contract == 0:
            st.error("Hedge option vega is 0. Choose another option.")
        else:
            hedge_contracts = (target_greek - pos_greek) / hedge_g_per_contract
            st.success(f"Trade {hedge_contracts:.3f} hedge option contracts (negative = sell, positive = buy, contract multiplier = {mult}).")
            st.write(f"New vega ≈ {pos_greek + hedge_contracts*hedge_g_per_contract:.3f}")