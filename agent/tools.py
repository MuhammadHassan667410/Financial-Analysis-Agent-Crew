from crewai.tools import tool
import yfinance as yf
import pandas as pd
from langchain_tavily import TavilySearch

@tool("Fetch Stock Data Tool")
def fetch_stock_data(ticker: str) -> str:
    """
        Fetches the last 6 months of historical closing prices and volume for a given stock ticker.
    Use this tool when you need statistical data, price history, or volume data for a stock.
    Input should be the stock ticker symbol (e.g., 'AAPL', 'MSFT').
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="6mo")
    
        if hist.empty:
            return f"Error: No data found for ticker {ticker}. Please ensure it is a valid Yahoo Finance ticker."
        
        hist.index = hist.index.strftime('%Y-%m-%d')
        important_data = hist[['Close', 'Volume']]
        start_price = important_data['Close'].iloc[0]
        end_price = important_data['Close'].iloc[-1]
        percent_return = ((end_price - start_price) / start_price) * 100
        report = f"--- Financial Data for {ticker} (Last 6 Months) ---\n"
        report += f"Start Date: {hist.index[0]} | End Date: {hist.index[-1]}\n"
        report += f"Start Price: ${start_price:.2f} | End Price: ${end_price:.2f}\n"
        report += f"Percent Return: {percent_return:.2f}%\n"
        report += important_data.tail(10).to_string()
        return report
    except Exception as e:
        return f"Error fetching data for {ticker}: {str(e)}"



web_search_tool = TavilySearch(max_results=3)
web_search_tool.name = "Web Search Tool"
web_search_tool.description = "A powerful search engine optimized for comprehensive, accurate, and trusted results. Useful for finding recent news, market sentiment, or general internet searches. Input should be a specific search query."

if __name__ == "__main__":
    print(web_search_tool.invoke({"query": "Latest news about Apple stock"}))