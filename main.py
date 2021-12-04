import requests
import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

account_sid = os.getenv('account_sid')
auth_token = os.getenv('auth_token')
stock_api_key = os.getenv('stock_api_key')
news_api_key = os.getenv('news_api_key')
from_number = os.getenv('from_number')
to_number = os.getenv('to_number')

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": stock_api_key
}

stock_response = requests.get(url=STOCK_ENDPOINT, params=stock_params)
stock_response.raise_for_status()
data = stock_response.json()

time_series = data['Time Series (Daily)']
data_list = [value for (key, value) in time_series.items()]

yday_closing_val = float(data_list[0]['4. close'])
day_before_closing = float(data_list[1]['4. close'])
difference_val = yday_closing_val - day_before_closing

if difference_val > 0:
    icon = "⬆️"
else:
    icon = "⬇️"

diff_percent = round((difference_val / yday_closing_val) * 100)

if abs(diff_percent) > 4:
    news_params = {
        "apiKey": news_api_key,
        "qInTitle": STOCK,
    }

    news_response = requests.get(url=NEWS_ENDPOINT, params=news_params)
    news_data = news_response.json()
    articles = news_data['articles']
    top_three = articles[:3]

    articles_list = [f"{COMPANY_NAME} - {STOCK} {icon} {diff_percent}% \nHeadline: {article['title']}." \
                     f"\nBrief: {article['description']}" for article in top_three]

    client = Client(account_sid, auth_token)

    for article in articles_list:
        message = client.messages \
            .create(
                body=article,
                from_=f"{from_number}",
                to=f"{to_number}"
            )
        print(message.status)
