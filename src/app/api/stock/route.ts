// src/app/api/stock/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { DEFAULT_DIVIDEND_STOCKS, BUILTIN_KR_STOCKS } from '@/constants/stockData';

export const runtime = 'nodejs';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  let symbol = (searchParams.get('symbol') || '').toUpperCase().trim();

  if (!symbol) {
    return NextResponse.json({ error: '종목 코드가 필요합니다.' }, { status: 400 });
  }

  // 한국 주식 6자리 숫자 코드 자동 접미사 처리
  if (/^\d{6}$/.test(symbol)) {
    symbol += '.KS';
  }

  try {
    // 1. 실시간 주가 조회 (Yahoo Finance v8 Chart API)
    const chartUrl = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(symbol)}?interval=1d&range=1d`;
    const chartRes = await fetch(chartUrl, {
      headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' },
      next: { revalidate: 300 },
    });

    if (!chartRes.ok) {
      return NextResponse.json({ error: `종목 [${symbol}] 데이터를 찾을 수 없습니다.` }, { status: 404 });
    }

    const chartJson = await chartRes.json();
    const meta = chartJson?.chart?.result?.[0]?.meta;
    const price = meta?.regularMarketPrice || 0;
    const shortName = meta?.shortName || symbol;

    if (price <= 0) {
      return NextResponse.json({ error: `종목 [${symbol}]의 현재가를 불러올 수 없습니다.` }, { status: 404 });
    }

    // 2. 배당 정보 조회 (QuoteSummary API)
    let rate = 0;
    let desc = '실시간 검색을 통해 추가된 종목입니다.';

    try {
      const summaryUrl = `https://query2.finance.yahoo.com/v10/finance/quoteSummary/${encodeURIComponent(symbol)}?modules=summaryDetail,defaultKeyStatistics,assetProfile`;
      const summaryRes = await fetch(summaryUrl, {
        headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' },
        next: { revalidate: 1800 },
      });

      if (summaryRes.ok) {
        const summaryJson = await summaryRes.json();
        const result = summaryJson?.quoteSummary?.result?.[0];
        const summaryDetail = result?.summaryDetail;
        const profile = result?.assetProfile;

        // 배당수익률 추출
        const dividendYieldRaw = summaryDetail?.dividendYield?.raw;
        const trailingAnnualDividendYield = summaryDetail?.trailingAnnualDividendYield?.raw;
        const dividendRate = summaryDetail?.dividendRate?.raw || summaryDetail?.trailingAnnualDividendRate?.raw;

        if (typeof dividendYieldRaw === 'number' && dividendYieldRaw > 0) {
          rate = Number((dividendYieldRaw * 100).toFixed(2));
        } else if (typeof trailingAnnualDividendYield === 'number' && trailingAnnualDividendYield > 0) {
          rate = Number((trailingAnnualDividendYield * 100).toFixed(2));
        } else if (typeof dividendRate === 'number' && dividendRate > 0 && price > 0) {
          rate = Number(((dividendRate / price) * 100).toFixed(2));
        }

        if (rate > 50.0) rate = 0.0; // 비정상 이상치 필터링

        if (profile?.longBusinessSummary) {
          desc = profile.longBusinessSummary.length > 50
            ? profile.longBusinessSummary.slice(0, 50) + '...'
            : profile.longBusinessSummary;
        }
      }
    // 프리셋 종목 정보가 있는 경우 Fallback (한국 ETF 배당 데이터 보완)
    const preset = DEFAULT_DIVIDEND_STOCKS.find(
      (s) => s.ticker.toUpperCase() === symbol || s.ticker.replace('.KS', '') === symbol
    );
    const builtin = BUILTIN_KR_STOCKS.find(
      (s) => s.ticker.toUpperCase() === symbol || s.code === symbol
    );

    const finalRate = rate > 0 ? rate : (preset?.rate || 0);
    const finalName = preset?.name || (builtin ? `${builtin.name} (${symbol})` : `${shortName} (${symbol})`);
    const finalDesc = preset?.desc || desc;
    const finalPeriod = preset?.period || (finalRate > 7.0 ? '월배당' : '분기배당');
    const finalMonths = preset?.months || (finalRate > 7.0 ? '매달' : '3, 6, 9, 12월');

    return NextResponse.json({
      ticker: symbol,
      price,
      rate: finalRate,
      name: finalName,
      desc: finalDesc,
      period: finalPeriod,
      months: finalMonths,
      isUS: !symbol.endsWith('.KS') && !symbol.endsWith('.KQ'),
    });
  } catch (error) {
    console.error('Error in single stock API:', error);
    return NextResponse.json(
      { error: '서버 내부 오류로 종목 조회에 실패했습니다.' },
      { status: 500 }
    );
  }
}
