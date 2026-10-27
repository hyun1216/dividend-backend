// src/services/dividendService.ts
import { StockItem } from '@/types/dividend';
import { SearchQuoteItem, SingleStockResponse } from '@/types/api';

/**
 * 대표 추천 배당주 목록 및 실시간 주가를 조회합니다.
 */
export async function getStocks(): Promise<{ data: StockItem[]; updateTime: string }> {
  const res = await fetch('/api/stocks', { cache: 'no-store' });
  if (!res.ok) {
    throw new Error('대표 배당주 목록을 불러오는데 실패했습니다.');
  }
  const json = await res.json();
  return {
    data: json.data || [],
    updateTime: json.update_time || '',
  };
}

/**
 * 실시간 환율 (USD/KRW)을 조회합니다.
 */
export async function getExchangeRate(): Promise<number> {
  const res = await fetch('/api/exchange');
  if (!res.ok) {
    return 1350; // Fallback 기본 환율
  }
  const json = await res.json();
  return json.rate || 1350;
}

/**
 * 단일 종목 심볼(티커)로 실시간 시세 및 배당수익률을 검색/조회합니다.
 */
export async function getStockBySymbol(symbol: string): Promise<SingleStockResponse> {
  const res = await fetch(`/api/stock?symbol=${encodeURIComponent(symbol)}`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.error || `종목 [${symbol}]을 찾을 수 없습니다.`);
  }
  return res.json();
}

/**
 * 종목명 또는 티커 키워드로 실시간 종목 목록을 검색합니다.
 */
export async function searchTicker(keyword: string): Promise<SearchQuoteItem[]> {
  if (!keyword.trim()) return [];
  const res = await fetch(`/api/search?q=${encodeURIComponent(keyword)}`);
  if (!res.ok) {
    throw new Error('종목 검색에 실패했습니다.');
  }
  const json = await res.json();
  return json.quotes || [];
}
