import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '10s', target: 20 },  // Разгон до 20 пользователей
    { duration: '30s', target: 100 }, // Рабочая пиковая нагрузка (100 одновременных пользователей)
    { duration: '10s', target: 0 },   // Снижение нагрузки
  ],
  thresholds: {
    // 95% запросов должны выполняться быстрее 150мс, 99% - быстрее 300мс
    http_req_duration: ['p(95)<150', 'p(99)<300'],
    // Доля ошибок не должна превышать 1%
    http_req_failed: ['rate<0.01'],
  },
};

const BASE_URL = __ENV.TARGET_URL || 'http://localhost:8000';

const ROUTES = [
  { from: 's9602497', to: 's9602725' }, // Финляндский -> Зеленогорск
  { from: 's9602497', to: 's9603175' }, // Финляндский -> Выборг
  { from: 's9602497', to: 's9603876' }, // Финляндский -> Девяткино
  { from: 's9603876', to: 's9603177' }, // Девяткино -> Приозерск
];

export default function () {
  const route = ROUTES[Math.floor(Math.random() * ROUTES.length)];

  // 1. Поиск маршрутов (основная нагрузка)
  const searchRes = http.get(
    `${BASE_URL}/api/v1/routes/search?from_code=${route.from}&to_code=${route.to}&date=2026-11-26`
  );

  check(searchRes, {
    'search status is 200': (r) => r.status === 200,
    'routes returned': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body.routes_count > 0;
      } catch (e) {
        return false;
      }
    },
    'response time < 200ms': (r) => r.timings.duration < 200,
  });

  // 2. Периодический запрос станций (20% пользователей)
  if (Math.random() < 0.2) {
    const stationsRes = http.get(`${BASE_URL}/api/v1/stations`);
    check(stationsRes, {
      'stations status is 200': (r) => r.status === 200,
    });
  }

  sleep(Math.random() * 0.5 + 0.1);
}
