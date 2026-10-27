// src/app/api/search/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { BUILTIN_KR_STOCKS } from '@/constants/stockData';
import { SearchQuoteItem } from '@/types/api';

export const runtime = 'nodejs';

export async function GET(request: NextRequest) {
  const query = (request.nextUrl.searchParams.get('q') || '').trim();

  if (!query) {
    return NextResponse.json({ quotes: [] });
  }

  const queryLower = query.toLowerCase();
  const quotes: SearchQuoteItem[] = [];

  // 1. 국내 내장 종목 매칭 (초고속 O(N) 필터)
  for (const stock of BUILTIN_KR_STOCKS) {
    const nameMatch = stock.name.includes(query);
    const codeMatch = stock.code.toLowerCase().includes(queryLower);
    const tickerMatch = stock.ticker.toLowerCase().includes(queryLower);

    if (nameMatch || codeMatch || tickerMatch) {
      quotes.push({
        shortname: stock.name,
        longname: stock.name,
        symbol: stock.ticker,
        exchange: 'KOR',
      });
    }

    if (quotes.length >= 15) break;
  }

  // 2. 해외 주식 또는 매칭 종목이 부족할 경우 Yahoo Finance Search API 조회
  if (queryLower.length >= 2) {
    try {
      const yahooUrl = `https://query2.finance.yahoo.com/v1/finance/search?q=${encodeURIComponent(query)}&quotesCount=10&newsCount=0`;
      const res = await fetch(yahooUrl, {
        headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' },
        next: { revalidate: 3600 },
      });

      if (res.ok) {
        const data = await res.json();
        const existingSymbols = new Set(quotes.map((q) => q.symbol));

        if (Array.isArray(data.quotes)) {
          for (const item of data.quotes) {
            if (item.symbol && !existingSymbols.has(item.symbol)) {
              quotes.push({
                shortname: item.shortname || item.longname || item.symbol,
                longname: item.longname || item.shortname,
                symbol: item.symbol,
                exchange: item.exchange || 'US',
              });
            }
            if (quotes.length >= 20) break;
          }
        }
      }
    } catch (err) {
      console.error('Yahoo Finance search error:', err);
    }
  }

  return NextResponse.json({ quotes });
}
