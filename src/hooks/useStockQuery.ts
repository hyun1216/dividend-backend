// src/hooks/useStockQuery.ts
'use client';

import { useState, useEffect, useCallback } from 'react';
import { StockItem } from '@/types/dividend';
import { getStocks, getExchangeRate, getStockBySymbol } from '@/services/dividendService';

export function useStockQuery() {
  const [stocks, setStocks] = useState<StockItem[]>([]);
  const [exchangeRate, setExchangeRate] = useState<number>(1350);
  const [updateTime, setUpdateTime] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isAddingStock, setIsAddingStock] = useState<boolean>(false);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [rate, stockResult] = await Promise.all([
        getExchangeRate(),
        getStocks(),
      ]);

      setExchangeRate(rate);
      setUpdateTime(stockResult.updateTime);

      // 미국 종목에 환율 적용
      const convertedStocks: StockItem[] = stockResult.data.map((stock) => {
        if (stock.isUS && stock.price > 0) {
          return {
            ...stock,
            price: stock.price * rate,
          };
        }
        return stock;
      });

      setStocks(convertedStocks);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : '데이터를 불러오지 못했습니다.';
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // 새로운 종목 검색 및 목록 추가
  const addStock = useCallback(
    async (symbol: string): Promise<StockItem> => {
      setIsAddingStock(true);
      try {
        const rawStock = await getStockBySymbol(symbol);
        const isUS = Boolean(rawStock.isUS);
        const finalPrice = isUS && rawStock.price > 0 ? rawStock.price * exchangeRate : rawStock.price;

        const newStockItem: StockItem = {
          category: isUS
            ? rawStock.rate > 5 ? 'us-etf' : 'us-stock'
            : rawStock.rate > 4 ? 'kr-etf' : 'kr-stock',
          ticker: rawStock.ticker,
          isUS,
          period: (rawStock.period as StockItem['period']) || '분기배당',
          months: rawStock.months || '매달',
          name: rawStock.name,
          rate: rawStock.rate,
          desc: rawStock.desc,
          price: finalPrice,
        };

        setStocks((prev) => {
          // 중복 티커가 이미 있으면 교체, 없으면 맨 앞에 추가
          const filtered = prev.filter(
            (s) => s.ticker.toUpperCase() !== newStockItem.ticker.toUpperCase()
          );
          return [newStockItem, ...filtered];
        });

        return newStockItem;
      } finally {
        setIsAddingStock(false);
      }
    },
    [exchangeRate]
  );

  return {
    stocks,
    exchangeRate,
    updateTime,
    isLoading,
    isAddingStock,
    error,
    refresh: fetchData,
    addStock,
  };
}
