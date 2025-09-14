from fastapi import FastAPI
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import date
import os
import uvicorn
from dotenv import load_dotenv
from db import create_tables  # ✅ Import DB setup

from llm import generate_llm_insights

app = FastAPI()
load_dotenv()
create_tables()  # Ensure tables are created on startup
# --- Environment ---
DB_URL = os.getenv("DB_URL")
engine = create_engine(DB_URL)

TICKERS = ["SOFI", "PYPL", "HOOD"]

# --- ETL Functions ---
def fetch_stock_data(tickers):
    df_list = []
    data = yf.download(tickers, period="1d")  # multi-index DataFrame

    for t in tickers:
        row = {
            "date": data.index[-1].date(),
            "ticker": t,
            "open_price": float(data['Open'][t].iloc[-1]),
            "high_price": float(data['High'][t].iloc[-1]),
            "low_price": float(data['Low'][t].iloc[-1]),
            "close_price": float(data['Close'][t].iloc[-1]),
            "volume": int(data['Volume'][t].iloc[-1])
        }
        df_list.append(row)

    return pd.DataFrame(df_list)


def insert_stock_data(df):
    with engine.begin() as conn:
        for _, row in df.iterrows():
            conn.execute(text("""
                INSERT INTO daily_stock_prices (date, ticker, open_price, high_price, low_price, close_price, volume)
                VALUES (:date, :ticker, :open_price, :high_price, :low_price, :close_price, :volume)
                ON CONFLICT (date, ticker) DO NOTHING;
            """), row.to_dict())


def insert_insights(prompt, response, df):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO daily_stock_insights (date, ticker, prompt, response)
            VALUES (:date, :ticker, :prompt, :response)
        """), {
            "date": df['date'].iloc[0],
            "ticker": None,  # global insight for all tickers
            "prompt": str(prompt),
            "response": str(response)
        })


# --- API Endpoint ---
@app.get("/run-daily-pipeline")
def run_daily_pipeline():
    # 1. Fetch stock data
    df = fetch_stock_data(TICKERS)

    # 2. Insert into DB
    insert_stock_data(df)

    # 3. Generate LLM insights
    prompt, response = generate_llm_insights(df)

    # 4. Insert insights into DB
    insert_insights(prompt, response, df)

    # 5. Return final results in API response
    return {
        "status": "success",
        "date": str(df['date'].iloc[0]),
        "tickers": df.to_dict(orient="records"),
        "llm_prompt": prompt,
        "llm_response": response
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
