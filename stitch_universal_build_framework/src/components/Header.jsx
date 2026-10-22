import React from 'react';
import { useInvestigation } from '../context/InvestigationContext';
import { Search, AlertTriangle, RefreshCw, Bell } from 'lucide-react';

export const Header = () => {
  const {
    summary,
    sanctions,
    refreshGraphAndSummary,
    refreshFindings,
    isLoadingGraph,
    setActiveTab,
  } = useInvestigation();

  const handleRefresh = async () => {
    await refreshGraphAndSummary();
    await refreshFindings();
  };

  return (
    <header className="fixed top-0 left-[300px] right-0 h-16 bg-white/90 backdrop-blur-md z-40 flex items-center justify-between px-6 border-b border-gray-200">
      {/* Search Bar / Quick Lookup */}
      <div className="flex items-center bg-gray-50 px-3.5 py-1.5 rounded-full border border-gray-200 w-80 shadow-2xs">
        <Search className="w-4 h-4 text-gray-400 mr-2 shrink-0" />
        <input
          className="bg-transparent border-none focus:ring-0 w-full outline-none placeholder:text-gray-400 font-mono text-xs text-gray-800"
          placeholder="Lookup address or transaction..."
          type="text"
          readOnly
        />
      </div>

      {/* Right Actions & Status Badges */}
      <div className="flex items-center gap-3">
        {/* Live Traced Status */}
        <div className="hidden sm:flex items-center gap-2 bg-gray-100/80 px-3 py-1 rounded-full border border-gray-200/80 shadow-2xs">
          <span className={`w-2 h-2 rounded-full ${summary.wallets_traced > 0 ? 'bg-emerald-500 animate-pulse' : 'bg-gray-400'}`} />
          <span className="text-xs font-mono font-medium text-gray-700">
            {summary.wallets_traced} wallets · {summary.transactions_mapped} txs
          </span>
        </div>

        {/* Sanctions Warning Badge if hits exist */}
        {sanctions && sanctions.length > 0 && (
          <button
            onClick={() => setActiveTab('findings')}
            className="flex items-center gap-1.5 bg-red-50 hover:bg-red-100 text-red-700 px-3 py-1 rounded-full border border-red-200 transition-colors shadow-2xs cursor-pointer active:scale-95"
            title="Click to view sanctioned entities in Findings"
          >
            <AlertTriangle className="w-3.5 h-3.5 text-red-600 shrink-0" />
            <span className="text-xs font-bold tracking-wider uppercase">
              {sanctions.length} Sanctioned Hit{sanctions.length > 1 ? 's' : ''}
            </span>
          </button>
        )}

        {/* Refresh button */}
        <button
          onClick={handleRefresh}
          disabled={isLoadingGraph}
          className="p-2 text-gray-500 hover:text-gray-900 transition-colors rounded-lg hover:bg-gray-100 disabled:opacity-50"
          title="Refresh Graph & Findings"
        >
          <RefreshCw className={`w-4 h-4 ${isLoadingGraph ? 'animate-spin text-primary' : ''}`} />
        </button>

        {/* Notification Bell */}
        <button
          onClick={() => {
            if (sanctions && sanctions.length > 0) {
              setActiveTab('findings');
            }
          }}
          className="relative p-2 text-gray-500 hover:text-gray-900 transition-colors rounded-lg hover:bg-gray-100"
          title={sanctions && sanctions.length > 0 ? `${sanctions.length} sanctions alerts` : 'Notifications'}
        >
          <Bell className="w-4 h-4" />
          {sanctions && sanctions.length > 0 && (
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-600 rounded-full ring-2 ring-white" />
          )}
        </button>
      </div>
    </header>
  );
};
