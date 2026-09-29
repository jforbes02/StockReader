from fastapi import FastAPI, HTTPException
import os
from dotenv import load_dotenv
import httpx2

load_dotenv()
app = FastAPI()

ticker_api_key = os.getenv("BRANDFETCH_API")
stock_history_key = os.getenv("ALPHAVANTAGE_API")
mag7_symbols = {
    'NVIDIA': 'NVDA',
    'APPLE': 'AAPL',
    'GOOGLE': 'GOOGL',
    'AMAZON': 'AMZN',
    'META': 'META',
    'TESLA': 'TSLA',
    'MICROSOFT': 'MSFT'
}



#return {"message": f"Ticker {mag7_symbols[symbol]}",
#        "img": f"https://cdn.brandfetch.io/ticker/{mag7_symbols[symbol]}?{ticker_api_key}"
#        }

@app.get("/stock/{company}")
async def get_stock_history(company: str):
    """
    The endpoint that feeds the data needed for the stock data when scanning
    :param company: Mag7 Company Name
    :return: The stock history of the company for the past 7 open days
        date - date of the stock history
        open - price when stock exchange open on that date
        high - highest price on stock exchange on that date
        low - lowest price on stock exchange on that date
        close - price when stock exchange close on that date
    """
    if company.upper() not in mag7_symbols:
        raise HTTPException(status_code=404, detail="Symbol not found")

    data = httpx2.get("https://www.alphavantage.co/query",
                      params={'function': 'TIME_SERIES_DAILY',
                              'symbol': mag7_symbols[company.upper()],
                              'apikey': stock_history_key,
                              'datatype': 'json',
                      },
    )

    #for errors
    data.raise_for_status()
    x = data.json()
    time = x.get("Time Series (Daily)")
    if not time:
        raise HTTPException(status_code=502, detail="No data found - issue with API provider")

    dates = sorted(time.keys(), reverse=True)[:7]
    return [{"date": d, "open": float(time[d]["1. open"]),"high": float(time[d]["2. high"]),"low": float(time[d]["3. low"]), "close": float(time[d]["4. close"])} for d in dates]