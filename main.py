import requests
import os
from twilio.rest import Client

STOCK = "AAPL"
alpha_vantage_api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
news_api_key = os.environ.get("NEWS_API_KEY")
ALPHA_VANTAGE_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_SENDER_PHONE = "+18456713421"
TWILIO_RECIPIENT_PHONE = "+380667806615"

alpha_vantage_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": alpha_vantage_api_key
}

news_params = {
    "q": STOCK,
    "apikey": news_api_key
}


def price_change():
    alpha_vantage_response = requests.get(url=ALPHA_VANTAGE_ENDPOINT, params=alpha_vantage_params)
    alpha_vantage_response.raise_for_status()
    alpha_vantage_data = alpha_vantage_response.json()

    last_trading_day = list(alpha_vantage_data["Time Series (Daily)"].keys())[0]
    last_trading_day_stats = alpha_vantage_data["Time Series (Daily)"][last_trading_day]
    before_last_trading_day = list(alpha_vantage_data["Time Series (Daily)"].keys())[1]
    before_last_trading_day_stats = alpha_vantage_data["Time Series (Daily)"][before_last_trading_day]
    last_trading_day_open = float(last_trading_day_stats["1. open"])
    before_last_trading_day_close = float(before_last_trading_day_stats["4. close"])
    percent_change = round(
        (last_trading_day_open - before_last_trading_day_close) / before_last_trading_day_close * 100, 2)
    if percent_change > 0:
        return f"🔺{percent_change}%"
    elif percent_change < 0:
        return f"🔻{percent_change}%"
    else:
        return "No change"


def get_news():
    news_response = requests.get(url=NEWS_ENDPOINT, params=news_params)
    news_response.raise_for_status()
    news_data = news_response.json()

    news_articles = news_data["articles"][:3]
    news_articles_data = {}
    for article in news_articles:
        news_articles_data[article["title"]] = article["description"]
    return news_articles_data


client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
price_change = price_change()
news_articles = get_news()
for title, description in news_articles.items():
    client.messages.create(
        body=f"{STOCK}: {price_change}\n\nHeadline: {title}\n\nBrief: {description}",
        from_=f"{TWILIO_SENDER_PHONE}",
        to=f"{TWILIO_RECIPIENT_PHONE}"
    )
