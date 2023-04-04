from datetime import datetime, timedelta
import streamlit as st
from parse import get_yahoo, get_mwatch
import plotly.graph_objects as go
from plotly.subplots import make_subplots

col1, col2 = st.columns(2)
with col1:
    today = datetime.now()
    three_months_ago = datetime.now() - timedelta(days=92)
    period = st.date_input("Период", value=(three_months_ago, today), max_value=today)

with col2:
    ticker = st.text_input("Введите тикер", value="AAPL")

service = st.selectbox("Выберите сервис", ["Yahoo Finance", "MarketWatch"])

load = st.button("Загрузить данные", type="primary", use_container_width=True)


@st.cache_data
def load_data(ticker, period, service):
    if ticker == '':
        "Пожалуйста, введите тикер"

    get_data = get_yahoo if service == "Yahoo Finance" else get_mwatch

    try:
        date_from = datetime.combine(period[0], datetime.min.time())
        date_to = datetime.combine(period[1], datetime.max.time())
        data = get_data(ticker, date_from, date_to)
    except Exception as e:
        st.error(f"Произошла ошибка при получении данных: {e}", icon="🔥")
        return

    data['Close MA-10'] = data['Close'].rolling(10, min_periods=1, center=True).mean()
    data['Close MA-20'] = data['Close'].rolling(20, min_periods=1, center=True).mean()
    data['Close MA-40'] = data['Close'].rolling(40, min_periods=1, center=True).mean()

    primary = go.Candlestick(x=data['Date'],
                       open=data['Open'],
                       high=data['High'],
                       low=data['Low'],
                       close=data['Close'],
                       showlegend=False)

    ma5 = go.Line(x=data['Date'],
                  y=data['Close MA-10'],
                  name="Close MA 10")

    ma20 = go.Line(x=data['Date'],
                   y=data['Close MA-20'],
                   name="Close MA 20")

    ma40 = go.Line(x=data['Date'],
                   y=data['Close MA-40'],
                   name="Close MA 40")

    vol = go.Bar(x=data['Date'],
                 y=data['Volume'],
                 name="Volume")

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.8, 0.2], vertical_spacing=0.04)

    fig.update_layout(
        title=ticker,
        yaxis=dict(
            ticksuffix='$'
        ),
        xaxis_rangeslider_visible=False,
        xaxis_rangebreaks=[dict(
            bounds=["sat", "mon"]
        )],
        legend=dict(
            y=1.115,
            orientation="h"
        )
    )

    fig.add_trace(primary, row=1, col=1)
    fig.add_trace(ma5, row=1, col=1)
    fig.add_trace(ma20, row=1, col=1)
    fig.add_trace(ma40, row=1, col=1)
    fig.add_trace(vol, row=2, col=1)

    st.plotly_chart(fig, theme=None, use_container_width=True, height=8000)


if load:
    load_data(ticker, period, service)
