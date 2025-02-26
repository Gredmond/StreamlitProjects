import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import datetime 

def get_recent_articles(ticker, days=3):
    # Fetches news articles for the ticker from the past 'days' (UTC).
    news = yf.Search(ticker).news
    now = datetime.datetime.now(datetime.timezone.utc)
    threshold = now - datetime.timedelta(days=days)
    articles = [
        art for art in news
        if art.get("providerPublishTime") and
           datetime.datetime.fromtimestamp(art["providerPublishTime"], datetime.timezone.utc) > threshold
    ]
    return articles

def add_technical_indicator(indicator: str, data: pd.DataFrame, fig: go.Figure) -> None:
    """Add a technical indicator to the chart."""
    if indicator == "20-Day SMA":
        sma = data['Close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(x=data.index, y=sma, mode='lines', name='SMA (20)'))
    elif indicator == "50-Day SMA":
        sma = data['Close'].rolling(window=50).mean()
        fig.add_trace(go.Scatter(x=data.index, y=sma, mode='lines', name='SMA (50)'))
    elif indicator == "20-Day EMA":
        ema = data['Close'].ewm(span=20).mean()
        fig.add_trace(go.Scatter(x=data.index, y=ema, mode='lines', name='EMA (20)'))
    elif indicator == "50-Day EMA":
        ema = data['Close'].ewm(span=50).mean()
        fig.add_trace(go.Scatter(x=data.index, y=ema, mode='lines', name='EMA (50)'))
    elif indicator == "20-Day Bollinger Bands":
        sma = data['Close'].rolling(window=20).mean()
        std = data['Close'].rolling(window=20).std()
        bb_upper = sma + 2 * std
        bb_lower = sma - 2 * std
        fig.add_trace(go.Scatter(x=data.index, y=bb_upper, mode='lines', name='BB Upper'))
        fig.add_trace(go.Scatter(x=data.index, y=bb_lower, mode='lines', name='BB Lower'))
    elif indicator == "VWAP":
        data['VWAP'] = (data['Close'] * data['Volume']).cumsum() / data['Volume'].cumsum()
        fig.add_trace(go.Scatter(x=data.index, y=data['VWAP'], mode='lines', name='VWAP'))
    elif indicator == "Support":
        for i, col in enumerate(data.columns):
            if col.startswith('Support_'):
                fig.add_trace(go.Scatter(x=data.index, y=data[col], mode='lines', name=col))
    elif indicator == "Resistance":
        for r, col in enumerate(data.columns):
            if col.startswith('Resistance_'):
                fig.add_trace(go.Scatter(x=data.index, y=data[col], mode='lines', name=col))
                
def analyze_ticker(ticker: str, data: pd.DataFrame, indicators: list) -> go.Figure:
    # Build a chart for the given ticker's data.
    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name="Candlestick"
    )])

    for indicator in indicators:
        add_technical_indicator(indicator,data,fig)

    fig.update_layout(xaxis_rangeslider_visible=False)
    return fig
