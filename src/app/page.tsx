// src/app/page.tsx
'use client';

import React, { useState } from 'react';
import { useStockQuery } from '@/hooks/useStockQuery';
import { useDividendCalculator } from '@/hooks/useDividendCalculator';
import { Header } from '@/components/common/Header';
import { Footer } from '@/components/common/Footer';
import { Modal } from '@/components/common/Modal';
import { DividendForm } from '@/components/calculator/DividendForm';
import { ResultSummary } from '@/components/calculator/ResultSummary';
import { StockSearchModal } from '@/components/calculator/StockSearchModal';

export default function DividendCalculatorPage() {
  const {
    stocks,
    exchangeRate,
    updateTime,
    isLoading,
    isAddingStock,
    addStock,
  } = useStockQuery();

  const {
    targetMonthNet,
    setTargetMonthNet,
    selectedCategory,
    setSelectedCategory,
    searchFilter,
    setSearchFilter,
    calculationResults,
  } = useDividendCalculator({ stocks });

  const [isTickerModalOpen, setIsTickerModalOpen] = useState(false);
  const [isPrivacyModalOpen, setIsPrivacyModalOpen] = useState(false);
  const [isGuideModalOpen, setIsGuideModalOpen] = useState(false);
  const [statusNotification, setStatusNotification] = useState<string | null>(null);

  // 새로운 종목 엔터 입력 또는 티커 선택 시 추가 핸들러
  const handleAddNewStock = async (query: string) => {
    try {
      setStatusNotification(`🔍 [${query}] 실시간 배당 데이터 수집 중...`);
      const newStock = await addStock(query);
      setStatusNotification(`✅ [${newStock.name}] 종목이 성공적으로 추가되었습니다!`);
      setTimeout(() => setStatusNotification(null), 3000);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : '종목 추가에 실패했습니다.';
      setStatusNotification(`❌ ${msg}`);
      setTimeout(() => setStatusNotification(null), 4000);
    }
  };

  const handleSelectTickerFromModal = (ticker: string) => {
    setSearchFilter(ticker);
    handleAddNewStock(ticker);
  };

  return (
    <main className="max-w-3xl w-full mx-auto bg-white border border-stone-300 p-6 sm:p-10 shadow-sm relative">
      <Header
        updateTime={updateTime}
        exchangeRate={exchangeRate}
        isLoading={isLoading}
        statusMessage={statusNotification || undefined}
      />

      <DividendForm
        targetMonthNet={targetMonthNet}
        onTargetChange={setTargetMonthNet}
        selectedCategory={selectedCategory}
        onSelectCategory={setSelectedCategory}
        searchFilter={searchFilter}
        onSearchFilterChange={setSearchFilter}
        onAddNewStock={handleAddNewStock}
        isAddingStock={isAddingStock}
        onOpenTickerModal={() => setIsTickerModalOpen(true)}
      />

      <div className="mt-8">
        <ResultSummary results={calculationResults} isLoading={isLoading} />
      </div>

      <Footer
        onOpenPrivacy={() => setIsPrivacyModalOpen(true)}
        onOpenGuide={() => setIsGuideModalOpen(true)}
      />

      {/* 우하단 고정 플로팅 버튼 (티커 찾기) */}
      <button
        onClick={() => setIsTickerModalOpen(true)}
        className="fixed bottom-6 right-6 bg-amber-600 hover:bg-amber-700 text-white font-bold text-xs sm:text-sm px-5 py-3 shadow-md flex items-center gap-2 border border-amber-500 transition-all z-40 active:scale-95"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
          <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        국내 종목 티커 찾기
      </button>

      {/* 1. 티커 검색 모달 */}
      <StockSearchModal
        isOpen={isTickerModalOpen}
        onClose={() => setIsTickerModalOpen(false)}
        onSelectTicker={handleSelectTickerFromModal}
      />

      {/* 2. 개인정보처리방침 모달 */}
      <Modal
        isOpen={isPrivacyModalOpen}
        onClose={() => setIsPrivacyModalOpen(false)}
        title="🛡️ 개인정보처리방침 및 면책조항"
      >
        <div>
          <h3 className="text-amber-700 font-bold mb-1">1. 수집하는 개인정보 (익명 데이터)</h3>
          <p>
            본 사이트는 별도의 회원가입 절차가 없으며 개인 식별 정보를 서버에 저장하지 않습니다.
          </p>
        </div>
        <div>
          <h3 className="text-amber-700 font-bold mb-1">2. 구글 애드센스 및 쿠키 사용</h3>
          <p>
            본 사이트는 구글 애드센스 광고를 게재하고 있습니다. 구글 및 타사 공급업체는 쿠키를 사용하여 맞춤 광고를 제공할 수 있습니다.
          </p>
        </div>
        <div>
          <h3 className="text-rose-600 font-bold mb-1">3. 투자 유의사항 및 면책</h3>
          <p>
            본 계산기에서 제공하는 배당금, 예상 원금 등은 최근 공시된 배당 데이터 기준의 참고용 수치입니다. 주가 변동 및 배당 삭감 등에 따라 실제 수치는 달라질 수 있습니다.
          </p>
        </div>
        <div className="pt-2 text-center">
          <button
            onClick={() => setIsPrivacyModalOpen(false)}
            className="bg-stone-900 hover:bg-stone-800 text-white px-6 py-2 font-bold text-xs transition-colors"
          >
            확인했습니다
          </button>
        </div>
      </Modal>

      {/* 3. 배당 투자 가이드 모달 */}
      <Modal
        isOpen={isGuideModalOpen}
        onClose={() => setIsGuideModalOpen(false)}
        title="🔰 초보자를 위한 배당 투자 가이드"
        maxWidth="max-w-lg"
      >
        <div className="space-y-3">
          <div className="bg-stone-50 p-4 border border-stone-200">
            <h4 className="font-bold text-stone-900 mb-1 flex items-center gap-1.5">
              <span className="text-amber-600 font-mono">01.</span> 일반 고배당주
            </h4>
            <p className="text-xs text-stone-500 mb-1">예: 신한지주, 맥쿼리인프라, 리얼티인컴(O)</p>
            <p className="text-xs text-stone-600 leading-relaxed">
              • <b>장점:</b> 안정적인 현금 흐름 창출<br />
              • <span className="text-rose-600">리스크:</span> 고금리 시기 매력 감소 및 시세 차익 한계
            </p>
          </div>

          <div className="bg-stone-50 p-4 border border-stone-200">
            <h4 className="font-bold text-stone-900 mb-1 flex items-center gap-1.5">
              <span className="text-amber-600 font-mono">02.</span> 배당 우선주
            </h4>
            <p className="text-xs text-stone-500 mb-1">예: 삼성전자우, 현대차2우B</p>
            <p className="text-xs text-stone-600 leading-relaxed">
              • <b>장점:</b> 본주 대비 저렴한 주가로 배당수익률 상승<br />
              • <span className="text-rose-600">리스크:</span> 거래량이 적어 환금성 주의 필요
            </p>
          </div>

          <div className="bg-stone-50 p-4 border border-stone-200">
            <h4 className="font-bold text-stone-900 mb-1 flex items-center gap-1.5">
              <span className="text-amber-600 font-mono">03.</span> 배당 성장 ETF
            </h4>
            <p className="text-xs text-stone-500 mb-1">예: SCHD, SOL 미국배당다우존스</p>
            <p className="text-xs text-stone-600 leading-relaxed">
              • <b>장점:</b> 배당금을 지속 증액하는 우량주 분산 투자 (복리 효과)<br />
              • <span className="text-rose-600">리스크:</span> 초기 배당률(3~4%대)이 다소 낮음
            </p>
          </div>

          <div className="bg-rose-50/50 p-4 border border-rose-200">
            <h4 className="font-bold text-stone-900 mb-1 flex items-center gap-1.5">
              <span className="text-rose-600 font-mono">04.</span> 커버드콜 / 초고배당 ETF
            </h4>
            <p className="text-xs text-stone-500 mb-1">예: JEPI, TLTW, +7% 프리미엄</p>
            <p className="text-xs text-stone-600 leading-relaxed">
              • <b>장점:</b> 연 7~14% 수준의 압도적인 현금 흐름<br />
              • <span className="text-rose-600 font-bold">주의:</span> 주가 상승 상방이 제한되고 원금 훼손 가능성 존재
            </p>
          </div>
        </div>
        <div className="pt-2 text-center">
          <button
            onClick={() => setIsGuideModalOpen(false)}
            className="bg-stone-900 hover:bg-stone-800 text-white px-6 py-2 font-bold text-xs transition-colors"
          >
            다 읽었습니다!
          </button>
        </div>
      </Modal>
    </main>
  );
}
