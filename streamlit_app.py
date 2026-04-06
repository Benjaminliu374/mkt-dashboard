import streamlit as st
import pandas as pd
import math
import yfinance as yf 

def get_stock_financials(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)

    # Cash Flow Statement
    cashflow = stock.cashflow

    # Financials (Income Statement)
    financials = stock.financials

    # Key metrics
    info = stock.info

    # Extract EBITDA and EPS
    ebitda = info.get("ebitda")
    eps = info.get("trailingEps")

    return {
        "cashflow": cashflow,
        "financials": financials,
        "ebitda": ebitda,
        "eps": eps
    }


if __name__ == "__main__":
    ticker = input("Enter stock ticker (e.g., AAPL): ").upper()

    data = get_stock_financials(ticker)

    print("\n=== EBITDA ===")
    print(data["ebitda"])

    print("\n=== EPS ===")
    print(data["eps"])

    print("\n=== Cash Flow Statement ===")
    print(data["cashflow"])

    print("\n=== Income Statement ===")
    print(data["financials"])
