// src/types/api.ts
import { StockItem } from './dividend';

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  updateTime?: string;
}

export interface StocksResponseData {
  data: StockItem[];
  update_time: string;
}

export interface SingleStockResponse {
  ticker: string;
  price: number;
  rate: number;
  name: string;
  desc: string;
  period: string;
  months: string;
  isUS?: boolean;
}

export interface SearchQuoteItem {
  shortname: string;
  longname?: string;
  symbol: string;
  exchange: string;
}

export interface SearchResponseData {
  quotes: SearchQuoteItem[];
}

export interface ExchangeRateResponseData {
  rates: {
    KRW: number;
    [key: string]: number;
  };
  time_last_update_utc?: string;
}
