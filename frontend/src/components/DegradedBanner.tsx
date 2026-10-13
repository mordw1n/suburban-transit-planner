import React from 'react';

interface DegradedBannerProps {
  isDegraded: boolean;
}

export const DegradedBanner: React.FC<DegradedBannerProps> = ({ isDegraded }) => {
  if (!isDegraded) return null;

  return (
    <div className="bg-amber-500/10 border-b border-amber-500/30 px-6 py-3">
      <div className="max-w-7xl mx-auto flex items-center justify-between text-xs text-amber-300">
        <div className="flex items-center gap-2">
          <i className="fa-solid fa-triangle-exclamation text-amber-400 text-sm"></i>
          <span>
            <strong>Режим отказоустойчивости (Graceful Degradation):</strong> Внешний сервис расписаний временно недоступен или превысил квоту. Сервис обслуживает запросы из локального кэша Redis/PostgreSQL.
          </span>
        </div>
        <span className="bg-amber-500/20 px-2 py-0.5 rounded font-mono text-[11px] border border-amber-500/30">
          Circuit Breaker: OPEN
        </span>
      </div>
    </div>
  );
};
