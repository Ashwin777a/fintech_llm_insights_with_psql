import streamlit as st
import requests
from app import app as fastapi_app

st.title("Daily Fintech Stock Insights")

# --- Run FastAPI in background ---
def run_api():
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)
#API_URL = "http://localhost:8000/run-daily-pipeline"
data = requests.get(API_URL).json()

st.subheader(f"Stock Data ({data['date']})")
for stock in data['tickers']:
    st.write(f"**{stock['ticker']}**: Open={stock['open_price']}, Close={stock['close_price']}, Volume={stock['volume']}")

st.subheader("LLM Insights")
llm_text = data['llm_response'].replace("\\n", "\n")
st.markdown(llm_text)
