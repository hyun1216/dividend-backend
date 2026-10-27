// src/app/api/stocks/route.ts
import { NextResponse } from 'next/server';
import { DEFAULT_DIVIDEND_STOCKS } from '@/constants/stockData';
import { StockItem } from '@/types/dividend';

export const runtime = 'nodejs';
export const revalidate = 600; // 10분 캐시

async function fetchTickerPrice(ticker: string): Promise<number> {
  try {
    const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(ticker)}?interval=1d&range=1d`;
    const res = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      },
      next: { revalidate: 600 },
    });

    if (!res.ok) return 0;
    const json = await res.json();
    const meta = json?.chart?.result?.[0]?.meta;
    const regularMarketPrice = meta?.regularMarketPrice;
    if (typeof regularMarketPrice === 'number' && regularMarketPrice > 0) {
      return regularMarketPrice;
    }

    const closePrices = json?.chart?.result?.[0]?.indicators?.quote?.[0]?.close;
    if (Array.isArray(closePrices) && closePrices.length > 0) {
      const valid = closePrices.filter((p: number | null) => p !== null);
      if (valid.length > 0) return valid[valid.length - 1];
    }
    return 0;
  } catch (error) {
    return 0;
  }
}

export async function GET() {
  try {
    const enrichedStocks: StockItem[] = await Promise.all(
      DEFAULT_DIVIDEND_STOCKS.map(async (stock) => {
        const price = await fetchTickerPrice(stock.ticker);
        return {
          ...stock,
          price,
        };
      })
    );

    const now = new Date();
    const updateTime = now.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    });

    return NextResponse.json({
      success: true,
      data: enrichedStocks,
      update_time: updateTime,
    });
  } catch (error) {
    console.error('Error fetching stock list:', error);
    return NextResponse.json(
      {
        success: false,
        error: '종목 데이터를 불러오지 못했습니다.',
        data: DEFAULT_DIVIDEND_STOCKS,
      },
      { status: 500 }
    );
  }
}
