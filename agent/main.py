import os
from dotenv import load_dotenv
from crewai import Agent, LLM
from tools import fetch_stock_data, web_search_tool
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
    goal="Gather the most recent and impactful news regarding the stock {ticker}.",
    backstory="""You are a veteran Wall Street researcher. 
    Your expertise lies in finding the most relevant news articles, press releases, and market sentiment 
    that could affect a company's stock price.""",
    verbose=True, 
    allow_delegation=False, 
    tools=[web_search_tool],
    llm=azure_llm
)

data_analyst = Agent(
    role="Quantitative Data Analyst",
    goal="Analyze the historical price data for {ticker} and summarize its recent performance.",
    backstory="""You are a brilliant quantitative analyst. 
    You excel at looking at raw stock prices, calculating returns, and explaining 
    price movements in a clear, concise manner.""",
    verbose=True,
    allow_delegation=False,
    tools=[fetch_stock_data],
    llm=azure_llm
)

report_writer = Agent(
    role="Financial Report Writer",
    goal="Synthesize the news research and the data analysis into a professional, easy-to-read executive summary for {ticker}.",
    backstory="""You are a renowned financial journalist and report writer. 
    You take complex research and data and weave it into a cohesive, highly professional executive summary 
    that investors can easily understand. You do not make up data; you strictly use what the researchers and analysts provide.""",
    verbose=True,
    allow_delegation=False,
    tools=[],
    llm=azure_llm
)
print("✅ Agents successfully defined!")

research_task = Task(
    description="""Search the internet for the most recent and impactful news regarding the stock {ticker}.
    Focus on earnings reports, product launches, macroeconomic factors, or analyst ratings.
    Compile a summary of at least 3 major news points.""",
    expected_output="A bulleted summary of the 3 most important recent news items regarding {ticker}.",
    agent=researcher
)

data_analysis_task = Task(
    description="""Use the fetch_stock_data tool to pull the last 6 months of price history for {ticker}.
    Analyze the percentage return, the recent price volatility, and the overall trend.""",
    expected_output="A statistical summary including the 6-month return, current price, and a brief analysis of the trend.",
    agent=data_analyst
)

writing_task = Task(
    description="""Take the output from the Market Researcher and the Quantitative Data Analyst.
    Combine them into a professional, cohesive executive summary for {ticker}.
    The report should be structured with clear headings: 'Market News', 'Data Analysis', and 'Executive Conclusion'.""",
    expected_output="A highly professional text report synthesizing all gathered research and data.",
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