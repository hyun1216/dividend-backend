from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import time
from datetime import datetime
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# 기본 TOP 15 리스트
DIVIDEND_STOCKS = [
    { "category": "kr-stock", "ticker": "005935.KS", "isUS": False, "period": "분기배당", "months": "3, 6, 9, 12월", "name": "삼성전자우 (005935)", "rate": 0.92, "desc": "국민 주식 삼성전자의 배당 우선 우선주, 국내 대표 분기 배당주" },
    { "category": "kr-stock", "ticker": "055550.KS", "isUS": False, "period": "분기배당", "months": "2, 4, 7, 11월", "name": "신한지주 (055550)", "rate": 2.78, "desc": "국내 금융지주사 중 최초로 분기 배당을 정착시킨 대표적인 고배당 은행주" },
    { "category": "us-stock", "ticker": "O", "isUS": True, "period": "월배당", "months": "매달", "name": "리얼티인컴 (O)", "rate": 5.24, "desc": "매달 따박따박 월세처럼 달러 배당금을 주는 미국 부동산 대장주" },
    { "category": "us-stock", "ticker": "ABBV", "isUS": True, "period": "분기배당", "months": "2, 5, 8, 11월", "name": "에브비 (ABBV)", "rate": 3.15, "desc": "50년 넘게 배당을 늘려온 미국 대표 제약·바이오 대표 배당귀족주" },
    { "category": "kr-etf", "ticker": "088980.KS", "isUS": False, "period": "반기배당", "months": "6, 12월", "name": "맥쿼리인프라 (088980)", "rate": 6.89, "desc": "우리나라 도로·교량 통행료로 배당 주는 국내 근본 고배당주" },
    { "category": "kr-etf", "ticker": "446720.KS", "isUS": False, "period": "월배당", "months": "매달", "name": "SOL 미국배당다우존스", "rate": 2.79, "desc": "미국 SCHD를 한국 주식시장에서 만 원대로 매달 적립할 수 있는 한국형 월배당 ETF" },
    { "category": "kr-etf", "ticker": "476080.KS", "isUS": False, "period": "월배당", "months": "매달", "name": "TIME Korea플러스배당액티브", "rate": 5.11, "desc": "고배당 중간배당 실시하는 월배당 ETF" },
    { "category": "kr-etf", "ticker": "161510.KS", "isUS": False, "period": "월배당", "months": "매달", "name": "PLUS고배당주", "rate": 3.73, "desc": "유동시총 상위200중 예상 배당수익률 30위 이내 종목에 투자하는 ETF" },
    { "category": "kr-etf", "ticker": "447770.KS", "isUS": False, "period": "월배당", "months": "매달", "name": "KODEX 미국배당커버드콜액티브", "rate": 8.7, "desc": "미국 우량 배당성장주에 투자하고 옵션을 매도하여 월배당을 지급하는 ETF" },
    { "category": "kr-etf", "ticker": "479620.KS", "isUS": False, "period": "월배당", "months": "매달", "name": "KODEX 200타겟위클리커버드콜", "rate": 11.32, "desc": "코스피200에 위클리 커버드콜 전략으로 투자하는 ETF" },
    { "category": "kr-etf", "ticker": "474220.KS", "isUS": False, "period": "지정월배당", "months": "11, 12, 1, 2, 3, 4, 5월", "name": "SOL 코리아고배당", "rate": 3.44, "desc": "국내 고배당주 중심으로 안정성과 배당 수익을 동시에 추구하는 ETF" },
    { "category": "us-etf", "ticker": "SCHD", "isUS": True, "period": "분기배당", "months": "3, 6, 9, 12월", "name": "SCHD (Schwab US Dividend Equity ETF)", "rate": 3.3, "desc": "안정적인 배당 성장의 교과서, 미국 우량 배당주 모음" },
    { "category": "us-etf", "ticker": "JEPI", "isUS": True, "period": "월배당", "months": "매달", "name": "JEPI (JP모건 초고배당 ETF)", "rate": 8.43, "desc": "주가 상승보단 압도적인 월 배당 현금 흐름에 집중하는 ETF" },
    { "category": "us-etf", "ticker": "QQQI", "isUS": True, "period": "월배당", "months": "매달", "name": "QQQI", "rate": 7.57, "desc": "나스닥 100에 커버드콜 전략으로 투자하는 ETF" },
    { "category": "us-etf", "ticker": "SPYI", "isUS": True, "period": "월배당", "months": "매달", "name": "SPYI", "rate": 11.65, "desc": "S&P 500 지수 옵션 선물 전략을 사용하는 양방향 투자 월배당 ETF" },
    { "category": "us-etf", "ticker": "TLTW", "isUS": True, "period": "월배당", "months": "매달", "name": "TLTW (미국 장기채 커버드콜 ETF)", "rate": 14.2, "desc": "미국 20년 국채 투자와 콜옵션 매도를 결합해 초고배당을 주는 월배당 ETF" },
    { "category": "us-etf", "ticker": "DIVO", "isUS": True, "period": "월배당", "months": "매달", "name": "Divo (앰플리파이 배당 수익 ETF)", "rate": 6.45, "desc": "미국 우량 대형주 투자와 전술적 커버드콜 옵션 매도를 활용하는 월배당 ETF" }
]

