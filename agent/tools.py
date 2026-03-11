from crewai.tools import tool
import yfinance as yf
import pandas as pd
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
load_dotenv(override=True)

def _safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _compute_rsi(close_series: pd.Series, period: int = 14) -> float | None:
    if close_series is None or len(close_series) < period + 1:
        return None

    delta = close_series.diff()
    gains = delta.where(delta > 0, 0.0)
    losses = -delta.where(delta < 0, 0.0)

    avg_gain = gains.rolling(window=period).mean()
    avg_loss = losses.rolling(window=period).mean()

    rs = avg_gain / avg_loss.replace(0, pd.NA)
    rsi = 100 - (100 / (1 + rs))
    latest_rsi = rsi.iloc[-1]
    if pd.isna(latest_rsi):
        return None
    return float(latest_rsi)

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

        latest_close = important_data['Close'].iloc[-1]
        ma50 = important_data['Close'].rolling(window=50).mean().iloc[-1] if len(important_data) >= 50 else None
        rsi_14 = _compute_rsi(important_data['Close'])
        support_20d = important_data['Close'].tail(20).min() if len(important_data) >= 20 else important_data['Close'].min()
        resistance_20d = important_data['Close'].tail(20).max() if len(important_data) >= 20 else important_data['Close'].max()
        avg_vol_10d = important_data['Volume'].tail(10).mean() if len(important_data) >= 10 else important_data['Volume'].mean()
        avg_vol_30d = important_data['Volume'].tail(30).mean() if len(important_data) >= 30 else important_data['Volume'].mean()

        report = f"--- Financial Data for {ticker} (Last 6 Months) ---\n"
        report += f"Start Date: {hist.index[0]} | End Date: {hist.index[-1]}\n"
        report += f"Start Price: ${start_price:.2f} | End Price: ${end_price:.2f}\n"
        report += f"Percent Return: {percent_return:.2f}%\n"
        if ma50 is not None:
            report += f"50-day Moving Average: ${ma50:.2f}\n"
        if rsi_14 is not None:
            report += f"RSI (14): {rsi_14:.2f}\n"
        report += f"Approx Support (20D low): ${support_20d:.2f} | Approx Resistance (20D high): ${resistance_20d:.2f}\n"
        report += f"Average Volume (10D): {avg_vol_10d:,.0f} | Average Volume (30D): {avg_vol_30d:,.0f}\n"
        report += f"Latest Close vs 50DMA: {'Above' if ma50 is not None and latest_close > ma50 else 'Below'}\n"
        report += important_data.tail(10).to_string()
        return report
    except Exception as e:
        return f"Error fetching data for {ticker}: {str(e)}"


