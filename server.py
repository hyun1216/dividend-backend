from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import time
from datetime import datetime
import requests
import urllib.request
import json
import ssl

# SSL 인증 에러 방지용
ssl._create_default_https_context = ssl._create_unverified_context

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
CACHE_TTL = 18000

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
                price = float(hist['Close'].iloc[-1]) if not hist.empty else 0
                cache[ticker] = (current_time, {"price": price})
            except:
                price = 0
        
        enriched_stock = stock.copy()
        enriched_stock["price"] = price
        response_data.append(enriched_stock)
        
    update_time_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    return jsonify({"data": response_data, "update_time": update_time_str})

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
        price = float(hist['Close'].iloc[-1]) if not hist.empty else 0.0
        
        info = ticker_obj.info
        
        dividend_rate_amount = info.get('dividendRate', 0) or info.get('trailingAnnualDividendRate', 0)
        rate_fallback = info.get('dividendYield', 0) or info.get('trailingAnnualDividendYield', 0)
        
        # 1차 배당률 계산
        if dividend_rate_amount and price > 0:
            rate_percent = round((dividend_rate_amount / price) * 100, 2)
        elif rate_fallback:
            rate_percent = round(rate_fallback * 100, 2)
        else:
            rate_percent = 0.0
            
        # 🚨 8214% 같은 야후 파이낸스 미친 오류 방어벽 🚨
        if rate_percent > 50.0: 
            if rate_fallback and round(rate_fallback * 100, 2) < 50.0:
                rate_percent = round(rate_fallback * 100, 2)
            else:
                rate_percent = 0.0 # 상식 밖의 수치는 성장주/데이터오류로 간주하여 0% 처리
        
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
    
KRX_API_URL = "https://data-dbg.krx.co.kr/svc/apis/sto/stk_bydd_trd"
KRX_AUTH_KEY = "F27E4E2DC4564CD6980AC9310636425A392217F9"

# 서버 메모리에 상장종목 마스터를 캐싱할 전역 변수
cached_krx_master = []

def update_krx_master_data():
    """KRX API를 찔러서 최근일자 기준 전 종목 코드와 이름을 가져와 캐싱하는 함수"""
    global cached_krx_master
    # Spec.docx 기준 basDd 파라미터가 필수이므로, 최근 평일 날짜(예: "20260623") 세팅
    # (매번 수동으로 바꾸기 번거로우면 서버 실행 시점의 날짜를 datetime으로 구해서 넣어줄 수도 있어!)
    payload = {"basDd": "20260623"} 
    
    req = urllib.request.Request(KRX_API_URL)
    req.add_header("Authorization", "Bearer " + KRX_AUTH_KEY)
    req.add_header("Content-Type", "application/json")
    req.data = json.dumps(payload).encode('utf-8')
    
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read()
            res_json = json.loads(res_body.decode('utf-8'))
            
            out_block = res_json.get("OutBlock_1", [])
            new_master = []
            for item in out_block:
                # ISU_CD(표준코드)에서 단축코드 6자리 추출 (보통 3~9번째 인덱스)
                # 예: KR7005930003 -> 005930
                code_str = item.get("ISU_CD", "")
                short_code = code_str[3:9] if code_str.startswith("KR7") else code_str[:6]
                
                new_master.append({
                    "code": short_code,
                    "name": item.get("ISU_NM")
                })
                
            if new_master:
                cached_krx_master = new_master
                print("KRX 종목 마스터 데이터 구축 완료: {0}개 종목".format(len(cached_krx_master)))
    except Exception as e:
        print("KRX 마스터 갱신 실패:", str(e))

@app.route('/api/search_krx_stock')
def search_krx_stock():
    """검색어(q)를 받아 cached_krx_master에서 일치하는 종목들을 반환하는 엔드포인트"""
    query = request.args.get('q', '').strip().lower()
    if not query or len(query) < 1:
        return jsonify({"results": []})
        
    # 서버 메모리에 마스터 데이터가 비어있다면 최초 1회 자동 구축
    if not cached_krx_master:
        update_krx_master_data()
        
    matches = []
    for stock in cached_krx_master:
        # 검색어가 종목명이나 종목코드(6자리)에 포함되어 있는지 확인 ("삼성" 또는 "005930" 매칭)
        if query in stock["name"].lower() or query in stock["code"].lower():
            # 코스피인지 코스닥인지 구분하여 .KS 또는 .KQ를 붙여줌
            # (유가증권 일별매매정보는 코스피 위주이므로 기본적으로 .KS를 결합)
            matches.append({
                "name": stock["name"],
                "ticker": stock["code"] + ".KS"
            })
            
        # 너무 많이 뜨면 화면이 복잡해지니 최대 10개로 제한
        if len(matches) >= 10:
            break
            
    return jsonify({"results": matches})

@app.route('/api/search_ticker')
def search_ticker():
    query = request.args.get('q', '')
    if not query:
        return jsonify({"quotes": []})
        
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    headers = {'User-Agent': 'Mozilla/5.0'}
    params = {'q': query, 'quotesCount': 10, 'newsCount': 0}
    
    try:
        res = requests.get(url, headers=headers, params=params)
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"error": "통신 에러"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
