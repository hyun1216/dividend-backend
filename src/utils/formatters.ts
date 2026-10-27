// src/utils/formatters.ts

/**
 * 숫자를 한국 통화 단위 문자열로 포맷팅합니다 (예: 1,000,000)
 */
export function formatMoney(amount: number): string {
  if (isNaN(amount) || amount === null || amount === undefined) return '0';
  return Math.round(amount).toLocaleString('ko-KR');
}

/**
 * 콤마가 포함된 문자열을 순수 숫자로 파싱합니다.
 */
export function parseMoneyString(str: string): number {
  if (!str) return 0;
  const cleaned = str.replace(/[^0-9]/g, '');
  return cleaned ? parseInt(cleaned, 10) : 0;
}

/**
 * 퍼센트 표기 (예: 4.5 -> "4.50%")
 */
export function formatPercent(rate: number, decimals: number = 2): string {
  if (isNaN(rate) || rate === null || rate === undefined) return '0.00%';
  return `${rate.toFixed(decimals)}%`;
}

/**
 * 만원/억원 단위 한글 축약 표기 (선택적 가독성 향상)
 */
export function formatKoreanUnit(amount: number): string {
  if (amount >= 100_000_000) {
    const eok = Math.floor(amount / 100_000_000);
    const man = Math.floor((amount % 100_000_000) / 10_000);
    return man > 0 ? `${eok}억 ${formatMoney(man)}만원` : `${eok}억원`;
  }
  if (amount >= 10_000) {
    const man = Math.floor(amount / 10_000);
    return `${formatMoney(man)}만원`;
  }
  return `${formatMoney(amount)}원`;
}
