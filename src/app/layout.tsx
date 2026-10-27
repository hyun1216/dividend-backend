// src/app/layout.tsx
import type { Metadata, Viewport } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: '월 배당금 목표 원금 계산기 | MyDividend',
  description: '원하는 월평균 배당금을 받기 위해 필요한 종목별 진짜 투자 원금을 실시간 주가와 배당률로 역산해 드립니다.',
  verification: {
    google: 'ApxSdhPPPzhnVYIeqsM9VVLi2qIgT2Xk-mjI0Lm_pIE',
  },
  openGraph: {
    title: '월 배당금 목표 원금 계산기',
    description: '원하는 월평균 배당금을 받기 위해 필요한 종목별 진짜 원금을 계산해 드립니다.',
    url: 'https://mydividend.co.kr',
    siteName: 'MyDividend',
    locale: 'ko_KR',
    type: 'website',
  },
  icons: {
    icon: 'data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>💰</text></svg>',
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <head>
        {/* 구글 애드센스 스크립트 */}
        <script
          async
          src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7665112064862173"
          crossOrigin="anonymous"
        />
      </head>
      <body className="min-h-screen flex items-center justify-center p-4 sm:p-8 antialiased">
        {children}
      </body>
    </html>
  );
}
