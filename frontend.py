import threading
import uvicorn
from app import app as fastapi_app
import streamlit as st
import requests

# --- Run FastAPI in background ---
def run_api():
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)

threading.Thread(target=run_api, daemon=True).start()

# --- Streamlit frontend ---
st.title("Daily Fintech Stock Insights")

API_URL = "http://localhost:8000/run-daily-pipeline"  # calls local FastAPI
data = requests.get(API_URL).json()

st.subheader(f"Stock Data ({data['date']})")
for stock in data['tickers']:
    st.write(f"**{stock['ticker']}**: Open={stock['open_price']}, Close={stock['close_price']}, Volume={stock['volume']}")

st.subheader("LLM Insights")
llm_text = data['llm_response'].replace("\\n", "\n")
st.markdown(llm_text)
