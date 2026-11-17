import { Station, RouteSearchResponse, LiveDelayItem } from '../types';

const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export async function fetchStations(): Promise<Station[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/stations`);
    if (!res.ok) throw new Error('Ошибка получения списка станций');
    return await res.json();
  } catch (err) {
    console.warn('API error, falling back to local seed stations:', err);
    return [
      { id: 'st-finlyandsky', code_yandex: 's9602497', title: 'Финляндский вокзал', direction: 'Финляндское', is_junction: true },
      { id: 'st-vyborg', code_yandex: 's9603175', title: 'Выборг', direction: 'Финляндское', is_junction: false },
      { id: 'st-zelenogorsk', code_yandex: 's9602725', title: 'Зеленогорск', direction: 'Финляндское', is_junction: true },
      { id: 'st-devyatkino', code_yandex: 's9603876', title: 'Девяткино', direction: 'Приозерское', is_junction: true },
      { id: 'st-priozersk', code_yandex: 's9603177', title: 'Приозерск', direction: 'Приозерское', is_junction: false },
      { id: 'st-baltiysky', code_yandex: 's9602498', title: 'Балтийский вокзал', direction: 'Балтийское', is_junction: true },
      { id: 'st-gatchina', code_yandex: 's9602758', title: 'Гатчина-Балтийская', direction: 'Балтийское', is_junction: false }
    ];
  }
}

export async function searchRoutes(fromCode: string, toCode: string, date: string): Promise<RouteSearchResponse> {
  const url = `${API_BASE_URL}/routes/search?from_code=${encodeURIComponent(fromCode)}&to_code=${encodeURIComponent(toCode)}&date=${encodeURIComponent(date)}`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Ошибка сервера при поиске маршрута: ${res.status}`);
  }
  return await res.json();
}

export async function fetchLiveDelays(): Promise<LiveDelayItem[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/delays/live`);
    if (!res.ok) throw new Error('Ошибка табло сбоев');
    return await res.json();
  } catch (err) {
    return [];
  }
}
