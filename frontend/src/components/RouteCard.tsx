import React from 'react';
import { RouteOption } from '../types';

interface RouteCardProps {
  route: RouteOption;
}

export const RouteCard: React.FC<RouteCardProps> = ({ route }) => {
  const getStatusBadge = (status: string, delay: number) => {
    if (status === 'CANCELLED') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/30">
          <i className="fa-solid fa-ban text-[10px]"></i> Отменен
        </span>
      );
    }
    if (delay > 0 || status === 'DELAYED') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30">
          <i className="fa-solid fa-clock text-[10px]"></i> Задержка +{delay} мин
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
        <i className="fa-solid fa-check text-[10px]"></i> По графику
      </span>
    );
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-md hover:border-slate-700 transition">
      <div className="flex flex-wrap items-center justify-between pb-4 mb-4 border-b border-slate-800 gap-3">
        <div className="flex items-center gap-4">
          <div className="text-2xl font-bold font-mono text-white">
            {route.departure_time}
            <span className="text-slate-500 mx-2 text-base font-normal">→</span>
            {route.arrival_time}
          </div>
          <span className="text-xs bg-slate-800 text-slate-400 px-3 py-1 rounded-full font-mono">
            В пути: {route.total_duration_minutes} мин
          </span>
        </div>

        <div>
          {route.is_direct ? (
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5">
              <i className="fa-solid fa-bolt text-[11px]"></i> Прямой рейс (Без пересадок)
            </span>
          ) : (
            <span className="px-3 py-1 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 flex items-center gap-1.5">
              <i className="fa-solid fa-shuffle text-[11px]"></i> 1 пересадка ({route.transfer?.junction_station_title})
            </span>
          )}
        </div>
      </div>

      <div className="space-y-4">
        {route.segments.map((segment, index) => (
          <div key={index} className="space-y-2">
            <div className="flex items-center justify-between bg-slate-950/60 p-3.5 rounded-xl border border-slate-800/80">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-blue-600/20 text-blue-400 flex items-center justify-center border border-blue-500/30">
                  <i className="fa-solid fa-train text-xs"></i>
                </div>
                <div>
                  <div className="text-sm font-semibold text-white flex items-center gap-2">
                    {segment.train_number}
                    <span className="text-[10px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded">
                      {segment.train_type}
                    </span>
                  </div>
                  <div className="text-xs text-slate-400">
                    {segment.station_from_title} ({segment.departure_time}) → {segment.station_to_title} ({segment.arrival_time})
                  </div>
                </div>
              </div>
              <div>
                {getStatusBadge(segment.status, segment.delay_minutes)}
              </div>
            </div>

            {index === 0 && route.transfer && (
              <div className="my-2 p-3 bg-cyan-950/30 border border-cyan-800/40 rounded-xl flex items-center justify-between text-xs">
                <div className="flex items-center gap-2 text-cyan-300">
                  <i className="fa-solid fa-person-walking text-base text-cyan-400"></i>
                  <span>
                    Пересадка на станции <strong>{route.transfer.junction_station_title}</strong>: ожидание {route.transfer.wait_time_minutes} мин
                    (запас на переход: {route.transfer.walking_buffer_minutes} мин)
                  </span>
                </div>
                {route.transfer.is_tight_connection && (
                  <span className="text-[11px] font-semibold text-rose-400 bg-rose-950/50 px-2 py-0.5 rounded border border-rose-800/50">
                    Короткая пересадка!
                  </span>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