cache = {}
CACHE_TTL = 18000  # 5시간

# 1. 메인화면용 전체 리스트 가져오기 (프론트엔드 형식에 맞춰 업데이트 시간 포함)
@app.route('/api/stocks')
def get_all_stocks():
    current_time = time.time()
    response_data = []
    
    for stock in DIVIDEND_STOCKS:
        ticker = stock["ticker"]
        if ticker in cache and (current_time - cache[ticker][0] < CACHE_TTL):
            price = cache[ticker][1].get("price", 0)
        else:
            try:
                ticker_obj = yf.Ticker(ticker)
                hist = ticker_obj.history(period="1d")
                if not hist.empty:
                    price = float(hist['Close'].iloc[-1])
                else:
                    price = 0
                cache[ticker] = (current_time, {"price": price})
            except:
                price = 0
        
        enriched_stock = stock.copy()
        enriched_stock["price"] = price
        response_data.append(enriched_stock)
        
    update_time_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    return jsonify({
        "data": response_data,
        "update_time": update_time_str
    })

# 2. 신규 추가 종목 실시간 검색 및 배당 데이터 완벽 추출
@app.route('/api/stock')
def get_single_stock():
    symbol = request.args.get('symbol', '').upper().strip()
    if not symbol:
        return jsonify({"error": "종목 코드가 없습니다."}), 400
        
    current_time = time.time()
    
    if symbol in cache and (current_time - cache[symbol][0] < CACHE_TTL) and "rate" in cache[symbol][1]:
        return jsonify(cache[symbol][1])
        
    try:
        ticker_obj = yf.Ticker(symbol)
        hist = ticker_obj.history(period="1d")
        if not hist.empty:
            price = float(hist['Close'].iloc[-1])
        else:
            price = 0.0
        
        info = ticker_obj.info
        
        # [핵심 로직] 확실한 배당률 계산 (퍼센트 오류 원천 차단)
        dividend_rate_amount = info.get('dividendRate', 0)
        if not dividend_rate_amount:
            dividend_rate_amount = info.get('trailingAnnualDividendRate', 0)
        
        if dividend_rate_amount and price > 0:
            # 배당금을 주가로 직접 나눠서 깔끔하게 퍼센트 산출
            rate_percent = round((dividend_rate_amount / price) * 100, 2)
        else:
            # 만약 배당금 정보 자체가 없으면 기존 방식 채택
            rate_fallback = info.get('dividendYield', 0)
            if not rate_fallback:
                rate_fallback = info.get('trailingAnnualDividendYield', 0)
            rate_percent = round(rate_fallback * 100, 2) if rate_fallback else 0.0
        
        short_name = info.get('shortName', symbol)
        summary = info.get('longBusinessSummary', '실시간으로 추가된 검색 종목입니다.')
        if summary and len(summary) > 50:
            summary = summary[:50] + "..."
            
        stock_data = {
            "ticker": symbol,
            "price": price,
            "rate": rate_percent,
            "name": "{0} ({1})".format(short_name, symbol),
            "desc": summary,
            "period": "월배당" if rate_percent > 7.0 else "분기배당",
            "months": "매달" if rate_percent > 7.0 else "3, 6, 9, 12월"
        }
        
        cache[symbol] = (current_time, stock_data)
        return jsonify(stock_data)
    except Exception as e:
        return jsonify({"error": "종목을 찾을 수 없거나 실패했습니다: {0}".format(str(e))}), 500
    

@app.route('/api/search_ticker')
def search_ticker():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"quotes": []})
        
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # 💡 이렇게 params로 넘겨주면 파이썬이 알아서 한글을 완벽하게 인코딩해서 야후로 보내줘!
    params = {'q': query, 'quotesCount': 10, 'newsCount': 0}
    
    try:
        res = requests.get(url, headers=headers, params=params)
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": "통신 에러"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
