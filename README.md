# Financial Analysis Agent Crew

AI-powered stock analysis workspace that combines a multi-agent backend (CrewAI + FastAPI) with a modern Next.js frontend to generate professional equity reports.

The pipeline is designed to produce institution-style reports with these required sections:
- Executive Summary
- Market News
- Data Analysis
- Valuation Analysis
- Technical Analysis
- Risk Assessment
- Competitive Context
- Executive Conclusion
- Sources

---

## What This Project Does

Given a stock ticker (for example `AAPL`), the system:
1. Researches recent market news with links and dates.
2. Pulls market data and computes performance + technical indicators.
3. Computes valuation metrics (P/E, forward P/E, PEG, etc.).
4. Compares the ticker vs peers (`MSFT`, `GOOGL`, `NVDA`) and `SPY`.
5. Synthesizes everything into a single markdown report.

---

## Repository Structure

```text
Financial-Analysis-Agent-Crew/
├── agent/
│   ├── api.py              # FastAPI server (streaming endpoint)
│   ├── main.py             # Crew and task orchestration
│   └── tools.py            # Data + web research tools
├── frontend/
│   ├── package.json        # Next.js scripts and dependencies
│   └── src/app/            # App router UI
├── AAPL_Analysis_Report.md # Example generated report
└── README.md
```

---

## Tech Stack

### Backend
- Python 3.11+
- CrewAI
- FastAPI + Uvicorn
- yfinance
- Tavily search integration
- Azure OpenAI (LLM via environment variables)

### Frontend
- Next.js 16
- React 19
- TypeScript
- Tailwind CSS 4
- react-markdown

---

## Prerequisites

- Python 3.11+
- Node.js 20+
- npm 10+
- Tavily API key
- Azure OpenAI deployment and credentials

---

## Environment Variables

Create/update `.env` in the project root:

```env
# Azure OpenAI
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-xx-xx

# Tavily
TAVILY_API_KEY=your_tavily_key
```

Notes:
- `AZURE_OPENAI_ENDPOINT` should be your base endpoint.
- Use a deployed model name in `AZURE_OPENAI_DEPLOYMENT_NAME`.

---

## Local Setup

### 1) Backend Setup

From the project root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install crewai fastapi uvicorn python-dotenv yfinance pandas langchain-tavily
```

Run API server:

```bash
cd agent
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Backend will run at:
- `http://localhost:8000`

### 2) Frontend Setup

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend will run at:
- `http://localhost:3000`

---

## How to Use

1. Open `http://localhost:3000`.
2. Enter a ticker symbol (example: `AAPL`).
3. Start analysis.
4. Watch streaming progress updates from the backend.
5. Review final generated report in the UI.

---

## API Reference

### `POST /api/analyze`

Request body:

```json
{
  "ticker": "AAPL"
}
```

Response:
- Server-Sent Events (`text/event-stream`)
- Emits progress messages and finally one `[REPORT_READY]` payload containing report content.

---

## Report Quality Standard (5/5 Target)

The current crew/task setup is configured to enforce:
- Valuation section with explicit multiples and judgment (cheap/fair/expensive).
- Technical section with evidence (support/resistance, moving averages, RSI, volume trend).
- Risk section with explicit named risks.
- Competitive benchmarking vs peers + S&P proxy (`SPY`).
- Sources section with URLs and publication dates.

If data is unavailable, the writer is instructed to output `Data Not Available` rather than fabricate.

---

## Troubleshooting

### CORS issues
- Backend currently allows `http://localhost:3000`.
- If frontend runs on a different origin, update `allow_origins` in `agent/api.py`.

### Empty/weak valuation or peer metrics
- Yahoo Finance metadata can be incomplete for some tickers.
- Re-run analysis later or use a different ticker to verify pipeline behavior.

### No report generated
- Confirm `.env` values are valid.
- Check backend logs for API/auth errors.
- Verify Tavily and Azure OpenAI credentials are active.

### Dependency errors
- Ensure virtual environment is activated.
- Upgrade `pip` and reinstall dependencies.

---

## Future Enhancements

- Persist reports in a database.
- Add unit/integration tests for tools and API.
- Add configurable peer universe per sector.
- Add report export (`.md`, `.pdf`).
- Add historical backtesting of recommendation signals.

---

## Disclaimer

This project is for educational and research purposes only and is **not** investment advice.
