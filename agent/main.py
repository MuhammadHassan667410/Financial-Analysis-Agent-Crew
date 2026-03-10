import os
from dotenv import load_dotenv
from crewai import Agent, LLM
from tools import fetch_stock_data, web_search_tool

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