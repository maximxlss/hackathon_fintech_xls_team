from datetime import datetime
from io import StringIO
import streamlit as st
import requests
import pandas as pd
from pandas import DataFrame

_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}


def check(data: DataFrame) -> DataFrame:
    for col in data.columns:
        if col != "Volume" and data[col].isnull().any():
            wrong_data = data[data[col].isnull()]
            raise Exception(f"Неверный ответ от сервера. Отсуствует поле {col} в столбцах:\n{wrong_data}")


@st.cache_data
def get_yahoo(ticker: str, date_from: datetime, date_to: datetime) -> DataFrame:
    url = f"https://finance.yahoo.com/quote/{ticker}/history?period1={int(date_from.timestamp())}&period2={int(date_to.timestamp())}&interval=1d"
    res = requests.get(url, headers=_headers)
    data = pd.read_html(res.text)
    data = data[0][:-1]
    data = data[data["Open"].str.contains("Dividend") == False]
    data['Date'] = pd.to_datetime(data['Date'])
    data = data[['Date', 'Open', 'High', 'Low', 'Adj Close**', 'Volume']]
    data = data.set_axis(['Date', 'Open', 'High', 'Low', 'Close', 'Volume'], axis='columns', copy=False)
    data['Volume'].replace({'-': None}, inplace=True)
    for col in data.columns:
        if col != 'Date':
            data[col] = pd.to_numeric(data[col])
    check(data)
    return data


@st.cache_data
def get_mwatch(ticker: str, date_from: datetime, date_to: datetime):
    url = f"https://www.marketwatch.com/investing/stock/{ticker}/downloaddatapartial?startdate={date_from.strftime('%m/%d/%Y')}%2000:00:00&enddate={date_to.strftime('%m/%d/%Y')}%2023:59:59&daterange=d30&frequency=p1d&csvdownload=true&downloadpartial=false&newdates=false"
    res = requests.get(url, headers=_headers)
    data = pd.read_csv(StringIO(res.text))
    data['Date'] = pd.to_datetime(data['Date'])
    data = data[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    data['Volume'] = data['Volume'].str.replace(",", "")
    for col in data.columns:
        if col != 'Date':
            data[col] = pd.to_numeric(data[col])
    check(data)
    return data
