// src/components/common/Header.tsx
import React from 'react';
import Link from 'next/link';
import { formatMoney } from '@/utils/formatters';

interface HeaderProps {
  updateTime: string;
  exchangeRate: number;
  isLoading: boolean;
  statusMessage?: string;
}

export const Header: React.FC<HeaderProps> = ({
  updateTime,
  exchangeRate,
  isLoading,
  statusMessage,
}) => {
  return (
    <header className="text-center mb-8 border-b border-stone-200 pb-6">
      <span className="text-[11px] font-bold uppercase tracking-widest bg-amber-100 text-amber-800 px-2.5 py-0.5 border border-amber-300 inline-block mb-2">
        Dividend Master V5.0 (Next.js)
      </span>
      <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-stone-900 mb-2">
        월 배당금 목표 원금 계산기
      </h1>

      {updateTime && (
        <div className="mb-2">
          <p className="text-xs text-rose-600 font-bold bg-rose-50 border border-rose-200 inline-block px-2.5 py-1">
            ※ 현재 주가는 {updateTime} 기준으로 계산됩니다.
          </p>
        </div>
      )}

      <p className="text-xs sm:text-sm text-stone-500">
        원하는 월평균 배당금을 받기 위해 필요한 종목별 진짜 원금을 계산해 드립니다.
      </p>

      <p className={`text-xs text-amber-700 mt-2 font-bold ${isLoading ? 'animate-pulse' : ''}`}>
        {statusMessage || (isLoading
          ? '실시간 금융 API 및 환율 연동 중...'
          : `적용 환율: 1달러 = ${formatMoney(exchangeRate)}원`)}
      </p>

      <nav className="mt-5 flex justify-center">
        <Link
          href="/board"
          className="inline-flex items-center justify-center gap-2 border border-amber-400 bg-amber-50 px-5 py-2 text-xs font-bold text-amber-800 transition-colors hover:bg-amber-100"
        >
          <span>배당금 자랑 게시판 바로가기</span>
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M9 5l7 7-7 7" />
          </svg>
        </Link>
      </nav>
    </header>
  );
};
