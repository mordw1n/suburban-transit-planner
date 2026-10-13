import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { DegradedBanner } from './components/DegradedBanner';
import { SearchForm } from './components/SearchForm';
import { RouteCard } from './components/RouteCard';
import { StationBoard } from './components/StationBoard';
import { fetchStations, searchRoutes, fetchLiveDelays } from './api/client';
import { Station, RouteOption, LiveDelayItem } from './types';

export const App: React.FC = () => {
  const [stations, setStations] = useState<Station[]>([]);
  const [routes, setRoutes] = useState<RouteOption[]>([]);
  const [delays, setDelays] = useState<LiveDelayItem[]>([]);
  const [isDegraded, setIsDegraded] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [hasSearched, setHasSearched] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadInitialData() {
      const sts = await fetchStations();
      setStations(sts);
      const dls = await fetchLiveDelays();
      setDelays(dls);

      handleSearch('s9600370', 's9600371', new Date().toISOString().split('T')[0]);
    }
    loadInitialData();
  }, []);

  const handleSearch = async (fromCode: string, toCode: string, date: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await searchRoutes(fromCode, toCode, date);
      setRoutes(res.routes);
      setIsDegraded(res.is_degraded);
      setHasSearched(true);
    } catch (err: any) {
      setError(err.message || 'Ошибка выполнения поиска');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col">
      <Navbar />
      <DegradedBanner isDegraded={isDegraded} />

      <main className="max-w-7xl mx-auto px-6 py-8 flex-1 w-full">
        <StationBoard delays={delays} />

        <SearchForm
          stations={stations}
          onSearch={handleSearch}
          isLoading={isLoading}
        />

        {error && (
          <div className="mb-6 p-4 bg-rose-950/60 border border-rose-800 rounded-xl text-rose-300 text-sm flex items-center gap-2">
            <i className="fa-solid fa-circle-exclamation text-rose-400"></i>
            <span>{error}</span>
          </div>
        )}

        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <i className="fa-solid fa-list-ol text-cyan-400"></i> Варианты маршрутов
              {hasSearched && (
                <span className="text-xs bg-slate-800 text-slate-400 px-2.5 py-0.5 rounded-full font-mono">
                  найдено: {routes.length}
                </span>
              )}
            </h2>
          </div>

          {isLoading ? (
            <div className="py-16 text-center text-slate-500">
              <i className="fa-solid fa-circle-notch fa-spin text-3xl mb-3 text-cyan-400"></i>
              <p className="text-sm">Идет расчет оптимальных стыковок и проверка задержек...</p>
            </div>
          ) : routes.length > 0 ? (
            <div className="space-y-4">
              {routes.map((route) => (
                <RouteCard key={route.option_id} route={route} />
              ))}
            </div>
          ) : hasSearched ? (
            <div className="py-12 bg-slate-900 border border-slate-800 rounded-2xl text-center text-slate-400">
              <i className="fa-solid fa-train-tunnel text-3xl mb-2 text-slate-600"></i>
              <p className="text-sm">По выбранному направлению маршрутов не найдено.</p>
            </div>
          ) : null}
        </div>
      </main>

      <footer className="border-t border-slate-800 py-6 text-center text-xs text-slate-500">
        Курсовой проект КПО | Сервис мультимодального планирования пригородных поездок | СПбПУ 2026
      </footer>
    </div>
  );
};

export default App;
