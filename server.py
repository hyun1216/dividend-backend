from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import time
from datetime import datetime
import requests
import urllib.parse
import re
import warnings

# SSL 인증서 경고 숨기기
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# 기본 TOP 리스트
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
# 🚨 하드코딩 제로! 무적의 이중 방어 네이버 크롤링 + 야후 API 🚨
# =========================================================================
@app.route('/api/search_ticker')
def search_ticker():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({"quotes": []})
        
    quotes = []
    
    # 💡 브라우저 완벽 위장 (Render 서버 IP 차단 100% 회피용)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Referer': 'https://finance.naver.com/',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    # 1단계: 네이버 금융 실시간 자동완성 API (위장 헤더 장착 완료)
    try:
        naver_url = "https://ac.finance.naver.com/ac"
        naver_params = {
            'q': query, 'q_enc': 'utf-8', 'st': '111', 'r_format': 'json', 'r_enc': 'utf-8'
        }
        naver_res = requests.get(naver_url, params=naver_params, headers=headers, timeout=3)
        naver_data = naver_res.json()
        
        if 'items' in naver_data and len(naver_data['items']) > 0:
            for item in naver_data['items'][0]:
                if len(item) >= 2:
                    name = item[0]
                    code = item[1]
                    market = item[2] if len(item) > 2 else ""
                    # 코스닥이면 .KQ, 그 외엔 .KS 붙여주기
                    suffix = ".KQ" if "KOSDAQ" in market else ".KS"
                    
                    quotes.append({
                        "shortname": name,
                        "longname": name,
                        "symbol": code + suffix,
                        "exchange": "KOR"
                    })
    except Exception as e:
        print("네이버 API 통신 에러:", str(e))

    # 2단계: API가 튕기면, 무식하지만 100% 확실한 네이버 통합검색 화면 통째로 뜯어오기! (정규식 크롤링)
    if not quotes:
        try:
            encoded_query = urllib.parse.quote(query)
            search_url = "https://finance.naver.com/search/searchList.naver?query=" + encoded_query
            search_res = requests.get(search_url, headers=headers, timeout=3)
            
            # HTML 안에서 '<a href="/item/main.naver?code=005380">현대차</a>' 이 규칙만 찾아내서 6자리 빼오기
            pattern = re.compile(r'href="/item/main\.naver\?code=(\d{6})"[^>]*>([^<]+)</a>')
            matches = pattern.findall(search_res.text)
            
            seen_codes = set()
            for code, name in matches:
                name = name.strip()
                if code not in seen_codes:
                    seen_codes.add(code)
                    quotes.append({
                        "shortname": name,
                        "longname": name,
                        "symbol": code + ".KS",  # 웹 화면에선 시장 구분이 안 되므로 .KS를 기본값으로 부여
                        "exchange": "KOR"
                    })
                if len(quotes) >= 15:
                    break
        except Exception as e:
            print("네이버 웹 스크래핑 에러:", str(e))

    # 3단계: 못 찾았거나 영어(AAPL 등) 검색어일 때 야후로 넘기기
    if not quotes or query.isascii():
        try:
            yahoo_url = "https://query2.finance.yahoo.com/v1/finance/search"
            yahoo_params = {'q': query, 'quotesCount': 10, 'newsCount': 0}
            yahoo_res = requests.get(yahoo_url, params=yahoo_params, headers={'User-Agent': 'Mozilla/5.0'}, timeout=3)
            yahoo_data = yahoo_res.json()
            
            if 'quotes' in yahoo_data:
                for q in yahoo_data['quotes']:
                    # 중복되지 않는 것만 리스트에 넣기
                    if q.get('symbol') not in [x['symbol'] for x in quotes]:
                        quotes.append(q)
        except Exception as e:
            print("Yahoo API 검색 에러:", str(e))

    return jsonify({"quotes": quotes})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
