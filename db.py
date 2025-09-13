from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = os.getenv("DB_URL")
engine = create_engine(DB_URL)

def create_tables():
    with engine.begin() as conn:
        # Create daily_stock_prices table
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS daily_stock_prices (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            ticker VARCHAR(10) NOT NULL,
            open_price NUMERIC(12,2),
            high_price NUMERIC(12,2),
            low_price NUMERIC(12,2),
            close_price NUMERIC(12,2),
            volume BIGINT,
            UNIQUE (date, ticker)
        );
        """))

        # Create daily_stock_insights table
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS daily_stock_insights (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            ticker VARCHAR(10),
            prompt TEXT,
            response TEXT
        );
        """))

    print("Tables created (if not existed).")

# # Run on import (optional)
# if __name__ == "__main__":
#     create_tables()
