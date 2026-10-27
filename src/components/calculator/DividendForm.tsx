// src/components/calculator/DividendForm.tsx
'use client';

import React, { useState } from 'react';
import { StockCategory } from '@/types/dividend';
import { CATEGORY_TABS } from '@/constants/stockData';
import { formatMoney, parseMoneyString } from '@/utils/formatters';

interface DividendFormProps {
  targetMonthNet: number;
  onTargetChange: (value: number) => void;
  selectedCategory: StockCategory;
  onSelectCategory: (category: StockCategory) => void;
  searchFilter: string;
  onSearchFilterChange: (query: string) => void;
  onAddNewStock: (query: string) => Promise<void>;
  isAddingStock: boolean;
  onOpenTickerModal: () => void;
}

export const DividendForm: React.FC<DividendFormProps> = ({
  targetMonthNet,
  onTargetChange,
  selectedCategory,
  onSelectCategory,
  searchFilter,
  onSearchFilterChange,
  onAddNewStock,
  isAddingStock,
  onOpenTickerModal,
}) => {
  const [inputValue, setInputValue] = useState(formatMoney(targetMonthNet));

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const rawVal = e.target.value;
    const num = parseMoneyString(rawVal);
    setInputValue(num > 0 ? formatMoney(num) : '');
    onTargetChange(num);
  };

  const handleKeyDownSearch = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      const trimmed = searchFilter.trim();
      if (trimmed) {
        onAddNewStock(trimmed);
      }
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. 목표 배당금 입력 카드 */}
      <div className="bg-stone-50 p-6 border border-stone-200">
        <label className="block text-xs font-bold text-stone-500 mb-2 uppercase tracking-wider">
          매달 받고 싶은 순수 배당금 (월평균 세후)
        </label>
        <div className="relative flex items-center">
          <input
            type="text"
            inputMode="numeric"
            value={inputValue}
            onChange={handleInputChange}
            className="w-full bg-white text-stone-900 text-2xl font-black pl-4 pr-12 py-3 border border-stone-300 focus:outline-none focus:border-amber-500 transition-colors text-right"
            placeholder="1,000,000"
          />
          <span className="absolute right-4 text-lg font-bold text-stone-400">원</span>
        </div>
        <p className="text-stone-400 text-[11px] mt-2 text-right">
          ※ 기본 배당소득세 15.4% 원천징수를 기준으로 역산한 보수적 수치입니다.
        </p>
      </div>

      {/* 2. 검색 및 신규 종목 추가 인풋 */}
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <svg className="h-4 w-4 text-stone-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <input
          type="text"
          value={searchFilter}
          onChange={(e) => onSearchFilterChange(e.target.value)}
          onKeyDown={handleKeyDownSearch}
          placeholder="종목명/티커 입력 후 결과가 없으면 '엔터(Enter)'를 쳐서 새로 추가하세요!"
          className="w-full bg-white text-stone-800 text-sm pl-11 pr-24 py-3 border border-stone-300 focus:outline-none focus:border-amber-500 transition-colors"
        />
        {isAddingStock ? (
          <div className="absolute right-3 top-3 text-xs text-amber-600 font-bold animate-pulse">
            조회 중...
          </div>
        ) : (
          <button
            type="button"
            onClick={onOpenTickerModal}
            className="absolute right-2 top-2 bg-amber-500 hover:bg-amber-600 text-white text-xs font-bold px-3 py-1.5 transition-colors"
          >
            티커 찾기
          </button>
        )}
      </div>

      {/* 3. 카테고리 탭 선택 */}
      <div className="flex flex-wrap gap-1 bg-stone-200 p-1 border border-stone-300">
        {CATEGORY_TABS.map((tab) => {
          const isActive = selectedCategory === tab.key;
          return (
            <button
              key={tab.key}
              onClick={() => onSelectCategory(tab.key)}
              className={`flex-1 min-w-[70px] text-xs sm:text-sm font-bold py-2 px-3 transition-colors text-center ${
                isActive
                  ? 'bg-white text-amber-700 border border-stone-300 shadow-xs'
                  : 'text-stone-600 hover:text-stone-900 hover:bg-stone-100'
              }`}
            >
              {tab.label}
            </button>
          );
        })}
      </div>
    </div>
  );
};
