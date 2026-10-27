// src/utils/calculator.ts
import { StockItem, CalculationResult } from '@/types/dividend';
import { formatMoney } from './formatters';

export const DIVIDEND_TAX_RATE = 0.154; // 배당소득세 15.4%

/**
 * 목표 월 배당금(세후)을 받기 위해 필요한 연간 세전 배당금을 계산합니다.
 */
export function calculateYearlyGross(targetMonthNet: number): number {
  if (targetMonthNet <= 0) return 0;
  return (targetMonthNet * 12) / (1 - DIVIDEND_TAX_RATE);
}

/**
 * 개별 종목에 대한 배당 계산 결과를 산출합니다.
 */
export function calculateStockDividend(
  stock: StockItem,
  targetMonthNet: number
): CalculationResult {
  const isGrowthStock = stock.rate <= 0;
  const targetYearGross = calculateYearlyGross(targetMonthNet);

  if (isGrowthStock || stock.price <= 0 || stock.rate <= 0) {
    return {
      stock,
      targetMonthNet,
      targetYearGross,
      requiredPrincipal: 0,
      requiredShares: 0,
      distributionGuide: '배당을 지급하지 않는 성장주입니다.',
      isGrowthStock: true,
    };
  }

  // 필요 원금 = 연 세전 배당금 / (배당률 / 100)
  const requiredPrincipal = targetYearGross / (stock.rate / 100);
  const requiredShares = Math.ceil(requiredPrincipal / stock.price);

  let distributionGuide = '';
  switch (stock.period) {
    case '월배당':
      distributionGuide = `매달 약 ${formatMoney(targetMonthNet)}원 지급`;
      break;
    case '분기배당':
      distributionGuide = `3개월마다 약 ${formatMoney(targetMonthNet * 3)}원 지급`;
      break;
    case '반기배당':
      distributionGuide = `6개월마다 약 ${formatMoney(targetMonthNet * 6)}원 지급`;
      break;
    case '지정월배당':
      distributionGuide = `지정월 집중 지급 (연간 합계 약 ${formatMoney(targetMonthNet * 12)}원)`;
      break;
    default:
      distributionGuide = `연간 약 ${formatMoney(targetMonthNet * 12)}원 지급`;
      break;
  }

  return {
    stock,
    targetMonthNet,
    targetYearGross,
    requiredPrincipal,
    requiredShares,
    distributionGuide,
    isGrowthStock: false,
  };
}
