# OptionLab

OptionLab is a lightweight options analytics dashboard built with Streamlit.
It combines option pricing models, implied volatility analysis, market regime context, and basic risk management tools in a single interface.

---

## Features

### Market Overview
- Cross-asset regime context (SPY / QQQ / IWM / VXX / TLT / GLD)
- Daily move tracking
- Risk-on / risk-off interpretation logic

### Volatility Scanner
- Option chain viewer
- Cross-sectional implied volatility comparison
- Local ATM reference IV calculation
- Detection of relatively IV-rich strikes

### Option Pricing
- European options via Black–Scholes model
- American options via CRR binomial tree
- Price vs stock price visualization
- Model comparison

### Hedging Advisor
- Delta-neutral sizing
- Gamma and vega exposure estimation
- Contract multiplier support

---

## Tech Stack

- Python
- Streamlit
- NumPy
- Pandas
- yfinance
- Matplotlib
- Finnhub API (market/news data)

---

## Installation (Run Locally)

Clone the repository:

bash
git clone https://github.com/vladzuck/OptionLab.git
cd OptionLab

---

#API

OptionLab – API Configuration Guide

Some modules of OptionLab require a Finnhub API key in order to retrieve market news and external data.

Follow the steps below to configure the API correctly.
	1.	Create a Finnhub Account
Go to: https://finnhub.io/
Sign up for a free account and generate your personal API key.
	2.	Create Streamlit Secrets Folder
In the root directory of the OptionLab project (same folder as app.py), create a folder named:

.streamlit
	3.	Create Secrets File
Inside the .streamlit folder, create a file named:

secrets.toml
	4.	Add Your API Key
Open secrets.toml and add the following line:

FINNHUB_API_KEY = “your_api_key_here”

Replace “your_api_key_here” with your actual API key.
	5.	Restart the Application
After saving the file, restart the Streamlit app:

streamlit run app.py
	6.	How the Key Is Used
Inside the code, the API key is accessed securely via:

st.secrets[“FINNHUB_API_KEY”]
	7.	Important Security Note
Do NOT upload the secrets.toml file to GitHub.
Make sure the following line exists in your .gitignore file:

.streamlit/secrets.toml

This ensures your API key remains private.
