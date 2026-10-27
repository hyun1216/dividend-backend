// src/types/dividend.ts

export type StockCategory = 'all' | 'kr-stock' | 'us-stock' | 'kr-etf' | 'us-etf';

export type DividendPeriod = '월배당' | '분기배당' | '반기배당' | '지정월배당' | '연배당';

export interface StockItem {
  category: StockCategory;
  ticker: string;
  isUS: boolean;
  period: DividendPeriod;
  months: string;
  name: string;
  rate: number; // 배당수익률 (%)
  desc: string;
  price: number; // 실시간 주가 (미국 주식은 환율 적용된 원화 주가)
}

export interface CalculationResult {
  stock: StockItem;
  targetMonthNet: number;       // 매달 받고 싶은 목표 세후 배당금
  targetYearGross: number;      // 연간 세전 배당금 (15.4% 역산)
  requiredPrincipal: number;    // 필요 투자 원금
  requiredShares: number;       // 필요 주식 수
  distributionGuide: string;    // 지급 주기별 실수령 안내 문구
  isGrowthStock: boolean;       // 무배당 성장주 여부
}
