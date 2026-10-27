// src/hooks/useDividendCalculator.ts
'use client';

import { useState, useMemo } from 'react';
import { StockItem, StockCategory, CalculationResult } from '@/types/dividend';
import { calculateStockDividend } from '@/utils/calculator';

interface UseDividendCalculatorProps {
  stocks: StockItem[];
}

export function useDividendCalculator({ stocks }: UseDividendCalculatorProps) {
  const [targetMonthNet, setTargetMonthNet] = useState<number>(1_000_000);
  const [selectedCategory, setSelectedCategory] = useState<StockCategory>('all');
  const [searchFilter, setSearchFilter] = useState<string>('');

  const calculationResults = useMemo<CalculationResult[]>(() => {
    const query = searchFilter.toLowerCase().trim();

    return stocks
      .filter((stock) => {
        // 카테고리 필터링
        if (selectedCategory !== 'all' && stock.category !== selectedCategory) {
          return false;
        }
        // 검색어 필터링 (종목명, 설명, 티커)
        if (query) {
          const matchName = stock.name.toLowerCase().includes(query);
          const matchDesc = stock.desc.toLowerCase().includes(query);
          const matchTicker = stock.ticker.toLowerCase().includes(query);
          if (!matchName && !matchDesc && !matchTicker) {
            return false;
          }
        }
        return true;
      })
      .map((stock) => calculateStockDividend(stock, targetMonthNet));
  }, [stocks, targetMonthNet, selectedCategory, searchFilter]);

  return {
    targetMonthNet,
    setTargetMonthNet,
    selectedCategory,
    setSelectedCategory,
    searchFilter,
    setSearchFilter,
    calculationResults,
  };
}
