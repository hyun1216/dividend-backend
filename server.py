from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import datetime
import time

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

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

# 새로운 시간표 기반 캐시 저장소
global_cache = {"schedule_key": "", "display_time": "", "stocks": []}
single_stock_cache = {}

# 현재 시간이 어느 스케줄에 속하는지 계산하는 아주 똑똑한 함수
def get_current_schedule():
    now = datetime.datetime.now()
    current_minutes = now.hour * 60 + now.minute
    
    if current_minutes >= 1410:   # 23:30 이후
        target_h, target_m = 23, 30
        target_date = now
    elif current_minutes >= 900:  # 15:00 이후
        target_h, target_m = 15, 0
        target_date = now
    elif current_minutes >= 750:  # 12:30 이후
        target_h, target_m = 12, 30
        target_date = now
    elif current_minutes >= 570:  # 09:30 이후
        target_h, target_m = 9, 30
        target_date = now
    else:                         # 09:30 이전이면 어제 23:30 데이터 사용!
        target_h, target_m = 23, 30
        target_date = now - datetime.timedelta(days=1)
        
    schedule_key = "{0:04d}{1:02d}{2:02d}-{3:02d}{4:02d}".format(
        target_date.year, target_date.month, target_date.day, target_h, target_m)
    display_time = "{0}시 {1:02d}분".format(target_h, target_m)
    
    return schedule_key, display_time


@app.route('/api/stocks')
def get_all_stocks():
    global global_cache
    current_key, display_time = get_current_schedule()
    
    # 1. 만약 현재 시간표 키와 캐시 키가 똑같고, 데이터가 살아있다면? -> 야후에 안 물어보고 바로 0.1초 컷!
    if global_cache["schedule_key"] == current_key and len(global_cache["stocks"]) > 0:
        return jsonify({"update_time": display_time, "data": global_cache["stocks"]})
        
    # 2. 시간표가 넘어갔다면 (예: 12:29 -> 12:30) 새롭게 데이터를 긁어옵니다.
    response_data = []
    
    for stock in DIVIDEND_STOCKS:
        ticker = stock["ticker"]
        try:
            ticker_obj = yf.Ticker(ticker)
            hist = ticker_obj.history(period="1d")
            if not hist.empty:
                price = float(hist['Close'].iloc[-1])
            else:
                price = float(ticker_obj.fast_info['last_price'])
                
        except Exception as e:
            print("Error [{0}]: {1}".format(ticker, str(e)))
            # 에러가 나서 0원이 될 위기라면? 과거 캐시에 있던 가격을 끌어와서 0원 방어!
            old_stock = next((s for s in global_cache["stocks"] if s["ticker"] == ticker), None)
            price = old_stock["price"] if old_stock else 0
            
        enriched_stock = stock.copy()
        enriched_stock["price"] = price
        response_data.append(enriched_stock)
        
    # 데이터베이스 갱신
    global_cache["schedule_key"] = current_key
    global_cache["display_time"] = display_time
    global_cache["stocks"] = response_data
    
    return jsonify({"update_time": display_time, "data": response_data})


@app.route('/api/stock')
def get_single_stock():
    symbol = request.args.get('symbol', '').upper().strip()
    if not symbol:
        return jsonify({"error": "종목 코드가 없습니다."}), 400
        
    current_key, display_time = get_current_schedule()
    
    # 개별 검색도 동일하게 시간표 방어막 적용
    if symbol in single_stock_cache and single_stock_cache[symbol]["schedule_key"] == current_key:
        result = single_stock_cache[symbol]["data"].copy()
        result["update_time"] = display_time
        return jsonify(result)
        
    try:
        ticker_obj = yf.Ticker(symbol)
        hist = ticker_obj.history(period="1d")
        
        if not hist.empty:
            price = float(hist['Close'].iloc[-1])
        else:
            price = float(ticker_obj.fast_info['last_price'])
        
        info = ticker_obj.info
        rate = info.get('dividendYield', 0)
        if not rate:
            rate = info.get('trailingAnnualDividendYield', 0)
        
        rate_percent = round(rate * 100, 2) if rate else 0.0
        
        short_name = info.get('shortName', symbol)
        summary = info.get('longBusinessSummary', '실시간으로 추가된 검색 종목입니다.')
        if len(summary) > 50:
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
        
        if price > 0:
            single_stock_cache[symbol] = {"schedule_key": current_key, "data": stock_data}
            
        stock_data_return = stock_data.copy()
        stock_data_return["update_time"] = display_time
        return jsonify(stock_data_return)
        
    except Exception as e:
        return jsonify({"error": "종목을 찾을 수 없거나 실패했습니다: {0}".format(str(e))}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
