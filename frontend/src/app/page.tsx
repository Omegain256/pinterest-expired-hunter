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
  const [maxResults, setMaxResults] = useState(10);
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
      // In production, you would change this to your Render.com backend URL
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080";
      const response = await fetch(`${backendUrl}/api/search`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ niche, max_results: maxResults }),
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

  return (
    <main className="min-h-screen bg-slate-950 text-white selection:bg-indigo-500/30 overflow-hidden relative">
      {/* Background Orbs */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[500px] bg-indigo-600/20 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-0 right-[-10%] w-[600px] h-[600px] bg-rose-600/10 blur-[150px] rounded-full pointer-events-none" />

      <div className="relative z-10 max-w-6xl mx-auto px-6 py-20 flex flex-col items-center">
        {/* Header */}
        <div className="text-center mb-12 animate-fade-in-up">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-6 backdrop-blur-md">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-sm font-medium text-slate-300">Pinterest Expired Domain Hunter</span>
          </div>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-4 text-transparent bg-clip-text bg-gradient-to-br from-white to-slate-400">
            Reclaim Dead Domains.
          </h1>
          <p className="text-slate-400 text-lg md:text-xl max-w-2xl mx-auto">
            Discover established Pinterest profiles linked to expired web domains. Claim them, inherit their SEO gravity, and scale your traffic instantly.
          </p>
        </div>

        {/* Action Form */}
        <form 
          onSubmit={handleSearch} 
          className="w-full max-w-2xl flex flex-col md:flex-row gap-4 bg-white/5 p-4 rounded-2xl border border-white/10 backdrop-blur-xl shadow-2xl transition-all hover:bg-white/[0.07]"
        >
          <div className="flex-1 relative">
            <input
              type="text"
              placeholder="Enter a niche (e.g. 'fitness', 'cooking')"
              value={niche}
              onChange={(e) => setNiche(e.target.value)}
              className="w-full bg-black/20 border border-white/5 rounded-xl px-5 py-4 text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
              required
            />
          </div>
          <div className="w-full md:w-32 relative">
            <input
              type="number"
              min="5"
              max="100"
              value={maxResults}
              onChange={(e) => setMaxResults(Number(e.target.value))}
              placeholder="Max Limit"
              className="w-full bg-black/20 border border-white/5 rounded-xl px-5 py-4 text-white placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all font-mono"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-8 py-4 bg-indigo-500 hover:bg-indigo-400 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-all shadow-[0_0_20px_rgba(99,102,241,0.4)] hover:shadow-[0_0_30px_rgba(99,102,241,0.6)] flex items-center justify-center min-w-[140px]"
          >
            {loading ? (
              <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : "Hunt Domains"}
          </button>
        </form>

        {error && (
          <div className="mt-8 px-6 py-4 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl">
            {error}
          </div>
        )}

        {/* Results Area */}
        <div className="w-full mt-16">
          {(!loading && results.length > 0) && (
            <div className="animate-fade-in-up">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-semibold">High-Value Opportunities</h2>
                <span className="px-3 py-1 bg-indigo-500/10 text-indigo-400 text-sm font-medium rounded-lg border border-indigo-500/20">
                  {results.length} Found
                </span>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {results.map((r, i) => (
                  <a
                    key={i}
                    href={r.profile_url}
                    target="_blank"
                    rel="noreferrer"
                    className="group block bg-white/5 border border-white/5 hover:border-indigo-500/50 p-6 rounded-2xl transition-all duration-300 hover:-translate-y-1 hover:bg-white/[0.08]"
                  >
                    <div className="flex justify-between items-start mb-4">
                      <div className="truncate pr-4">
                        <p className="text-xs text-slate-400 font-mono mb-1 uppercase tracking-wider">Linked Domain</p>
                        <h3 className="text-lg font-medium text-white group-hover:text-indigo-400 transition-colors truncate">
                          {r.linked_website}
                        </h3>
                      </div>
                      <div className="flex flex-col items-end">
                        <div className="px-2.5 py-1 rounded bg-indigo-500 text-white font-bold text-xs shadow-[0_0_10px_rgba(99,102,241,0.3)]">
                          {r.score} PTS
                        </div>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 mb-5">
                      <div className="bg-black/30 p-3 rounded-xl border border-white/5">
                        <p className="text-xs text-slate-400 mb-1">Followers</p>
                        <p className="font-semibold text-slate-200">{(r.followers / 1000).toFixed(1)}K</p>
                      </div>
                      <div className="bg-black/30 p-3 rounded-xl border border-white/5">
                        <p className="text-xs text-slate-400 mb-1">Monthly Views</p>
                        <p className="font-semibold text-slate-200">{(r.monthly_views / 1000).toFixed(1)}K</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 text-sm justify-between">
                      <span className={`px-2 py-1 rounded-md text-xs font-semibold ${
                        r.dns_dead 
                          ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' 
                          : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                        }`}>
                        {r.dns_dead ? 'DNS DEAD' : 'DNS ALIVE'}
                      </span>
                      <span className="text-slate-500 text-xs font-mono">{r.domain_age} YRS OLD</span>
                    </div>
                  </a>
                ))}
              </div>
            </div>
          )}

          {(!loading && results.length === 0 && !error) && (
            <div className="text-center py-20 opacity-50">
               <span className="text-6xl mb-4 block">🔍</span>
               <p className="text-slate-400">Run a search to find your first dead domain.</p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
