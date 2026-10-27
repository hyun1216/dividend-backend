// src/components/calculator/ResultSummary.tsx
import React from 'react';
import { CalculationResult } from '@/types/dividend';
import { formatMoney } from '@/utils/formatters';

interface ResultSummaryProps {
  results: CalculationResult[];
  isLoading: boolean;
}

export const ResultSummary: React.FC<ResultSummaryProps> = ({ results, isLoading }) => {
  if (isLoading) {
    return (
      <div className="bg-white border border-stone-200 p-12 text-center">
        <div className="w-8 h-8 border-3 border-stone-200 border-t-amber-500 rounded-full animate-spin mx-auto mb-4" />
        <p className="text-sm font-bold text-stone-600">실시간 종목 및 주가 데이터를 불러오고 있습니다...</p>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="bg-white border border-dashed border-stone-300 p-12 text-center">
        <p className="text-base font-bold text-stone-700">해당 조건에 일치하는 종목이 없습니다.</p>
        <p className="text-xs text-stone-400 mt-1">
          상단 검색창에 종목명이나 티커를 입력하고 &apos;Enter&apos;를 눌러 새로 추가해 보세요.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {results.map(({ stock, requiredPrincipal, requiredShares, distributionGuide, isGrowthStock }) => {
        const periodBadgeColor =
          stock.period === '지정월배당'
            ? 'bg-amber-100 text-amber-800 border-amber-300'
            : stock.period === '분기배당'
            ? 'bg-cyan-50 text-cyan-800 border-cyan-300'
            : 'bg-emerald-50 text-emerald-800 border-emerald-300';

        if (isGrowthStock) {
          return (
            <div
              key={stock.ticker}
              className="bg-white border border-stone-200 p-5 hover:border-amber-500 transition-colors flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4"
            >
              <div>
                <div className="flex flex-wrap items-center gap-2 mb-1">
                  <h3 className="text-base font-bold text-stone-900">{stock.name}</h3>
                  <span className="bg-stone-100 text-stone-600 text-[10px] font-bold px-2 py-0.5 border border-stone-300">
                    성장주
                  </span>
                </div>
                <p className="text-xs text-stone-500 max-w-md">{stock.desc}</p>
                <div className="text-[11px] text-stone-400 mt-2 flex items-center gap-1">
                  <span>💵 실시간 주가:</span>
                  <span className="text-stone-700 font-bold">{formatMoney(stock.price)}원</span>
                </div>
              </div>
              <div className="text-right border-t sm:border-t-0 pt-3 sm:pt-0 border-stone-100">
                <div className="bg-stone-50 border border-stone-200 p-3 inline-block text-left min-w-[200px] sm:min-w-[250px]">
                  <div className="text-xs font-bold text-amber-700 mb-1">
                    💡 본 종목은 배당을 지급하지 않는 성장주입니다.
                  </div>
                  <div className="text-[10px] text-stone-500">
                    시세 차익 중심의 포트폴리오 구성에 적합합니다.
                  </div>
                </div>
              </div>
            </div>
          );
        }

        return (
          <div
            key={stock.ticker}
            className="bg-white border border-stone-200 p-5 hover:border-amber-500 transition-colors flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4"
          >
            <div>
              <div className="flex flex-wrap items-center gap-2 mb-1">
                <h3 className="text-base font-bold text-stone-900">{stock.name}</h3>
                <span className="bg-stone-900 text-white text-[10px] font-bold px-2 py-0.5">
                  연 {stock.rate}%
                </span>
                <span className={`text-[10px] font-bold px-1.5 py-0.5 border ${periodBadgeColor}`}>
                  {stock.period}
                </span>
              </div>
              <p className="text-xs text-stone-500 max-w-md">{stock.desc}</p>
              <div className="text-[11px] text-stone-400 mt-2 flex items-center gap-1">
                <span>💵 실시간 주가:</span>
                <span className="text-stone-700 font-bold">{formatMoney(stock.price)}원</span>
              </div>
            </div>

            <div className="text-right border-t sm:border-t-0 pt-3 sm:pt-0 border-stone-100">
              <div className="text-xs font-bold text-stone-400 mb-0.5 uppercase tracking-wider">
                필요 투자 원금
              </div>
              <div className="text-xl sm:text-2xl font-black text-amber-600">
                약 {formatMoney(requiredPrincipal)}원
              </div>
              <div className="text-xs font-bold text-stone-600 mt-0.5">
                (약 {formatMoney(requiredShares)}주 보유 필요)
              </div>
              <div className="text-[10px] text-stone-500 mt-1">
                💡 {distributionGuide}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