@tool("Fetch Valuation Metrics Tool")
def fetch_valuation_metrics(ticker: str) -> str:
    """
    Fetches valuation and fundamental metrics for a ticker using Yahoo Finance metadata.
    Use this tool for P/E, forward P/E, PEG, market cap, and profitability context.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info or {}

        trailing_pe = _safe_float(info.get("trailingPE"))
        forward_pe = _safe_float(info.get("forwardPE"))
        peg_ratio = _safe_float(info.get("pegRatio"))
        price_to_book = _safe_float(info.get("priceToBook"))
        ev_to_ebitda = _safe_float(info.get("enterpriseToEbitda"))
        market_cap = _safe_float(info.get("marketCap"))
        gross_margins = _safe_float(info.get("grossMargins"))
        operating_margins = _safe_float(info.get("operatingMargins"))
        revenue_growth = _safe_float(info.get("revenueGrowth"))

        report = f"--- Valuation & Fundamentals for {ticker} ---\n"
        report += f"Trailing P/E: {trailing_pe:.2f}\n" if trailing_pe is not None else "Trailing P/E: N/A\n"
        report += f"Forward P/E: {forward_pe:.2f}\n" if forward_pe is not None else "Forward P/E: N/A\n"
        report += f"PEG Ratio: {peg_ratio:.2f}\n" if peg_ratio is not None else "PEG Ratio: N/A\n"
        report += f"Price/Book: {price_to_book:.2f}\n" if price_to_book is not None else "Price/Book: N/A\n"
        report += f"EV/EBITDA: {ev_to_ebitda:.2f}\n" if ev_to_ebitda is not None else "EV/EBITDA: N/A\n"
        report += f"Market Cap: ${market_cap:,.0f}\n" if market_cap is not None else "Market Cap: N/A\n"
        report += f"Gross Margin: {gross_margins * 100:.2f}%\n" if gross_margins is not None else "Gross Margin: N/A\n"
        report += f"Operating Margin: {operating_margins * 100:.2f}%\n" if operating_margins is not None else "Operating Margin: N/A\n"
        report += f"Revenue Growth (YoY): {revenue_growth * 100:.2f}%\n" if revenue_growth is not None else "Revenue Growth (YoY): N/A\n"
        return report
    except Exception as e:
        return f"Error fetching valuation metrics for {ticker}: {str(e)}"


@tool("Fetch Competitive Context Tool")
def fetch_competitive_context(ticker: str) -> str:
    """
    Compares ticker performance and valuation versus mega-cap peers and S&P 500 ETF (SPY).
    """
    try:
        peer_universe = [ticker.upper(), "MSFT", "GOOGL", "NVDA", "SPY"]
        seen = set()
        symbols = []
        for symbol in peer_universe:
            if symbol not in seen:
                seen.add(symbol)
                symbols.append(symbol)

        comparison_rows = []
        for symbol in symbols:
            peer = yf.Ticker(symbol)
            hist_6mo = peer.history(period="6mo")
            hist_1y = peer.history(period="1y")
            info = peer.info or {}

            if hist_6mo.empty:
                continue

            start_6mo = hist_6mo["Close"].iloc[0]
            end_6mo = hist_6mo["Close"].iloc[-1]
            ret_6mo = ((end_6mo - start_6mo) / start_6mo) * 100

            ret_1y = None
            if not hist_1y.empty:
                start_1y = hist_1y["Close"].iloc[0]
                end_1y = hist_1y["Close"].iloc[-1]
                ret_1y = ((end_1y - start_1y) / start_1y) * 100

            comparison_rows.append(
                {
                    "Symbol": symbol,
                    "6M Return %": round(ret_6mo, 2),
                    "1Y Return %": round(ret_1y, 2) if ret_1y is not None else None,
                    "Trailing PE": _safe_float(info.get("trailingPE")),
                    "Forward PE": _safe_float(info.get("forwardPE")),
                    "PEG": _safe_float(info.get("pegRatio")),
                }
            )

        if not comparison_rows:
            return f"Error: Unable to build competitive comparison for {ticker}."

        df = pd.DataFrame(comparison_rows)
        df = df.sort_values(by="6M Return %", ascending=False)

        report = f"--- Competitive Context for {ticker} vs Peers & S&P 500 (SPY) ---\n"
        report += df.to_string(index=False)
        return report
    except Exception as e:
        return f"Error fetching competitive context for {ticker}: {str(e)}"
tavily_engine = TavilySearch(max_results=3)

@tool("Web Search Tool")
def web_search_tool(query: str) -> str:
    """
    A powerful search engine optimized for comprehensive, accurate, and trusted results. 
    Useful for finding recent news, market sentiment, or general internet searches. 
    Input should be a specific search query.
    """
    try:
        results = tavily_engine.invoke({"query": query})
        if not isinstance(results, dict):
            return str(results)

        formatted = ["--- Web Research Results ---"]
        for idx, item in enumerate(results.get("results", []), start=1):
            title = item.get("title", "No title")
            url = item.get("url", "No URL")
            content = item.get("content", "")
            published_date = item.get("published_date", "Unknown date")
            formatted.append(f"[{idx}] {title}")
            formatted.append(f"URL: {url}")
            formatted.append(f"Published: {published_date}")
            formatted.append(f"Summary: {content}\n")

        return "\n".join(formatted)
    except Exception as e:
         return f"Error performing web search: {str(e)}"
if __name__ == "__main__":
    print(web_search_tool.run(query="Latest news about Apple stock"))