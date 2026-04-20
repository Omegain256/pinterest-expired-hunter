"use client";

import { useState } from "react";

type Opportunity = {
  profile_url: string;
  linked_website: string;
  domain_status: string;
  dns_dead: boolean;
  followers: number;
  monthly_views: number;
  domain_age: number;
  score: number;
};

export default function Home() {
  const [niche, setNiche] = useState("");
  const [maxResults, setMaxResults] = useState(20);
  const [searchMode, setSearchMode] = useState<"profiles" | "pins">("profiles");
  const [minFollowers, setMinFollowers] = useState(100);
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<Opportunity[]>([]);
  const [error, setError] = useState("");

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!niche) return;

    setLoading(true);
    setError("");
    setResults([]);

    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";
      const response = await fetch(`${backendUrl}/api/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          niche, 
          max_results: maxResults,
          mode: searchMode,
          min_followers: minFollowers
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to search. Is the backend running?");
      }

      const data = await response.json();
      if (data.results) {
        setResults(data.results);
      }
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  };

  const exportCSV = () => {
    if (results.length === 0) return;
    const headers = ["Domain", "Status", "Followers", "Views", "Age", "Profile", "Score"];
    const rows = results.map(r => [
      r.linked_website,
      r.domain_status,
      r.followers,
      r.monthly_views,
      r.domain_age,
      r.profile_url,
      r.score
    ]);
    
    const csvContent = "data:text/csv;charset=utf-8," 
      + headers.join(",") + "\n" 
      + rows.map(e => e.join(",")).join("\n");
      
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `pinterest_leads_${niche || "export"}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <main className="min-h-screen bg-slate-950 text-white selection:bg-indigo-500/30 overflow-hidden relative">
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-indigo-600/20 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-0 right-[-10%] w-[600px] h-[600px] bg-rose-600/10 blur-[150px] rounded-full pointer-events-none" />

      <div className="relative z-10 max-w-6xl mx-auto px-6 py-20 flex flex-col items-center">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-6 backdrop-blur-md">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-sm font-medium text-slate-300">Advanced Domain Hunter v2</span>
          </div>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-4 text-transparent bg-clip-text bg-gradient-to-br from-white to-slate-400">
            Find Dead Links.
          </h1>
          <p className="text-slate-400 text-lg md:text-xl max-w-2xl mx-auto italic">
            "One man's broken link is another man's traffic goldmine."
          </p>
        </div>

        <div className="w-full max-w-3xl flex flex-col gap-4">
          <form 
            onSubmit={handleSearch} 
            className="flex flex-col md:flex-row gap-4 bg-white/5 p-4 rounded-3xl border border-white/10 backdrop-blur-xl shadow-2xl transition-all hover:bg-white/[0.07]"
          >
            <div className="flex-1 flex gap-2">
                <select 
                  value={searchMode}
                  onChange={(e) => setSearchMode(e.target.value as any)}
                  className="bg-black/40 border border-white/10 rounded-xl px-3 text-xs font-bold text-indigo-400 focus:outline-none uppercase tracking-tighter"
                >
                    <option value="profiles">Profiles</option>
                    <option value="pins">Pin Links</option>
                </select>
                <input
                  type="text"
                  placeholder={`Search ${searchMode === 'profiles' ? 'Profiles' : 'Pin Links'} by niche...`}
                  value={niche}
                  onChange={(e) => setNiche(e.target.value)}
                  className="w-full bg-black/20 border border-white/5 rounded-xl px-5 py-4 text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
                  required
                />
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="px-8 py-4 bg-indigo-500 hover:bg-indigo-400 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-2xl transition-all shadow-[0_0_20px_rgba(99,102,241,0.4)] flex items-center justify-center min-w-[140px]"
            >
              {loading ? "Hunting..." : "Start Hunt"}
            </button>
          </form>

          {/* Advanced Options Bar */}
          <div className="px-4">
            <button 
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="text-xs text-slate-500 hover:text-indigo-400 flex items-center gap-2 transition-colors uppercase font-bold tracking-widest"
            >
                {showAdvanced ? '[-] Hide Settings' : '[+] Advanced Settings'}
            </button>
            
            {showAdvanced && (
                <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-6 p-6 bg-white/5 border border-white/10 rounded-2xl animate-fade-in">
                    <div className="space-y-2">
                        <label className="text-xs text-slate-400 uppercase font-mono">Max Scan Limit: {maxResults}</label>
                        <input 
                            type="range" min="10" max="100" step="10"
                            value={maxResults} onChange={(e) => setMaxResults(Number(e.target.value))}
                            className="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                        />
                    </div>
                    <div className="space-y-2">
                        <label className="text-xs text-slate-400 uppercase font-mono">Min Followers: {minFollowers}+</label>
                        <input 
                            type="range" min="0" max="10000" step="100"
                            value={minFollowers} onChange={(e) => setMinFollowers(Number(e.target.value))}
                            className="w-full h-1 bg-white/10 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                        />
                    </div>
                </div>
            )}
          </div>
        </div>

        {error && (
          <div className="mt-8 px-6 py-4 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl">
            {error}
          </div>
        )}

        <div className="w-full mt-16">
          {(!loading && results.length > 0) && (
            <div className="animate-fade-in-up">
              <div className="flex items-center justify-between mb-8">
                <h2 className="text-2xl font-semibold">Discovery Results</h2>
                <button 
                    onClick={exportCSV}
                    className="px-4 py-2 bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-xs font-bold rounded-xl hover:bg-emerald-500/30 transition-all uppercase tracking-widest"
                >
                    Download CSV
                </button>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {results.map((r, i) => (
                  <div
                    key={i}
                    className="group relative bg-white/5 border border-white/5 hover:border-indigo-500/50 p-6 rounded-2xl transition-all duration-300 hover:-translate-y-1 hover:bg-white/[0.08]"
                  >
                    <div className="flex justify-between items-start mb-4">
                      <div className="truncate pr-4 flex-1">
                        <p className="text-[10px] text-slate-500 font-mono mb-1 uppercase tracking-wider">Opportunity</p>
                        <h3 className="text-lg font-medium text-white truncate break-all">
                          {r.linked_website}
                        </h3>
                      </div>
                      <div className="px-2 py-1 rounded bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 font-bold text-xs">
                        {r.score}
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-2 mb-4">
                      <div className="px-3 py-2 bg-black/40 rounded-xl border border-white/5">
                        <p className="text-[10px] text-slate-500 uppercase">Fans</p>
                        <p className="text-sm font-bold text-slate-200">{(r.followers / 1000).toFixed(1)}K</p>
                      </div>
                      <div className="px-3 py-2 bg-black/40 rounded-xl border border-white/5">
                        <p className="text-[10px] text-slate-500 uppercase">Age</p>
                        <p className="text-sm font-bold text-slate-200">{r.domain_age}Y</p>
                      </div>
                    </div>

                    <div className="flex items-center justify-between mt-auto">
                        <a href={r.profile_url} target="_blank" className="text-[10px] text-indigo-400 hover:underline uppercase font-bold tracking-widest">
                            View Source
                        </a>
                        <span className="text-[10px] text-rose-400 font-bold uppercase py-1 px-2 bg-rose-500/10 rounded-md">
                            Dead DNS
                        </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {(!loading && results.length === 0 && !error) && (
            <div className="text-center py-20 opacity-50 bg-white/5 rounded-3xl border border-white/5">
               <span className="text-6xl mb-4 block filter grayscale opacity-50">🦅</span>
               <p className="text-slate-400 max-w-sm mx-auto">
                  {niche ? `Scanning for depth... No dead links found yet for '${niche}'. Try Pin-Link mode for wider reach.` : "Configure your target and begin the hunt."}
               </p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
