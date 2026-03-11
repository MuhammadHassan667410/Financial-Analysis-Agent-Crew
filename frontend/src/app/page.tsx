'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Activity, Terminal, CheckCircle2, FileText, ChevronRight } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export default function Home() {
  const [ticker, setTicker] = useState('AAPL');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [logs, setLogs] = useState<string[]>([]);
  const [finalReport, setFinalReport] = useState<string | null>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ticker) return;

    setIsAnalyzing(true);
    setLogs([]);
    setFinalReport(null);

    try {
      // Connect to our FastAPI SSE endpoint
      const response = await fetch('http://127.0.0.1:8000/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ticker: ticker.toUpperCase() }),
      });

      if (!response.body) throw new Error("No readable stream");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;
        if (value) {
          const chunk = decoder.decode(value, { stream: true });
          // SSE chunks are strictly separated by double newlines usually
          const lines = chunk.split('\n\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.replace('data: ', '').trim();
              if (!data) continue;

              if (data.startsWith('[REPORT_READY]')) {
                // Done! Extract the report (replace <br> back to \n and format it safely)
                const rawReport = data.replace('[REPORT_READY] ', '');
                const cleanReport = rawReport.replace(/<br>/g, '\n');
                setFinalReport(cleanReport);
                setIsAnalyzing(false);
              } else {
                // Just a normal log message from the streaming crew
                setLogs(prev => [...prev, data]);
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('Error connecting to AI crew:', error);
      setLogs(prev => [...prev, '❌ Connection error: Could not reach the AI agent team. Ensure the FastAPI backend is running!']);
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 font-sans selection:bg-blue-500/30">
      {/* Dynamic Background Effects */}
      <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-1/4 w-[500px] h-[500px] bg-blue-600/20 blur-[120px] rounded-full mix-blend-screen" />
        <div className="absolute bottom-1/4 left-1/4 w-[600px] h-[600px] bg-teal-600/10 blur-[150px] rounded-full mix-blend-screen" />
      </div>

      <main className="max-w-5xl mx-auto p-6 md:p-12 relative z-10 flex flex-col gap-8">
        {/* Header */}
        <header className="flex flex-col items-center text-center gap-4 py-8">
          <div className="inline-flex items-center justify-center p-3 bg-blue-500/10 border border-blue-500/20 rounded-2xl shadow-[0_0_30px_rgba(59,130,246,0.15)] backdrop-blur-sm mb-2">
            <Activity className="w-8 h-8 text-blue-400" />
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-white via-blue-100 to-blue-400 bg-clip-text text-transparent">
            AI Financial Crew
          </h1>
          <p className="text-slate-400 max-w-xl text-lg">
            Unleash a team of autonomous AI agents to research, analyze, and synthesize professional stock market reports in real-time.
          </p>
        </header>

        {/* Action Form */}
        <div className="w-full max-w-2xl mx-auto">
          <form onSubmit={handleAnalyze} className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-blue-500 via-teal-400 to-blue-500 rounded-2xl blur opacity-25 group-hover:opacity-40 transition duration-1000 group-hover:duration-200"></div>
            <div className="relative flex items-center bg-slate-900 border border-slate-700/50 rounded-2xl p-2 shadow-2xl backdrop-blur-xl transition-all focus-within:border-blue-500/50">
              <div className="pl-4 pr-3 text-slate-400 font-semibold">
                $
              </div>
              <input
                type="text"
                value={ticker}
                onChange={(e) => setTicker(e.target.value.toUpperCase())}
                placeholder="Enter Stock Ticker (e.g. AAPL, TSLA)"
                disabled={isAnalyzing}
                className="flex-1 bg-transparent border-none outline-none text-xl font-medium tracking-wide placeholder:text-slate-600 uppercase transition-all disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={isAnalyzing || !ticker}
                className="ml-2 bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl font-medium flex items-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed active:scale-95 shadow-[0_0_20px_rgba(37,99,235,0.3)]"
              >
                {isAnalyzing ? (
                  <span className="flex items-center gap-2 animate-pulse">
                    <Activity className="w-5 h-5 animate-spin" />
                    Analyzing
                  </span>
                ) : (
                  <>
                    <Send className="w-5 h-5" />
                    Kickoff Crew
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 mt-4">

          {/* Live Agent Terminal / Logs */}
          <div className="lg:col-span-5 h-[500px] flex flex-col bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl relative">
            <div className="absolute inset-0 bg-gradient-to-b from-white/[0.02] to-transparent pointer-events-none" />
            <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-800/80 bg-slate-900/50">
              <Terminal className="w-4 h-4 text-slate-500" />
              <span className="text-sm font-semibold tracking-wider text-slate-400 uppercase">Agent Terminal</span>
              <div className="ml-auto flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-slate-700"></div>
                <div className="w-3 h-3 rounded-full bg-slate-700"></div>
                <div className="w-3 h-3 rounded-full bg-slate-700"></div>
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-4 font-mono text-sm leading-relaxed space-y-3">
              {logs.length === 0 && !isAnalyzing && (
                <div className="text-slate-600 flex flex-col items-center justify-center h-full gap-3">
                  <Activity className="w-8 h-8 opacity-20" />
                  <p>Awaiting deployment orders...</p>
                </div>
              )}

              {logs.map((log, index) => (
                <div
                  key={index}
                  className="animate-in fade-in slide-in-from-bottom-2 duration-300 flex items-start gap-3"
                >
                  <ChevronRight className="w-4 h-4 text-blue-500 mt-0.5 shrink-0" />
                  <span className="text-slate-300 break-words">{log}</span>
                </div>
              ))}
              <div ref={logsEndRef} />

              {isAnalyzing && (
                <div className="flex items-center gap-2 text-slate-500 mt-4 animate-pulse">
                  <ChevronRight className="w-4 h-4" />
                  <span className="w-2 h-4 bg-slate-500 inline-block animate-[bounce_1s_infinite]"></span>
                </div>
              )}
            </div>
          </div>

          {/* Final Executive Report Area */}
          <div className="lg:col-span-7 h-[500px] bg-[#0c1222] border border-slate-800 rounded-3xl p-6 shadow-2xl relative overflow-hidden flex flex-col">
            <div className="absolute top-0 right-0 w-64 h-64 bg-teal-500/5 blur-[100px] rounded-full pointer-events-none" />

            <div className="flex items-center gap-3 mb-6 relative z-10">
              <div className="p-2 bg-slate-800/80 rounded-lg border border-slate-700">
                <FileText className="w-5 h-5 text-teal-400" />
              </div>
              <h2 className="text-xl font-bold text-slate-200 tracking-tight">Executive Summary</h2>

              {finalReport && (
                <span className="ml-auto flex items-center gap-1.5 text-xs font-medium text-emerald-400 bg-emerald-400/10 px-3 py-1 rounded-full border border-emerald-400/20">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Verified & Synthesized
                </span>
              )}
            </div>

            <div className="flex-1 overflow-y-auto pr-4 custom-scrollbar relative z-10">
              {!finalReport ? (
                <div className="h-full flex flex-col items-center justify-center text-slate-600 gap-4">
                  <FileText className="w-12 h-12 opacity-10" />
                  <p className="max-w-xs text-center text-sm leading-relaxed">
                    The final synthesized report from the Report Writer will appear here once the crew completes their analysis.
                  </p>
                </div>
              ) : (
                <article className="prose prose-invert prose-slate prose-headings:text-slate-200 prose-a:text-blue-400 max-w-none prose-p:leading-relaxed prose-li:marker:text-blue-500 animate-in fade-in duration-700">
                  <ReactMarkdown>{finalReport}</ReactMarkdown>
                </article>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
