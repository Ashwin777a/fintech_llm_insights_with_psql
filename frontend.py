import streamlit as st
import requests

st.title("Daily Fintech Stock Insights")

API_URL = "http://localhost:8000/run-daily-pipeline"
data = requests.get(API_URL).json()

st.subheader(f"Stock Data ({data['date']})")
for stock in data['tickers']:
    st.write(f"**{stock['ticker']}**: Open={stock['open_price']}, Close={stock['close_price']}, Volume={stock['volume']}")

st.subheader("LLM Insights")
llm_text = data['llm_response'].replace("\\n", "\n")
st.markdown(llm_text)
