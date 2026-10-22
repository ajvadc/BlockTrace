import React from 'react';
import { useInvestigation } from '../context/InvestigationContext';
import { loadCuratedCase } from '../api/client';

export const LandingScreen = () => {
  const {
    setActiveTab,
    curatedCases,
    refreshGraphAndSummary,
    refreshFindings,
    showToast,
    setActionLoading,
  } = useInvestigation();

  const handleOpenCuratedCase = async (caseName) => {
    setActionLoading(true);
    try {
      showToast(`Loading case: ${caseName}...`, 'info');
      await loadCuratedCase(caseName);
      await refreshGraphAndSummary();
      await refreshFindings();
      showToast(`Successfully loaded ${caseName}`, 'success');
      setActiveTab('investigate');
    } catch (err) {
      console.error(err);
      showToast('Failed to load curated case', 'error');
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="w-full min-h-screen bg-surface font-body-md text-on-surface">
      {/* Top Header */}
      <header className="fixed top-0 w-full z-50 bg-surface/90 backdrop-blur-md shadow-xs border-b border-outline-variant/40">
        <div className="h-20 max-w-7xl mx-auto px-lg flex items-center justify-between">
          <div className="flex items-center gap-md cursor-pointer" onClick={() => setActiveTab('landing')}>
            <div className="w-9 h-9 rounded-lg bg-primary flex items-center justify-center text-white shadow-md">
              <span className="material-symbols-outlined text-[22px]">hub</span>
            </div>
            <span className="font-headline-md text-headline-md text-on-surface tracking-tight uppercase font-bold">
              BlockTrace
            </span>
          </div>

          <nav className="hidden md:flex items-center gap-xl text-sm font-semibold">
            <a href="#solution" className="text-on-surface-variant hover:text-on-surface transition-colors">
              Solution
            </a>
            <a href="#how-it-works" className="text-on-surface-variant hover:text-on-surface transition-colors">
              How It Works
            </a>
            <a href="#comparison" className="text-on-surface-variant hover:text-on-surface transition-colors">
              Why Us
            </a>
            <a href="#technology" className="text-on-surface-variant hover:text-on-surface transition-colors">
              Technology
            </a>
            <a href="#verified-cases" className="text-on-surface-variant hover:text-on-surface transition-colors">
              Real Cases
            </a>
          </nav>

          <div className="flex items-center gap-md">
            <button
              onClick={() => setActiveTab('investigate')}
              className="bg-primary text-on-primary text-xs px-5 py-2.5 rounded-lg uppercase tracking-wider font-bold transition-all hover:bg-primary/90 shadow-md active:scale-95 flex items-center gap-1.5"
            >
              <span>Launch App</span>
              <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative z-10 w-full flex flex-col items-center justify-center px-lg py-20 pt-36 overflow-hidden bg-gradient-to-b from-surface via-surface-container-low to-surface">
        <div className="max-w-4xl mx-auto text-center flex flex-col items-center gap-6 relative z-10">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-blue-50 text-blue-700 rounded-full border border-blue-200/80 shadow-xs">
            <span className="material-symbols-outlined text-[18px]">verified</span>
            <span className="text-xs tracking-wider uppercase font-bold">
              Cryptographically Verifiable Blockchain Forensics
            </span>
          </div>

          <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-on-surface max-w-3xl leading-tight">
            Trace crypto crime.{' '}
            <span className="text-primary block sm:inline">Verify every finding.</span>
          </h1>

          <p className="text-base md:text-lg text-on-surface-variant max-w-2xl mx-auto leading-relaxed">
            BlockTrace investigates cryptocurrency wallets, flags suspicious laundering patterns with transparent reasoning, and issues cryptographic proof that its findings cannot be silently altered.
          </p>

          <div className="flex flex-col sm:flex-row items-center gap-4 mt-4">
            <button
              onClick={() => setActiveTab('investigate')}
              className="w-full sm:w-auto bg-primary text-white text-xs px-8 py-3.5 rounded-xl uppercase tracking-wider transition-all hover:bg-primary/90 shadow-lg active:scale-95 flex items-center justify-center gap-2 font-bold"
            >
              <span>Launch Investigator</span>
              <span className="material-symbols-outlined text-[18px]">arrow_forward</span>
            </button>
            <a
              href="#verified-cases"
              className="w-full sm:w-auto bg-surface border-2 border-outline-variant text-on-surface text-xs px-8 py-3 rounded-xl uppercase tracking-wider transition-all hover:bg-surface-container flex items-center justify-center gap-2 font-bold"
            >
              <span>Explore Example Cases</span>
            </a>
          </div>
        </div>
      </section>

      {/* ==================== SCREENSHOT 3: Our Solution: Trace It, Explain It, Prove It ==================== */}
      <section id="solution" className="w-full py-20 px-lg bg-white border-t border-outline-variant/40">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-extrabold text-[#111827] mb-10 tracking-tight">
            Our Solution: Trace It, Explain It, Prove It
          </h2>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
            {/* Left Column: Solution Snapshot & Problem-to-Answer Table */}
            <div className="flex flex-col gap-6">
              {/* Solution Snapshot Card */}
              <div className="bg-[#f0f7ff] border border-[#bae0ff] rounded-2xl p-6 md:p-8 shadow-xs">
                <span className="text-[11px] font-extrabold tracking-widest text-[#0958d9] uppercase block mb-3">
                  Solution Snapshot
                </span>
                <p className="text-sm md:text-base text-[#1f2937] leading-relaxed font-normal">
                  BlockTrace is an open, explainable blockchain investigation platform. Give it a wallet; it pulls live data, builds a graph of the money flow, flags suspicious behaviour with five readable rules, screens against sanctions, and seals the findings in a certificate anyone can re-verify.
                </p>
              </div>

              {/* Problem -> Our Answer Table */}
              <div className="flex flex-col gap-3">
                <span className="text-[11px] font-extrabold tracking-widest text-[#059669] uppercase mb-1">
                  Problem &rarr; Our Answer
                </span>

                <div className="flex items-center gap-3">
                  <div className="flex-1 py-3 px-4 bg-[#fff1f0] border border-[#ffccc7] text-[#cf1322] rounded-xl text-xs md:text-sm font-semibold text-center">
                    Slow manual tracing
                  </div>
                  <span className="text-gray-400 font-bold">&rarr;</span>
                  <div className="flex-1 py-3 px-4 bg-[#f6ffed] border border-[#b7eb8f] text-[#389e0d] rounded-xl text-xs md:text-sm font-semibold text-center">
                    Automated multi-hop trail (BFS)
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div className="flex-1 py-3 px-4 bg-[#fff1f0] border border-[#ffccc7] text-[#cf1322] rounded-xl text-xs md:text-sm font-semibold text-center">
                    Black-box scores
                  </div>
                  <span className="text-gray-400 font-bold">&rarr;</span>
                  <div className="flex-1 py-3 px-4 bg-[#f6ffed] border border-[#b7eb8f] text-[#389e0d] rounded-xl text-xs md:text-sm font-semibold text-center">
                    Five explainable heuristics
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div className="flex-1 py-3 px-4 bg-[#fff1f0] border border-[#ffccc7] text-[#cf1322] rounded-xl text-xs md:text-sm font-semibold text-center">
                    Unverifiable results
                  </div>
                  <span className="text-gray-400 font-bold">&rarr;</span>
                  <div className="flex-1 py-3 px-4 bg-[#f6ffed] border border-[#b7eb8f] text-[#389e0d] rounded-xl text-xs md:text-sm font-semibold text-center">
                    SHA-256 hash-chained certificates
                  </div>
                </div>
              </div>
            </div>

            {/* Right Column: Target Users, Value Badges, and Use Case */}
            <div className="flex flex-col gap-4">
              <span className="text-[11px] font-extrabold tracking-widest text-[#722ed1] uppercase mb-1">
                Target Users
              </span>

              {/* Card 1: Primary - Investigators */}
              <div className="bg-[#fafafa] border border-[#f0f0f0] rounded-2xl p-5 hover:border-[#d9d9d9] transition-all">
                <span className="text-[10px] font-bold text-[#1677ff] tracking-wider uppercase block mb-1">
                  Primary
                </span>
                <h4 className="text-sm md:text-base font-bold text-[#111827] mb-1">
                  Investigators & forensic analysts
                </h4>
                <p className="text-xs md:text-sm text-[#4b5563] leading-relaxed">
                  Get a first-pass, explainable read on a wallet's trail in minutes instead of hours.
                </p>
              </div>

              {/* Card 2: Primary - Compliance & Risk */}
              <div className="bg-[#fafafa] border border-[#f0f0f0] rounded-2xl p-5 hover:border-[#d9d9d9] transition-all">
                <span className="text-[10px] font-bold text-[#1677ff] tracking-wider uppercase block mb-1">
                  Primary
                </span>
                <h4 className="text-sm md:text-base font-bold text-[#111827] mb-1">
                  Compliance & risk teams
                </h4>
                <p className="text-xs md:text-sm text-[#4b5563] leading-relaxed">
                  Screen addresses against sanctions data and keep a verifiable audit record.
                </p>
              </div>

              {/* Card 3: Secondary - Researchers & Students */}
              <div className="bg-[#fafafa] border border-[#f0f0f0] rounded-2xl p-5 hover:border-[#d9d9d9] transition-all">
                <span className="text-[10px] font-bold text-[#6b7280] tracking-wider uppercase block mb-1">
                  Secondary
                </span>
                <h4 className="text-sm md:text-base font-bold text-[#111827] mb-1">
                  Researchers, students & small organisations
                </h4>
                <p className="text-xs md:text-sm text-[#4b5563] leading-relaxed">
                  Use a free, transparent alternative to closed enterprise platforms.
                </p>
              </div>

              {/* Value Badges Row */}
              <div className="flex items-center gap-3 mt-2">
                {['Faster', 'Explainable', 'Verifiable', 'Open'].map((badge) => (
                  <div
                    key={badge}
                    className="flex-1 py-2 text-center rounded-xl bg-[#e6f4ff] border border-[#91caff] text-[#0958d9] text-xs font-bold shadow-2xs"
                  >
                    {badge}
                  </div>
                ))}
              </div>

              {/* Use Case Note */}
              <p className="text-xs text-[#6b7280] italic mt-1 leading-relaxed">
                Use case: paste the Ronin Bridge hacker wallet &rarr; follow the funds across hops &rarr; see peel chains and fan-out flagged &rarr; export a sealed PDF report.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ==================== SCREENSHOT 1: How It Works: From Wallet Address to Sealed Evidence ==================== */}
      <section id="how-it-works" className="w-full py-20 px-lg bg-[#fcfcfd] border-t border-outline-variant/40">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-extrabold text-[#111827] mb-10 tracking-tight">
            How It Works: From Wallet Address to Sealed Evidence
          </h2>

          {/* Top 7 Steps Row */}
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 mb-10">
            {[
              {
                num: 1,
                title: 'Ingest',
                desc: 'Live data from Etherscan API v2',
                highlight: false,
              },
              {
                num: 2,
                title: 'Graph',
                desc: 'Wallets as nodes, SENT edges in Neo4j',
                highlight: false,
              },
              {
                num: 3,
                title: 'Multi-hop',
                desc: 'Breadth-first expansion of the trail',
                highlight: false,
              },
              {
                num: 4,
                title: 'Detect',
                desc: 'Five explainable heuristics',
                highlight: false,
              },
              {
                num: 5,
                title: 'Score',
                desc: 'Low · Medium · High by overlapping signals',
                highlight: false,
              },
              {
                num: 6,
                title: 'Screen',
                desc: 'Match against sanctions (OFAC SDN)',
                highlight: true,
              },
              {
                num: 7,
                title: 'Certify',
                desc: 'PDF report + SHA-256 hash-chained certificate',
                highlight: true,
              },
            ].map((step) => (
              <div
                key={step.num}
                className={`p-4 rounded-2xl border flex flex-col justify-start transition-all shadow-2xs ${
                  step.highlight
                    ? 'bg-[#f6ffed] border-[#b7eb8f]'
                    : 'bg-white border-[#e5e7eb]'
                }`}
              >
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-extrabold mb-3 text-white ${
                    step.highlight ? 'bg-[#389e0d]' : 'bg-[#4b5563]'
                  }`}
                >
                  {step.num}
                </div>
                <h4 className="text-sm font-bold text-[#111827] mb-1">{step.title}</h4>
                <p className="text-[11px] text-[#4b5563] leading-relaxed">{step.desc}</p>
              </div>
            ))}
          </div>

          {/* Middle: THE FIVE HEURISTICS */}
          <div className="mb-8">
            <span className="text-[11px] font-extrabold tracking-widest text-[#722ed1] uppercase block mb-3">
              The Five Heuristics
            </span>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
              {[
                { name: 'Hub activity', desc: 'High in/out degree' },
                { name: 'Fan-out', desc: 'Rapid 1-to-N splits' },
                { name: 'Peel chains', desc: 'Incremental small drops' },
                { name: 'Round numbers', desc: 'Exact integer amounts' },
                { name: 'Circular flows', desc: 'A &rarr; B &rarr; C &rarr; A loops' },
              ].map((h) => (
                <div
                  key={h.name}
                  className="bg-[#f9f0ff] border border-[#d3adf7] rounded-xl p-4 shadow-2xs"
                >
                  <h4 className="text-xs font-bold text-[#111827] mb-1">{h.name}</h4>
                  <p
                    className="text-[11px] text-[#4b5563]"
                    dangerouslySetInnerHTML={{ __html: h.desc }}
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Bottom Summary Callout Box */}
          <div className="bg-[#e6f4ff] border border-[#91caff] rounded-xl p-4 text-xs md:text-sm text-[#1f2937] leading-relaxed shadow-2xs">
            <span className="font-bold text-[#0958d9]">Input &rarr;</span> wallet address + hop limit.&nbsp;&nbsp;
            <span className="font-bold text-[#0958d9]">Output &rarr;</span> interactive graph, plain-English findings, sanctions flags, PDF report, JSON certificate.&nbsp;&nbsp;
            <span className="font-bold text-[#0958d9]">Loop &rarr;</span> anyone can re-verify the certificate later.
          </div>
        </div>
      </section>

      {/* ==================== SCREENSHOT 2: What Makes BlockTrace Different ==================== */}
      <section id="comparison" className="w-full py-20 px-lg bg-white border-t border-outline-variant/40">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-extrabold text-[#111827] mb-10 tracking-tight">
            What Makes BlockTrace Different
          </h2>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* Left 8 Cols: Comparison Table */}
            <div className="lg:col-span-8 flex flex-col gap-4">
              <div className="overflow-x-auto rounded-xl border border-[#e5e7eb] shadow-xs">
                <table className="w-full text-left text-xs md:text-sm border-collapse">
                  <thead>
                    <tr>
                      <th className="py-3.5 px-4 bg-[#111827] text-white font-bold w-1/4">Feature</th>
                      <th className="py-3.5 px-4 bg-[#374151] text-white font-bold w-1/4">Commercial black-box tools</th>
                      <th className="py-3.5 px-4 bg-[#4b5563] text-white font-bold w-1/4">Manual explorer tracing</th>
                      <th className="py-3.5 px-4 bg-[#1677ff] text-white font-extrabold w-1/4">BlockTrace</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#e5e7eb]">
                    <tr className="hover:bg-gray-50/50">
                      <td className="py-3 px-4 font-bold text-[#111827]">Access</td>
                      <td className="py-3 px-4 text-[#4b5563]">Closed, costly</td>
                      <td className="py-3 px-4 text-[#4b5563]">Open</td>
                      <td className="py-3 px-4 font-bold text-[#0958d9] bg-[#f0f7ff]/50">Open source</td>
                    </tr>
                    <tr className="hover:bg-gray-50/50">
                      <td className="py-3 px-4 font-bold text-[#111827]">Explainability</td>
                      <td className="py-3 px-4 text-[#4b5563]">No &mdash; probability scores</td>
                      <td className="py-3 px-4 text-[#4b5563]">Limited</td>
                      <td className="py-3 px-4 font-bold text-[#0958d9] bg-[#f0f7ff]/50">Yes &mdash; 5 readable rules</td>
                    </tr>
                    <tr className="hover:bg-gray-50/50">
                      <td className="py-3 px-4 font-bold text-[#111827]">Independent verification</td>
                      <td className="py-3 px-4 text-[#4b5563]">No</td>
                      <td className="py-3 px-4 text-[#4b5563]">No</td>
                      <td className="py-3 px-4 font-bold text-[#0958d9] bg-[#f0f7ff]/50">Yes &mdash; SHA-256 certificates</td>
                    </tr>
                    <tr className="hover:bg-gray-50/50">
                      <td className="py-3 px-4 font-bold text-[#111827]">Speed</td>
                      <td className="py-3 px-4 text-[#4b5563]">Fast</td>
                      <td className="py-3 px-4 text-[#4b5563]">Slow, breaks past ~2 hops</td>
                      <td className="py-3 px-4 font-bold text-[#0958d9] bg-[#f0f7ff]/50">Fast &mdash; automated multi-hop</td>
                    </tr>
                    <tr className="hover:bg-gray-50/50">
                      <td className="py-3 px-4 font-bold text-[#111827]">Chains</td>
                      <td className="py-3 px-4 text-[#4b5563]">Varies</td>
                      <td className="py-3 px-4 text-[#4b5563]">One explorer per chain</td>
                      <td className="py-3 px-4 font-bold text-[#0958d9] bg-[#f0f7ff]/50">Ethereum, BSC, Polygon</td>
                    </tr>
                    <tr className="hover:bg-gray-50/50">
                      <td className="py-3 px-4 font-bold text-[#111827]">Language of findings</td>
                      <td className="py-3 px-4 text-[#4b5563]">Risk scores</td>
                      <td className="py-3 px-4 text-[#4b5563]">Analyst's own notes</td>
                      <td className="py-3 px-4 font-bold text-[#0958d9] bg-[#f0f7ff]/50">Hedged indicators, never verdicts</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {/* Novelty Callout */}
              <p className="text-xs md:text-sm font-bold text-[#1677ff] leading-relaxed mt-2">
                Novelty: open forensics + explainable detection + tamper-evident, independently verifiable evidence in a single tool.
              </p>
            </div>

            {/* Right 4 Cols: UNFAIR ADVANTAGES */}
            <div className="lg:col-span-4 flex flex-col gap-3">
              <span className="text-[11px] font-extrabold tracking-widest text-[#722ed1] uppercase mb-1">
                Unfair Advantages
              </span>

              <div className="bg-[#fafafa] border border-[#f0f0f0] rounded-xl p-4 shadow-2xs">
                <h4 className="text-xs font-bold text-[#111827] mb-1">Zero-trust certificates</h4>
                <p className="text-[11px] text-[#4b5563] leading-relaxed">
                  Re-verify any finding locally with SHA-256 &mdash; no server, no database.
                </p>
              </div>

              <div className="bg-[#fafafa] border border-[#f0f0f0] rounded-xl p-4 shadow-2xs">
                <h4 className="text-xs font-bold text-[#111827] mb-1">No black box</h4>
                <p className="text-[11px] text-[#4b5563] leading-relaxed">
                  Every flag maps to a rule a judge can read.
                </p>
              </div>

              <div className="bg-[#fafafa] border border-[#f0f0f0] rounded-xl p-4 shadow-2xs">
                <h4 className="text-xs font-bold text-[#111827] mb-1">Sanctions done carefully</h4>
                <p className="text-[11px] text-[#4b5563] leading-relaxed">
                  Small, manually verified list to avoid stale-data false positives.
                </p>
              </div>

              <div className="bg-[#fafafa] border border-[#f0f0f0] rounded-xl p-4 shadow-2xs">
                <h4 className="text-xs font-bold text-[#111827] mb-1">Quality built in</h4>
                <p className="text-[11px] text-[#4b5563] leading-relaxed">
                  51/51 tests, incl. a test that rejects accusatory wording and verifies dual database engines.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ==================== SCREENSHOT 4: Technology Behind BlockTrace ==================== */}
      <section id="technology" className="w-full py-20 px-lg bg-[#fcfcfd] border-t border-outline-variant/40">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-extrabold text-[#111827] mb-10 tracking-tight">
            Technology Behind BlockTrace
          </h2>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            {/* Left 7 Cols: System Architecture Graphic */}
            <div className="lg:col-span-7 flex flex-col gap-2">
              <div className="bg-[#1a1a1a] rounded-2xl p-6 text-white border border-gray-800 shadow-xl overflow-hidden">
                {/* Title inside card */}
                <div className="text-center mb-6">
                  <h3 className="text-lg font-bold text-white tracking-wide">
                    <span className="text-[#ff6d1f]">BlockTrace</span> System Architecture
                  </h3>
                </div>

                {/* Top Data Source */}
                <div className="flex justify-center mb-6">
                  <div className="border border-[#ff6d1f]/60 bg-[#262626] rounded-xl p-3 px-5 flex items-center gap-3 shadow-md">
                    <div className="w-8 h-8 rounded-lg bg-[#ff6d1f] flex items-center justify-center font-bold text-xs text-white">
                      EVM
                    </div>
                    <div>
                      <div className="text-xs font-bold text-white flex items-center gap-2">
                        Etherscan API v2
                        <span className="bg-[#ff6d1f]/20 text-[#ff6d1f] text-[9px] px-1.5 py-0.5 rounded uppercase font-semibold">
                          Live Data
                        </span>
                      </div>
                      <div className="text-[10px] text-gray-400">Ethereum · BNB Smart Chain · Polygon (via chainid)</div>
                    </div>
                  </div>
                </div>

                {/* Main 5 Layers Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-center mb-4">
                  {/* Layer 1: Client */}
                  <div className="border border-gray-700 bg-[#222222] rounded-xl p-3 flex flex-col items-center">
                    <span className="text-[9px] uppercase tracking-wider text-gray-400 font-bold mb-1">Client Layer</span>
                    <div className="text-xs font-bold text-[#1677ff] mb-2 flex items-center gap-1">
                      <span className="material-symbols-outlined text-[14px]">devices</span>
                      React Frontend
                    </div>
                    <div className="text-[9px] text-gray-400 space-y-1 text-left w-full pl-2">
                      <div>• Investigate</div>
                      <div>• Findings</div>
                      <div>• Certificates</div>
                      <div>• Cases & Reports</div>
                      <div>• Homepage</div>
                    </div>
                  </div>

                  {/* Layer 2: API */}
                  <div className="border border-gray-700 bg-[#222222] rounded-xl p-3 flex flex-col items-center">
                    <span className="text-[9px] uppercase tracking-wider text-gray-400 font-bold mb-1">API Layer</span>
                    <div className="text-xs font-bold text-emerald-400 mb-2 flex items-center gap-1">
                      <span className="material-symbols-outlined text-[14px]">bolt</span>
                      FastAPI
                    </div>
                    <div className="text-[9px] text-gray-400 space-y-1 text-left w-full pl-2">
                      <div>• ~25 REST routes</div>
                      <div>• CORS Dev/Prod</div>
                      <div>• Multi-chain params</div>
                      <div>• Safe error wraps</div>
                    </div>
                  </div>

                  {/* Layer 3: Logic */}
                  <div className="border border-gray-700 bg-[#222222] rounded-xl p-3 flex flex-col items-center">
                    <span className="text-[9px] uppercase tracking-wider text-gray-400 font-bold mb-1">Logic Layer</span>
                    <div className="text-xs font-bold text-[#ff6d1f] mb-2 flex items-center gap-1">
                      <span className="material-symbols-outlined text-[14px]">psychology</span>
                      logic.py
                    </div>
                    <div className="text-[9px] text-gray-400 space-y-1 text-left w-full pl-2">
                      <div>• Risk Scoring</div>
                      <div>• Narrative Engine</div>
                      <div>• Sanctions Match</div>
                      <div>• Certificate Hash</div>
                    </div>
                  </div>

                  {/* Layer 4: Data Layer */}
                  <div className="border border-gray-700 bg-[#222222] rounded-xl p-3 flex flex-col items-center">
                    <span className="text-[9px] uppercase tracking-wider text-gray-400 font-bold mb-1">Data Layer</span>
                    <div className="text-xs font-bold text-cyan-400 mb-2 flex items-center gap-1">
                      <span className="material-symbols-outlined text-[14px]">database</span>
                      Neo4j / SQLite
                    </div>
                    <div className="text-[9px] text-gray-400 space-y-1 text-left w-full pl-2">
                      <div>• Wallet nodes</div>
                      <div>• SENT transactions</div>
                      <div>• Auto-detection</div>
                      <div>• Zero-config fallback</div>
                    </div>
                  </div>
                </div>

                {/* Bottom Output Artifacts */}
                <div className="flex justify-center gap-4 pt-2 border-t border-gray-800">
                  <div className="flex items-center gap-2 bg-red-950/40 border border-red-700/50 px-3 py-1.5 rounded-lg text-[10px] text-red-200">
                    <span className="material-symbols-outlined text-[14px] text-red-400">picture_as_pdf</span>
                    <span>PDF Forensic Report (ReportLab)</span>
                  </div>
                  <div className="flex items-center gap-2 bg-blue-950/40 border border-blue-700/50 px-3 py-1.5 rounded-lg text-[10px] text-blue-200">
                    <span className="material-symbols-outlined text-[14px] text-blue-400">verified</span>
                    <span>JSON Proof Certificate (SHA-256)</span>
                  </div>
                </div>
              </div>

              <p className="text-xs text-gray-500 italic text-center">
                System architecture &mdash; five layers fed by live Etherscan data with Neo4j and embedded SQLite engine
              </p>
            </div>

            {/* Right 5 Cols: Tech Stack Specifications & Security */}
            <div className="lg:col-span-5 flex flex-col gap-6">
              {/* Stack Specs Table */}
              <div className="bg-white border border-[#e5e7eb] rounded-2xl p-5 shadow-xs">
                <div className="space-y-3 text-xs md:text-sm">
                  <div className="flex items-center justify-between pb-2 border-b border-gray-100">
                    <span className="text-gray-400 font-bold uppercase text-[11px] tracking-wider">Frontend</span>
                    <span className="font-semibold text-gray-900">React · Vite · Tailwind</span>
                  </div>
                  <div className="flex items-center justify-between pb-2 border-b border-gray-100">
                    <span className="text-gray-400 font-bold uppercase text-[11px] tracking-wider">Backend</span>
                    <span className="font-semibold text-gray-900">FastAPI · Python 3.11+</span>
                  </div>
                  <div className="flex items-center justify-between pb-2 border-b border-gray-100">
                    <span className="text-gray-400 font-bold uppercase text-[11px] tracking-wider">Database</span>
                    <span className="font-semibold text-gray-900">Neo4j (Cypher) + SQLite</span>
                  </div>
                  <div className="flex items-center justify-between pb-2 border-b border-gray-100">
                    <span className="text-gray-400 font-bold uppercase text-[11px] tracking-wider">Data</span>
                    <span className="font-semibold text-gray-900">Etherscan API v2 (ETH · BSC · Polygon)</span>
                  </div>
                  <div className="flex items-center justify-between pb-2 border-b border-gray-100">
                    <span className="text-gray-400 font-bold uppercase text-[11px] tracking-wider">Reports</span>
                    <span className="font-semibold text-gray-900">ReportLab (PDF) · JSON Certificate</span>
                  </div>
                  <div className="flex items-center justify-between pb-2 border-b border-gray-100">
                    <span className="text-gray-400 font-bold uppercase text-[11px] tracking-wider">Testing</span>
                    <span className="font-semibold text-emerald-600">pytest — 51/51 passing</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-400 font-bold uppercase text-[11px] tracking-wider">Deploy</span>
                    <span className="font-semibold text-gray-900">Local / Uvicorn Server</span>
                  </div>
                </div>
              </div>

              {/* Reliability & Security Card */}
              <div className="bg-[#f0fdf4] border border-[#bbf7d0] rounded-2xl p-5 shadow-xs">
                <span className="text-[11px] font-extrabold tracking-widest text-[#15803d] uppercase block mb-3">
                  Reliability & Security
                </span>
                <ul className="space-y-2 text-xs md:text-sm text-[#166534]">
                  <li className="flex items-start gap-2">
                    <span className="text-[#15803d] font-bold">•</span>
                    <span>Idempotent MERGE writes &mdash; no duplicate nodes in graph</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[#15803d] font-bold">•</span>
                    <span>Invalid, negative, and &gt;1M ETH sanity bounds enforced</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[#15803d] font-bold">•</span>
                    <span>Public on-chain data only; zero personal information stored</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-[#15803d] font-bold">•</span>
                    <span>Certificates verifiable offline via standard SHA-256</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ==================== Verified Cases Showcase ==================== */}
      <section id="verified-cases" className="w-full py-20 px-lg bg-white border-t border-outline-variant/40">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-14">
            <span className="text-xs uppercase tracking-widest text-primary font-bold">
              Real-World Evidence
            </span>
            <h2 className="text-3xl font-bold text-on-surface mt-2 tracking-tight">
              Tested Against Documented Incidents
            </h2>
            <p className="text-sm text-gray-500 mt-2">
              Launch pre-verified investigations into historic DeFi and cross-chain bridge exploits.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {(curatedCases.length > 0
              ? curatedCases
              : [
                  {
                    name: 'Ronin Bridge Hack ($600M, 2022)',
                    address: '0x098B716B8Aaf21512996dC57EB0615e2383E2f96',
                    description: 'Wallet linked to the Axie Infinity / Ronin Bridge exploit. Sanctioned by OFAC and attributed to Lazarus Group.',
                  },
                  {
                    name: 'Poly Network Hack ($611M, 2021)',
                    address: '0xC8a65Fadf0e0dDAf421F28FEAb69Bf6E2E589963',
                    description: 'DeFi exploit draining assets across Ethereum, BSC, and Polygon with extensive cross-chain movement.',
                  },
                  {
                    name: 'Wormhole Bridge Hack ($321M, 2022)',
                    address: '0x629e7Da20197a5429d30da36E77D06CdF796b71a',
                    description: 'Exploit of the Ethereum-Solana bridge directly labeled Wormhole Exploiter on Etherscan.',
                  },
                ]
            ).map((c) => (
              <div
                key={c.name}
                className="bg-[#fafafa] p-6 rounded-2xl border border-[#e5e7eb] flex flex-col justify-between shadow-xs hover:border-primary transition-all"
              >
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <span className="material-symbols-outlined text-primary text-[20px]">folder</span>
                    <h3 className="text-base font-bold text-[#111827]">{c.name}</h3>
                  </div>
                  <p className="text-xs text-gray-600 mb-4 leading-relaxed line-clamp-3">
                    {c.description}
                  </p>
                  <div className="p-2.5 bg-white rounded-lg text-[11px] text-gray-700 font-mono mb-4 break-all border border-gray-200 shadow-2xs">
                    {c.address}
                  </div>
                </div>

                <button
                  onClick={() => handleOpenCuratedCase(c.name)}
                  className="w-full py-2.5 px-4 bg-primary text-white text-xs uppercase rounded-xl hover:bg-primary/90 transition-colors font-bold flex items-center justify-center gap-1.5 shadow-sm active:scale-95"
                >
                  <span>Launch Investigation</span>
                  <span className="material-symbols-outlined text-[16px]">arrow_forward</span>
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Bottom CTA & Footer */}
      <section className="w-full bg-[#111827] text-white py-16 px-lg">
        <div className="max-w-7xl mx-auto flex flex-col items-center text-center gap-6">
          <h2 className="text-3xl font-extrabold tracking-tight">Start an Investigation in Seconds</h2>
          <p className="text-gray-400 max-w-xl text-sm leading-relaxed">
            Directly connect to blockchain nodes, visualize laundering topologies, and generate immutable cryptographic proof of findings.
          </p>
          <button
            onClick={() => setActiveTab('investigate')}
            className="bg-primary text-white text-xs uppercase px-8 py-3.5 rounded-xl font-bold tracking-wider hover:bg-primary/90 transition-all shadow-lg active:scale-95 flex items-center gap-2"
          >
            <span>Open Investigator Console</span>
            <span className="material-symbols-outlined text-[18px]">launch</span>
          </button>
          <div className="pt-8 border-t border-gray-800 w-full flex flex-col sm:flex-row items-center justify-between text-xs text-gray-400 gap-4">
            <span>© 2026 BlockTrace Forensics. All rights reserved.</span>
            <span className="italic text-gray-400">
              Note: Detection results are heuristic indicators, not definitive proof of wrongdoing.
            </span>
          </div>
        </div>
      </section>
    </div>
  );
};
