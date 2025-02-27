import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
from datetime import timedelta    
from Utils import get_recent_articles, analyze_ticker

articles = None

# Set up Streamlit app
st.set_page_config(layout="wide")
st.title("Technical Stock Analysis Dashboard")
st.sidebar.header("Configuration")

# Input for multiple stock tickers (comma-separated)
tickers_input = st.sidebar.text_input("Enter Stock Tickers (comma-separated):", "SG")
# Parse tickers by stripping extra whitespace and splitting on commas
tickers = [ticker.strip().upper() for ticker in tickers_input.split(",") if ticker.strip()]

# Set the date range: start date = one year before today, end date = today
end_date_default = datetime.datetime.today()
start_date_default = end_date_default - timedelta(days=60)
start_date = st.sidebar.date_input("Start Date", value=start_date_default)
end_date = st.sidebar.date_input("End Date", value=end_date_default)

# Technical indicators selection (applied to every ticker)
st.sidebar.subheader("Technical Indicators")
indicators = st.sidebar.multiselect(
    "Select Indicators:",
    ["20-Day SMA", "50-Day SMA", "20-Day EMA", "50-Day EMA", "20-Day Bollinger Bands", "VWAP","Support","Resistance"],
    default=["20-Day SMA"]
)

# Button to fetch data for all tickers
################################################################Sidebar#################################################################################################################### 
if st.sidebar.button("Fetch Data"):
    stock_data = {}
    for ticker in tickers:
        # Download data for each ticker using yfinance
        data = yf.download(ticker, start=start_date, end=end_date,multi_level_index=False)
        
        # add support lines
        support = data[data.Low == data.Low.rolling(5, center=True).min()].Low
        for i, value in enumerate(support):
            if i < 5:
                data[f'Support_{i}'] = round(value, 2)
                
        #add resistance lines
        resistance = data[data.High == data.High.rolling(5, center=True).max()].High
        for i, value in enumerate(resistance):
            if i < 5:
                data[f'Resistance_{i}'] = round(value, 2)        
        
        if not data.empty:
            stock_data[ticker] = data
        else:
            st.warning(f"No data found for {ticker}.")
            
    st.session_state["stock_data"] = stock_data
    st.success("Stock data loaded successfully for: " + ", ".join(stock_data.keys()))


# Ensure we have data to analyze
##################################################################Tabs##################################################################################################################   
    # Define a function to build chart, call the Gemini API and return structured result

if "stock_data" in st.session_state and st.session_state["stock_data"]:
    # Create tabs: first tab for overall summary, subsequent tabs per ticker
    tab_names = list(st.session_state["stock_data"].keys())
    tabs = st.tabs(tab_names)

    # Process each ticker and populate results
    for i, ticker in enumerate(st.session_state["stock_data"]):
        data = st.session_state["stock_data"][ticker]
        # Analyze ticker: get chart figure and structured output result
        fig = analyze_ticker(ticker, data, indicators)
        with tabs[i]:
            info = yf.Ticker(ticker).info
            st.subheader(f"Analysis for {ticker} ({info.get('shortName', '')})")
            st.plotly_chart(fig)
            st.write("**Detailed Justifications:**")
            
            sub_tab_names = ["Stock Information", "Latest News"]
            sub_tabs = st.tabs(sub_tab_names)

            with sub_tabs[0]:
                st.write(f"**Short Name:** {info.get('shortName', '')}")
                st.write(f"**Long Business Summary:** {info.get('longBusinessSummary', '')}")

            with sub_tabs[1]:
                articles = get_recent_articles(ticker)
                if articles != None:
                    for art in articles:
                        st.write(pub_time = datetime.datetime.fromtimestamp(art["providerPublishTime"], datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))
                        st.write(art.get("title", "No title available"))
                        st.write(art.get("link", "No link available"))                        
                else:
                    print("No articles found in the past 3 days.")
else:
    st.info("Please fetch stock data using the sidebar.")