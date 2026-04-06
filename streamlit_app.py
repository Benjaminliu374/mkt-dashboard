import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="Financial Dashboard", layout="centered")
st.title("📊 Financial Metrics + Candlestick Chart")

ticker_symbol = st.text_input("Enter Stock Ticker (e.g., AAPL)").upper()
period_choice = st.radio("Select Period (for financials)", ["Annual", "Quarterly"])

def to_thousands(series):
    return series / 1_000 if series is not None else None

def format_number(value):
    return f"{value:,.2f}" if value is not None else "N/A"

def calculate_yoy(series):
    if series is not None and len(series) > 1:
        latest, prev = series.iloc[0], series.iloc[1]
        if prev != 0:
            return ((latest - prev) / abs(prev)) * 100
    return None

def get_series(df, row_name):
    return df.loc[row_name] if df is not None and row_name in df.index else None

def get_metrics(ticker, period):
    stock = yf.Ticker(ticker)
    if period == "Annual":
        cashflow = stock.cashflow
        financials = stock.financials
    else:
        cashflow = stock.quarterly_cashflow
        financials = stock.quarterly_financials

    info = stock.info
    ebitda = info.get("ebitda")

    revenue = get_series(financials, "Total Revenue")
    fcf = get_series(cashflow, "Free Cash Flow")

    if period == "Annual":
        eps_ser = stock.earnings.T.loc["Earnings"] / stock.info.get("sharesOutstanding") if stock.earnings is not None else None
    else:
        eps_ser = stock.quarterly_earnings.T.loc["Earnings"] / stock.info.get("sharesOutstanding") if stock.quarterly_earnings is not None else None

    return ebitda, revenue, fcf, eps_ser

if ticker_symbol:
    try:
        ebitda, revenue_ser, fcf_ser, eps_ser = get_metrics(ticker_symbol, period_choice)

        rev_k = to_thousands(revenue_ser)
        fcf_k = to_thousands(fcf_ser)
        ebitda_k = ebitda / 1_000 if ebitda else None

        rev_yoy = calculate_yoy(revenue_ser)
        fcf_yoy = calculate_yoy(fcf_ser)
        eps_yoy = calculate_yoy(eps_ser)

        st.subheader(f"{ticker_symbol} Metrics")
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("EBITDA (K)", format_number(ebitda_k))
        c2.metric("Revenue (K)", format_number(rev_k.iloc[0] if rev_k is not None else None), f"{rev_yoy:.2f}%" if rev_yoy else "N/A")
        c3.metric("Free Cash Flow (K)", format_number(fcf_k.iloc[0] if fcf_k is not None else None), f"{fcf_yoy:.2f}%" if fcf_yoy else "N/A")
        c4.metric("EPS", format_number(eps_ser.iloc[0] if eps_ser is not None else None), f"{eps_yoy:.2f}%" if eps_yoy else "N/A")

        st.subheader(f"{ticker_symbol} Candlestick (with MA200 + Support/Resistance)")

        stock_data = yf.Ticker(ticker_symbol).history(period="1y")
        stock_data["MA200"] = stock_data["Close"].rolling(window=200).mean()

        # — Support / Resistance
        highs = stock_data["High"]
        lows = stock_data["Low"]

        resistance = highs.max()          # highest high
        support = lows.min()              # lowest low

        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=stock_data.index,
            open=stock_data["Open"],
            high=stock_data["High"],
            low=stock_data["Low"],
            close=stock_data["Close"],
            name="Price"
        ))

        fig.add_trace(go.Scatter(x=stock_data.index, y=stock_data["MA200"],
                                 mode="lines", name="MA200", line=dict(color="blue")))

        fig.add_hline(y=resistance, line=dict(color="red", dash="dash"), annotation_text="Resistance")
        fig.add_hline(y=support, line=dict(color="green", dash="dash"), annotation_text="Support")

        fig.update_layout(xaxis_rangeslider_visible=False, template="plotly_dark")

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error fetching data: {e}")