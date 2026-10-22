import React from 'react';
import { useInvestigation } from '../context/InvestigationContext';
import { AlertCircle, CheckCircle, AlertTriangle, Info, X } from 'lucide-react';

export const ToastContainer = () => {
  const { toasts, removeToast } = useInvestigation();

  if (!toasts.length) return null;

  return (
    <div className="fixed bottom-6 right-6 z-[9999] flex flex-col gap-2 max-w-md w-full pointer-events-none">
      {toasts.map((toast) => {
        const isError = toast.type === 'error';
        const isSuccess = toast.type === 'success';
        const isWarning = toast.type === 'warning';

        return (
          <div
            key={toast.id}
            className={`pointer-events-auto flex items-start gap-3 p-4 rounded-xl shadow-xl border backdrop-blur-md transition-all transform translate-y-0 animate-in slide-in-from-bottom-5 duration-200 ${
              isError
                ? 'bg-[#ffebee] border-error/40 text-error shadow-error/10'
                : isSuccess
                ? 'bg-[#e8f5e9] border-[#4C8C4A]/40 text-[#2e682c] shadow-[#4C8C4A]/10'
                : isWarning
                ? 'bg-[#fff3e0] border-[#FF6D1F]/40 text-[#9c400d] shadow-[#FF6D1F]/10'
                : 'bg-surface-container border-outline-variant text-on-surface'
            }`}
          >
            <span className="shrink-0 mt-0.5">
              {isError ? (
                <AlertCircle className="w-5 h-5 text-red-600" />
              ) : isSuccess ? (
                <CheckCircle className="w-5 h-5 text-emerald-600" />
              ) : isWarning ? (
                <AlertTriangle className="w-5 h-5 text-amber-600" />
              ) : (
                <Info className="w-5 h-5 text-blue-600" />
              )}
            </span>
            <div className="flex-1 text-sm font-medium leading-snug break-words">
              {toast.message}
            </div>
            <button
              onClick={() => removeToast(toast.id)}
              className="text-on-surface-variant hover:text-on-surface opacity-60 hover:opacity-100 transition-opacity shrink-0"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        );
      })}
    </div>
  );
};
