// src/components/calculator/StockSearchModal.tsx
'use client';

import React, { useState, useEffect } from 'react';
import { Modal } from '@/components/common/Modal';
import { QUICK_PICK_STOCKS } from '@/constants/stockData';
import { searchTicker } from '@/services/dividendService';
import { SearchQuoteItem } from '@/types/api';

interface StockSearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectTicker: (ticker: string) => void;
}

export const StockSearchModal: React.FC<StockSearchModalProps> = ({
  isOpen,
  onClose,
  onSelectTicker,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState<SearchQuoteItem[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    if (!searchTerm.trim()) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }

    setIsSearching(true);
    const timeoutId = setTimeout(async () => {
      try {
        const quotes = await searchTicker(searchTerm);
        setSearchResults(quotes);
      } catch (err) {
        console.error('Ticker search failed:', err);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchTerm]);

  const handleSelect = (rawTicker: string) => {
    const cleanTicker = rawTicker.replace('.KS', '').replace('.KQ', '');
    onSelectTicker(cleanTicker);
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="🇰🇷 국내 주식 및 티커 실시간 검색기">
      <div className="flex flex-col gap-3">
        <p className="text-[11px] text-stone-500">
          종목명이나 코드를 입력하시면 실시간으로 티커를 찾아 바로 계산기에 추가해 드립니다.
        </p>

        <input
          type="text"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          placeholder="예: 카카오, 네이버, 현대차우, AAPL"
          className="w-full bg-stone-50 text-stone-800 text-sm font-bold px-3 py-2.5 border border-stone-300 focus:outline-none focus:border-amber-500 transition-colors"
          autoFocus
        />

        <div className="space-y-2 mt-2 h-[45vh] overflow-y-auto pr-1">
          {isSearching && (
            <div className="text-center py-6 text-xs text-amber-600 font-bold animate-pulse">
              실시간 데이터 검색 중... 🔍
            </div>
          )}

          {!isSearching && searchTerm.trim() && searchResults.length === 0 && (
            <div className="text-center py-6 text-xs text-stone-400">
              매칭되는 종목을 찾지 못했습니다. 🥲
            </div>
          )}

          {!searchTerm.trim() && (
            <div>
              <div className="text-[10px] text-amber-700 mb-2 font-bold px-1">
                🔥 많이 찾는 우선주 / 인프라 추천
              </div>
              <div className="space-y-2">
                {QUICK_PICK_STOCKS.map((item) => (
                  <div
                    key={item.ticker}
                    className="flex justify-between items-center bg-white p-3 border border-stone-200 text-xs hover:border-amber-500 transition-colors"
                  >
                    <span className="font-bold text-stone-700 truncate w-2/3">{item.name}</span>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-amber-700 font-bold tracking-wider bg-stone-50 px-2 py-1 border border-stone-200">
                        {item.ticker.replace('.KS', '')}
                      </span>
                      <button
                        onClick={() => handleSelect(item.ticker)}
                        className="bg-stone-900 hover:bg-stone-800 text-white px-3 py-1 font-bold text-[10px] transition-colors"
                      >
                        선택
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {!isSearching && searchResults.length > 0 && (
            <div className="space-y-2">
              {searchResults.map((item) => (
                <div
                  key={item.symbol}
                  className="flex justify-between items-center bg-white p-3 border border-stone-200 text-xs hover:border-amber-500 transition-colors"
                >
                  <div className="truncate w-2/3">
                    <span className="font-bold text-stone-800">{item.shortname || item.symbol}</span>
                    {item.longname && item.longname !== item.shortname && (
                      <p className="text-[10px] text-stone-400 truncate">{item.longname}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-amber-700 font-bold tracking-wider bg-stone-50 px-2 py-1 border border-stone-200">
                      {item.symbol.replace('.KS', '').replace('.KQ', '')}
                    </span>
                    <button
                      onClick={() => handleSelect(item.symbol)}
                      className="bg-stone-900 hover:bg-stone-800 text-white px-3 py-1 font-bold text-[10px] transition-colors"
                    >
                      선택
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Modal>
  );
};
