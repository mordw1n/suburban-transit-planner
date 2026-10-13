import React, { useState } from 'react';
import { Station } from '../types';

interface SearchFormProps {
  stations: Station[];
  onSearch: (fromCode: string, toCode: string, date: string) => void;
  isLoading: boolean;
}

export const SearchForm: React.FC<SearchFormProps> = ({ stations, onSearch, isLoading }) => {
  const [fromCode, setFromCode] = useState<string>('s9600370');
  const [toCode, setToCode] = useState<string>('s9600371');
  const [date, setDate] = useState<string>(new Date().toISOString().split('T')[0]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (fromCode && toCode) {
      onSearch(fromCode, toCode, date);
    }
  };

  const handleSwap = () => {
    const temp = fromCode;
    setFromCode(toCode);
    setToCode(temp);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl mb-8">
      <h2 className="text-base font-bold text-white mb-4 flex items-center gap-2">
        <i className="fa-solid fa-route text-cyan-400"></i> Поиск пригородных маршрутов и пересадок
      </h2>
      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-12 gap-4 items-end">
        <div className="md:col-span-4">
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
            Откуда
          </label>
          <select
            value={fromCode}
            onChange={(e) => setFromCode(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500"
          >
            {stations.map((s) => (
              <option key={s.code_yandex} value={s.code_yandex}>
                {s.title} ({s.direction})
              </option>
            ))}
          </select>
        </div>

        <div className="md:col-span-1 flex justify-center pb-1">
          <button
            type="button"
            onClick={handleSwap}
            className="w-10 h-10 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition flex items-center justify-center border border-slate-700"
            title="Поменять местами"
          >
            <i className="fa-solid fa-arrow-right-arrow-left"></i>
          </button>
        </div>

        <div className="md:col-span-4">
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
            Куда
          </label>
          <select
            value={toCode}
            onChange={(e) => setToCode(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-cyan-500"
          >
            {stations.map((s) => (
              <option key={s.code_yandex} value={s.code_yandex}>
                {s.title} ({s.direction})
              </option>
            ))}
          </select>
        </div>

        <div className="md:col-span-3 flex gap-2">
          <div className="flex-1">
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">
              Дата
            </label>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500"
            />
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="mt-auto bg-cyan-600 hover:bg-cyan-500 text-white font-semibold py-2.5 px-5 rounded-xl shadow-lg shadow-cyan-600/20 transition flex items-center justify-center gap-2"
          >
            {isLoading ? <i className="fa-solid fa-spinner animate-spin"></i> : <i className="fa-solid fa-magnifying-glass"></i>}
            <span>Найти</span>
          </button>
        </div>
      </form>
    </div>
  );
};
