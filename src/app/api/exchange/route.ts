// src/app/api/exchange/route.ts
import { NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const revalidate = 3600; // 1시간 캐시

export async function GET() {
  try {
    const res = await fetch('https://open.er-api.com/v6/latest/USD', {
      next: { revalidate: 3600 },
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
      },
    });

    if (!res.ok) {
      throw new Error(`Exchange API error: ${res.status}`);
    }

    const data = await res.json();
    const krwRate = data.rates?.KRW || 1350;

    return NextResponse.json({
      success: true,
      rate: krwRate,
      updatedAt: data.time_last_update_utc || new Date().toUTCString(),
    });
  } catch (error) {
    console.error('Failed to fetch exchange rate:', error);
    // Fallback 안전값
    return NextResponse.json({
      success: true,
      rate: 1350,
      isFallback: true,
      updatedAt: new Date().toUTCString(),
    });
  }
}
