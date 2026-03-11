import os
from dotenv import load_dotenv
from crewai import Agent, LLM
from tools import (
    fetch_stock_data,
    fetch_valuation_metrics,
    fetch_competitive_context,
    web_search_tool,
)
from crewai import Task, Crew

load_dotenv(override=True)

azure_llm = LLM(
    model=f"azure/{os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')}",
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)
print(f"✅ Successfully initialized LLM: {os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')}")
researcher = Agent(
    role="Senior Market Researcher",
    goal="Gather the most recent and impactful market developments regarding {ticker}, with verifiable sources and clear risk implications.",
    backstory="""You are a veteran Wall Street researcher. 
    Your expertise lies in finding the most relevant news articles, press releases, and market sentiment 
    that could affect a company's stock price. You always provide source links and publication dates.""",
    verbose=True, 
    allow_delegation=False, 
    tools=[web_search_tool],
    llm=azure_llm
)

data_analyst = Agent(
    role="Quantitative Data Analyst",
    goal="Deliver evidence-backed analysis for {ticker} covering performance, valuation, technicals, and peer-relative context.",
    backstory="""You are a brilliant quantitative analyst. 
    You excel at looking at raw stock prices, calculating returns, and explaining 
    price movements in a clear, concise manner. You support every conclusion with specific numbers and comparisons.""",
    verbose=True,
    allow_delegation=False,
    tools=[fetch_stock_data, fetch_valuation_metrics, fetch_competitive_context],
    llm=azure_llm
)

report_writer = Agent(
    role="Financial Report Writer",
    goal="Synthesize research and analysis into an institutional-quality stock report for {ticker}, with complete sections and clear sourcing.",
    backstory="""You are a renowned financial journalist and report writer. 
    You take complex research and data and weave it into a cohesive, highly professional executive summary 
    that investors can easily understand. You do not make up data; you strictly use what the researchers and analysts provide.
    If any required section lacks data, you explicitly write 'Data Not Available' instead of fabricating.""",
    verbose=True,
    allow_delegation=False,
    tools=[],
    llm=azure_llm
)
print("✅ Agents successfully defined!")

research_task = Task(
    description="""Search for the most recent and impactful developments regarding {ticker}.
    You MUST include at least 5 high-signal items across:
    1) earnings/financial results,
    2) AI/product roadmap updates,
    3) analyst target/recommendation changes,
    4) regulatory or legal developments,
    5) macro or FX impacts.

    For each item include:
    - concise summary,
    - bull/bear interpretation,
    - a source URL and publication date.

    Also provide an explicit risk list that names and briefly explains key risks (e.g., China exposure, antitrust pressure, AI monetization delays, FX headwinds).""",
    expected_output="A structured research brief with at least 5 market news items, explicit risk bullets, and source citations (URL + date) for each item.",
    agent=researcher
)

data_analysis_task = Task(
    description="""Use all quantitative tools for {ticker}:
    - fetch_stock_data
    - fetch_valuation_metrics
    - fetch_competitive_context

    Produce a structured analytical package that includes:
    1) Performance: 6-month return and recent volatility behavior.
    2) Technical analysis evidence: key support/resistance, 50-day and 200-day moving averages (if available), RSI(14), and volume trend interpretation.
    3) Valuation analysis: trailing P/E, forward P/E, PEG, and whether valuation appears cheap/fair/expensive versus peers and recent trend.
    4) Competitive context: compare {ticker} performance to MSFT, GOOGL, NVDA, and SPY over 6M/1Y where available.

    Every claim must reference the numeric evidence from tool outputs.""",
    expected_output="A detailed quantitative brief with valuation, technical indicators, and peer/S&P benchmarking supported by explicit numbers.",
    agent=data_analyst
)

writing_task = Task(
    description="""Create a final professional report for {ticker} by combining the research and quantitative briefs.

    REQUIRED HEADINGS (all mandatory):
    - Executive Summary
    - Market News
    - Data Analysis
    - Valuation Analysis
    - Technical Analysis
    - Risk Assessment
    - Competitive Context
    - Executive Conclusion
    - Sources

    Quality requirements:
    - Keep existing strengths from prior report (clear narrative + performance summary).
    - Add missing institutional elements: valuation judgment (cheap/fair/expensive), explicit risk section, evidence-backed technical section, peer/S&P context, and source citations.
    - Do not invent facts. If missing, state Data Not Available.
    - In the Sources section, list every cited link with publication date and outlet.
    - Write in concise, professional markdown suitable for investor review.""",
    expected_output="A complete markdown investment report containing all required sections and source-backed analysis.",
    agent=report_writer
)

financial_crew = Crew(
    agents=[researcher, data_analyst, report_writer],
    tasks=[research_task, data_analysis_task, writing_task],
    verbose=True
)

def run_financial_crew(ticker: str):
    print(f"\n🚀 Starting Financial Analysis Crew for {ticker}...\n")
    # Kickoff the crew
    result = financial_crew.kickoff(inputs={"ticker": ticker})
    return result.raw

if __name__ == "__main__":
    report_text = run_financial_crew("AAPL")
    
    # Save the report to a markdown file
    with open("AAPL_Analysis_Report.md", "w", encoding="utf-8") as file:
        file.write(report_text)
    
    print("\n✅ Report successfully saved to AAPL_Analysis_Report.md!")