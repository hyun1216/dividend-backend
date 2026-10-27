# MyDividend (배당달력 & 배당계산기)

한국 및 미국 주식 배당금 조회, 월별 배당 달력, 배당금 시뮬레이션 및 커뮤니티 게시판을 제공하는 풀스택 웹 애플리케이션입니다.

## 🚀 기술 스택

- **Frontend**: Next.js (App Router), React, TypeScript, Tailwind CSS, Lucide Icons
- **Backend / Serverless**: Python 3.9+, Flask, PyMySQL, yfinance
- **Database**: Aiven Cloud MySQL (SSL 암호화 연결)
- **Deployment**: Vercel (Next.js + Python Serverless Functions)

## 📁 프로젝트 구조

```text
├── api/                  # Vercel 파이썬 서버리스 함수 (Flask API)
│   └── index.py          # 주식 데이터(Yahoo Finance) 및 게시판 CRUD
├── src/                  # Next.js 프론트엔드
│   ├── app/              # App Router 페이지 (홈, 배당달력, 게시판 등)
│   └── components/       # UI 컴포넌트
├── public/               # 정적 애셋
├── requirements.txt      # 파이썬 의존성 패키지
├── vercel.json           # Vercel 보안 및 라우팅 설정
└── .env.example          # 환경변수 템플릿
```

## ⚙️ 환경변수 설정 (Vercel)

Vercel 대시보드의 **Settings > Environment Variables**에 아래 변수를 등록합니다:

- `DB_HOST`: 데이터베이스 호스트
- `DB_USER`: 데이터베이스 사용자명
- `DB_PASSWORD`: 데이터베이스 비밀번호
- `DB_NAME`: 데이터베이스 이름
- `DB_PORT`: 데이터베이스 포트