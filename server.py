from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import time
from datetime import datetime, timedelta
import requests
import warnings

# SSL 인증서 경고 숨기기
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# --- (기존 DIVIDEND_STOCKS 및 get_all_stocks, get_single_stock 로직은 유지) ---
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
    if not symbol: return jsonify({"error": "종목 코드가 없습니다."}), 400
        
    current_time = time.time()
    if symbol in cache and (current_time - cache[symbol][0] < CACHE_TTL) and "rate" in cache[symbol][1]:
        return jsonify(cache[symbol][1])
        
    try:
        ticker_obj = yf.Ticker(symbol)
        hist = ticker_obj.history(period="1d")
        price = float(hist['Close'].iloc[-1]) if not hist.empty else 0.0
        
        info = ticker_obj.info
        dividend_rate_amount = info.get('dividendRate', 0) or info.get('trailingAnnualDividendRate', 0)
        
        if dividend_rate_amount and price > 0:
            rate_percent = round((dividend_rate_amount / price) * 100, 2)
        else:
            rate_fallback = info.get('dividendYield', 0) or info.get('trailingAnnualDividendYield', 0)
            rate_percent = round(rate_fallback * 100, 2) if rate_fallback else 0.0
        
        # 8214% 같은 야후 오류 방어
        if rate_percent > 50.0: rate_percent = 0.0 
        
        short_name = info.get('shortName', symbol)
        summary = info.get('longBusinessSummary', '실시간으로 추가된 검색 종목입니다.')
        if summary and len(summary) > 50: summary = summary[:50] + "..."
            
        stock_data = {
            "ticker": symbol, "price": price, "rate": rate_percent,
            "name": "{0} ({1})".format(short_name, symbol), "desc": summary,
            "period": "월배당" if rate_percent > 7.0 else "분기배당",
            "months": "매달" if rate_percent > 7.0 else "3, 6, 9, 12월"
        }
        cache[symbol] = (current_time, stock_data)
        return jsonify(stock_data)
    except Exception as e:
        return jsonify({"error": "종목을 찾을 수 없거나 실패했습니다: {0}".format(str(e))}), 500
    
# =========================================================================
# 🚨 새봄이가 뚫어온 한국거래소(KRX) API 연동 마스터 데이터 로직 🚨
# =========================================================================
KRX_API_URL = "https://data-dbg.krx.co.kr/svc/apis/sto/stk_bydd_trd"
KRX_AUTH_KEY = "F27E4E2DC4564CD6980AC9310636425A392217F9"
cached_krx_master = []

def get_recent_biz_day():
    """KRX 데이터가 존재하는 가장 최근 영업일(평일)을 안전하게 계산"""
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    if yesterday.weekday() == 5: # 토요일이면 목/금요일로
        yesterday = today - timedelta(days=2)
    elif yesterday.weekday() == 6: # 일요일이면 금요일로
        yesterday = today - timedelta(days=3)
    return yesterday.strftime("%Y%m%d")

def update_krx_master_data():
    """서버 최초 구동 시 KRX 전체 종목을 1번만 싹 가져와서 저장해두는 함수"""
    global cached_krx_master
    basDd = get_recent_biz_day()
    
    headers = {
        "Authorization": "Bearer " + KRX_AUTH_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        # 공공 API 명세(InBlock_1)에 맞게 GET 파라미터 또는 POST JSON으로 시도
        res = requests.get(KRX_API_URL, headers=headers, params={"basDd": basDd}, verify=False, timeout=5)
        if res.status_code != 200 or "OutBlock_1" not in res.text:
            res = requests.post(KRX_API_URL, headers=headers, json={"basDd": basDd}, verify=False, timeout=5)
            
        out_block = res.json().get("OutBlock_1", [])
        new_master = []
        for item in out_block:
            code_str = item.get("ISU_CD", "")
            name = item.get("ISU_NM", "")
            mkt = item.get("MKT_NM", "")
            
            # KR7005930003 같은 12자리 표준코드에서 6자리 단축코드만 쏙 빼기
            short_code = code_str[3:9] if code_str.startswith("KR7") else code_str[:6]
            # 코스닥/코스피 야후 티커용 접미사 부여
            suffix = ".KQ" if "KOSDAQ" in mkt or "코스닥" in mkt else ".KS"
            
            new_master.append({
                "code": short_code,
                "ticker": short_code + suffix,
                "name": name
            })
            
        if new_master:
            cached_krx_master = new_master
            print("KRX 종목 마스터 업데이트 완료! 총 {0}개 (기준일: {1})".format(len(new_master), basDd))
    except Exception as e:
        print("KRX 마스터 데이터 갱신 실패:", str(e))

@app.route('/api/search_ticker')
def search_ticker():
    query = request.args.get('q', '').strip().lower()
    if not query:
        return jsonify({"quotes": []})
        
    quotes = []
    
    # 💡 1단계: 서버 메모리에 KRX 리스트가 없으면 최초 1회 다운로드!
    if not cached_krx_master:
        update_krx_master_data()
        
    # 💡 2단계: 네이버 안 거치고, 서버 메모리에서 빛의 속도로 초성/한글 검색!
    for stock in cached_krx_master:
        # 검색어가 이름이나 6자리 코드에 포함되어 있으면 매칭
        if query in stock["name"].lower() or query in stock["code"]:
            quotes.append({
                "shortname": stock["name"],
                "longname": stock["name"],
                "symbol": stock["ticker"],
                "exchange": "KOR"
            })
        if len(quotes) >= 15: # 너무 많이 나오면 렉 걸리니 15개 컷
            break
            
    # 💡 3단계: 국내 주식이 아니거나(예: AAPL 검색), 못 찾았으면 글로벌 야후 API로 우회 검색!
    if not quotes or query.isascii():
        try:
            yahoo_url = "https://query2.finance.yahoo.com/v1/finance/search"
            yahoo_params = {'q': query, 'quotesCount': 10, 'newsCount': 0}
            yahoo_res = requests.get(yahoo_url, params=yahoo_params, headers={'User-Agent': 'Mozilla/5.0'}, timeout=3)
            yahoo_data = yahoo_res.json()
            
            if 'quotes' in yahoo_data:
                for q in yahoo_data['quotes']:
                    if q.get('symbol') not in [x['symbol'] for x in quotes]:
                        quotes.append(q)
        except Exception as e:
            print("Yahoo API 검색 에러:", str(e))

    return jsonify({"quotes": quotes})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
