// src/components/common/Footer.tsx
'use client';

import React from 'react';

interface FooterProps {
  onOpenPrivacy: () => void;
  onOpenGuide: () => void;
}

export const Footer: React.FC<FooterProps> = ({ onOpenPrivacy, onOpenGuide }) => {
  return (
    <footer className="mt-12 text-center border-t border-stone-200 pt-6">
      <div className="flex justify-center gap-3 mb-3">
        <button
          onClick={onOpenGuide}
          className="text-xs font-bold text-amber-700 bg-amber-50 hover:bg-amber-100 border border-amber-200 px-3 py-1.5 transition-colors"
        >
          🔰 초보자를 위한 배당 가이드
        </button>
        <button
          onClick={onOpenPrivacy}
          className="text-xs text-stone-500 hover:text-stone-800 underline underline-offset-4 transition-colors"
        >
          개인정보처리방침 및 면책조항
        </button>
      </div>

      <p className="text-[11px] text-stone-400 leading-relaxed max-w-lg mx-auto">
        ⚠️ 본 계산기는 각 종목의 최근 평균 배당수익률 기준으로 계산된 참고용 수치입니다.
        <br />
        주가 변동 및 기업의 배당 정책에 따라 실제 수치는 변동될 수 있으므로 투자 시 리스크에 유의하시기 바랍니다.
      </p>

      <p className="text-[10px] text-stone-400 mt-3 font-mono">
        © {new Date().getFullYear()} MyDividend.co.kr. All rights reserved.
      </p>
    </footer>
  );
};
