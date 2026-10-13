export interface Station {
  id: string;
  code_yandex: string;
  title: string;
  direction: string;
  latitude?: number;
  longitude?: number;
  is_junction: boolean;
}

export interface RouteSegment {
  train_number: string;
  train_type: string;
  station_from_title: string;
  station_from_code: string;
  station_to_title: string;
  station_to_code: string;
  departure_time: string;
  arrival_time: string;
  delay_minutes: number;
  status: 'ON_TIME' | 'DELAYED' | 'CANCELLED';
}

export interface TransferInfo {
  junction_station_title: string;
  junction_station_code: string;
  wait_time_minutes: number;
  walking_buffer_minutes: number;
  is_tight_connection: boolean;
}

export interface RouteOption {
  option_id: string;
  is_direct: boolean;
  total_duration_minutes: number;
  departure_time: string;
  arrival_time: string;
  segments: RouteSegment[];
  transfer?: TransferInfo;
}

export interface RouteSearchResponse {
  from_station: Station;
  to_station: Station;
  search_date: string;
  is_degraded: boolean;
  system_status: string;
  routes_count: number;
  routes: RouteOption[];
}

export interface LiveDelayItem {
  train_number: string;
  station_title: string;
  scheduled_time: string;
  delay_minutes: number;
  status: string;
  recorded_at: string;
}
