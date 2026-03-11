from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from main import run_financial_crew
import os

app = FastAPI(title="Financial Crew API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"], # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    ticker: str

async def generate_crew_output(ticker: str):
    # Simulate streaming output
    yield "data: 🚀 Starting the Financial Crew...\n\n"
    await asyncio.sleep(1)
    
    yield f"data: 🧐 Researcher is looking up news for {ticker}...\n\n"
    await asyncio.sleep(1)
    
    yield "data: 📊 Analyst is pulling 6 months of historical data...\n\n"
    await asyncio.sleep(1)
    
    yield "data: ✍️ Report Writer is finalizing the document...\n\n"
    
    # Run the actual crew (synchronously for now)
    final_report = run_financial_crew(ticker)
    
    # Send the final report
    safe_report = final_report.replace('\n', '<br>')
    yield f"data: [REPORT_READY] {safe_report}\n\n"

@app.post("/api/analyze")
async def analyze_stock(request: AnalysisRequest):
    return StreamingResponse(
        generate_crew_output(request.ticker), 
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
