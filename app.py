from fastapi import FastAPI
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
from datetime import date
import os
import uvicorn
from dotenv import load_dotenv

from llm import generate_llm_insights
app = FastAPI()
load_dotenv()
# --- Environment ---
DB_URL = os.getenv("DB_URL")

TICKERS=["SOFI","PYPL","HOOD"]

engine = create_engine(DB_URL)

#ETL Functions
def fetch_stock_data(tickers):
    df_list = []
    data = yf.download(tickers, period="1d")  # multi-index DataFrame

    for t in tickers:
        # Extract scalar values from the last row
        open_price = data['Open'][t].iloc[-1]
        high_price = data['High'][t].iloc[-1]
        low_price = data['Low'][t].iloc[-1]
        close_price = data['Close'][t].iloc[-1]
        volume = data['Volume'][t].iloc[-1]
        date_val = data.index[-1].date()

        df_list.append({
            "date": date_val,
            "ticker": t,
            "open_price": open_price,
            "high_price": high_price,
            "low_price": low_price,
            "close_price": close_price,
            "volume": volume
        })

    return pd.DataFrame(df_list)

# --- Insert into PostgreSQL ---
def insert_stock_data(df):
    # Ensure all columns are scalar types
    df = df.astype({
        "open_price": float,
        "high_price": float,
        "low_price": float,
        "close_price": float,
        "volume": int
    })
    df.to_sql("daily_stock_prices", engine, if_exists="append", index=False)
#---  Insert LLM insights into PostgreSQL ---`
def insert_insights(prompt, response, df):
    rec_df = pd.DataFrame([{
        "date": df['date'].iloc[0],
        "ticker": None,
        "prompt": str(prompt),
        "response": str(response)
    }])
    rec_df.to_sql("daily_stock_insights", engine, if_exists="append", index=False)



# --- 5. Daily ETL Endpoint ---
@app.get("/run-daily-pipeline")
def run_daily_pipeline():
    df = fetch_stock_data(TICKERS)
    insert_stock_data(df)
    prompt, response = generate_llm_insights(df)
    insert_insights(prompt, response, df)
    return {"status": "success", "message": "Daily pipeline completed."}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)