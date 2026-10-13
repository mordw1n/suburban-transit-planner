import { Station, RouteSearchResponse, LiveDelayItem } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export async function fetchStations(): Promise<Station[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/stations`);
    if (!res.ok) throw new Error('Ошибка получения списка станций');
    return await res.json();
  } catch (err) {
    console.warn('API error, falling back to local seed stations:', err);
    return [
      { id: '1', code_yandex: 's9600370', title: 'Финляндский вокзал', direction: 'Финляндское', is_junction: true },
      { id: '2', code_yandex: 's9600371', title: 'Выборг', direction: 'Финляндское', is_junction: false },
      { id: '3', code_yandex: 's9600372', title: 'Зеленогорск', direction: 'Финляндское', is_junction: true },
      { id: '4', code_yandex: 's9600373', title: 'Девяткино', direction: 'Приозерское', is_junction: true },
      { id: '5', code_yandex: 's9600375', title: 'Приозерск', direction: 'Приозерское', is_junction: false },
      { id: '6', code_yandex: 's9600377', title: 'Балтийский вокзал', direction: 'Балтийское', is_junction: true },
      { id: '7', code_yandex: 's9600376', title: 'Гатчина-Балтийская', direction: 'Балтийское', is_junction: false }
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
