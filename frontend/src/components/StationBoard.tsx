import React from 'react';
import { LiveDelayItem } from '../types';

interface StationBoardProps {
  delays: LiveDelayItem[];
}

export const StationBoard: React.FC<StationBoardProps> = ({ delays }) => {
  if (!delays.length) return null;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl mb-8">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-bold text-white flex items-center gap-2">
          <i className="fa-solid fa-triangle-exclamation text-amber-400"></i> Оперативное табло отклонений от графика (СПб)
        </h2>
        <span className="text-xs text-slate-400">Автообновление каждые 3 мин</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {delays.map((item, idx) => (
          <div key={idx} className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-bold text-white">{item.train_number}</span>
              <span className="text-xs font-mono text-slate-400">{item.scheduled_time}</span>
            </div>
            <div className="text-xs text-slate-400 mb-3">
              Станция: <strong className="text-slate-200">{item.station_title}</strong>
            </div>
            <div>
              {item.status === 'CANCELLED' ? (
                <div className="px-2.5 py-1 rounded-md text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/30 text-center">
                  Рейс отменен технологическим «окном»
                </div>
              ) : (
                <div className="px-2.5 py-1 rounded-md text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30 text-center">
                  Опоздание на {item.delay_minutes} мин
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
