from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
import yfinance as yf
import time
from datetime import datetime, timedelta
import requests
import threading
import warnings
import os
import pymysql

# SSL 인증서 경고 숨기기
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# =========================================================================
# 🌐 화면 라우팅 (폴더 및 파일명 변경 반영 완료)
# =========================================================================
@app.route('/')
def calculator_page():
    return send_from_directory(app.root_path, 'index.html')

@app.route('/board')
def board_page():
    # board 폴더 안에 있는 index.html을 찾아가도록 수정!
    return send_from_directory(os.path.join(app.root_path, 'board'), 'index.html')

# =========================================================================
# 🗄️ DB 접속 설정 (포트 환경변수 추가 완료)
# =========================================================================
db_config = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'dividend'),
    'password': os.environ.get('DB_PASSWORD'), 
    'database': os.environ.get('DB_NAME', 'dividend'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
    'ssl': {'ca': None}  # 👈 이 옵션을 추가하면 SSL 요구사항을 맞춰서 연결해!
}

def get_db_connection():
    return pymysql.connect(**db_config)

def is_post_password_match(stored_password, input_password):
    if not stored_password or not input_password:
        return False

    try:
        if check_password_hash(stored_password, input_password):
            return True
    except ValueError:
        pass

    return stored_password == input_password

# =========================================================================
# 📈 주식 데이터 및 계산기 로직
# =========================================================================
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
    { "category": "us-etf", "ticker": "SPYI", "isUS": True, "period": "월배당", "months": "매달", "name": "SPYI", "rate": 11.65, "desc": "S&P 500 지수 옵션 선물 전략을 활용하는 양방향 투자 월배당 ETF" },
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
# 📝 배당금 인증 게시판 API 로직 
# =========================================================================

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """게시글 목록 불러오기"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    id,
                    nickname,
                    title,
                    content,
                    image_url,
                    likes,
                    DATE_FORMAT(created_at, '%Y-%m-%d %H:%i') AS created_at
                FROM board
                ORDER BY created_at DESC
            """)
            posts = cursor.fetchall()
            return jsonify(posts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals() and conn.open:
            conn.close()

@app.route('/api/posts', methods=['POST'])
def add_post():
    """새 게시글 작성하기"""
    data = request.get_json(silent=True) or {}
    nickname = (data.get('nickname') or '').strip()
    password = (data.get('password') or '').strip()
    title = (data.get('title') or '').strip()
    content = (data.get('content') or '').strip()
    image_url = (data.get('image_url') or '').strip()

    if not nickname or not password or not title or not content:
        return jsonify({"error": "닉네임, 비밀번호, 제목, 내용을 모두 입력해 주세요."}), 400

    if len(nickname) > 40:
        return jsonify({"error": "닉네임은 40자 이하로 입력해 주세요."}), 400

    if len(title) > 120:
        return jsonify({"error": "제목은 120자 이하로 입력해 주세요."}), 400

    if image_url and not image_url.startswith(("http://", "https://")):
        return jsonify({"error": "이미지 URL은 http:// 또는 https://로 시작해야 합니다."}), 400

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "INSERT INTO board (nickname, password, title, content, image_url) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (
                nickname,
                generate_password_hash(password),
                title,
                content,
                image_url or None
            ))
            conn.commit()
            return jsonify({"status": "success"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals() and conn.open:
            conn.close()

@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    """게시글 좋아요 누르기"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("UPDATE board SET likes = likes + 1 WHERE id = %s", (post_id,))
            if cursor.rowcount == 0:
                return jsonify({"error": "게시글을 찾을 수 없습니다."}), 404
            cursor.execute("SELECT likes FROM board WHERE id = %s", (post_id,))
            updated_post = cursor.fetchone()
            conn.commit()
            return jsonify({"status": "success", "likes": updated_post["likes"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals() and conn.open:
            conn.close()

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """작성 비밀번호 확인 후 게시글 삭제하기"""
    data = request.get_json(silent=True) or {}
    password = (data.get('password') or '').strip()

    if not password:
        return jsonify({"error": "삭제하려면 작성 비밀번호를 입력해 주세요."}), 400

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, password FROM board WHERE id = %s", (post_id,))
            post = cursor.fetchone()

            if not post:
                return jsonify({"error": "게시글을 찾을 수 없습니다."}), 404

            if not is_post_password_match(post["password"], password):
                return jsonify({"error": "비밀번호가 일치하지 않습니다."}), 403

            cursor.execute("DELETE FROM board WHERE id = %s", (post_id,))
            conn.commit()
            return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals() and conn.open:
            conn.close()

# =========================================================================
# 🚨 KRX API 연동 마스터 데이터 로직
# =========================================================================
KRX_API_URL = "https://data-dbg.krx.co.kr/svc/apis/sto/stk_bydd_trd"
KRX_AUTH_KEY = "F27E4E2DC4564CD6980AC9310636425A392217F9"
cached_krx_master = []

BUILTIN_KR_STOCKS = [
    {"code": "005930", "ticker": "005930.KS", "name": "삼성전자"},
    {"code": "005935", "ticker": "005935.KS", "name": "삼성전자우"},
    {"code": "000660", "ticker": "000660.KS", "name": "SK하이닉스"},
    {"code": "035420", "ticker": "035420.KS", "name": "NAVER"},
    {"code": "035720", "ticker": "035720.KS", "name": "카카오"},
    {"code": "005380", "ticker": "005380.KS", "name": "현대차"},
    {"code": "005387", "ticker": "005387.KS", "name": "현대차2우B"},
    {"code": "005385", "ticker": "005385.KS", "name": "현대차우"},
    {"code": "051910", "ticker": "051910.KS", "name": "LG화학"},
    {"code": "066570", "ticker": "066570.KS", "name": "LG전자"},
    {"code": "066575", "ticker": "066575.KS", "name": "LG전자우"},
    {"code": "055550", "ticker": "055550.KS", "name": "신한지주"},
    {"code": "105560", "ticker": "105560.KS", "name": "KB금융"},
    {"code": "086790", "ticker": "086790.KS", "name": "하나금융지주"},
    {"code": "316140", "ticker": "316140.KS", "name": "우리금융지주"},
    {"code": "032830", "ticker": "032830.KS", "name": "삼성생명"},
    {"code": "017670", "ticker": "017670.KS", "name": "SK텔레콤"},
    {"code": "030200", "ticker": "030200.KS", "name": "KT"},
    {"code": "032640", "ticker": "032640.KS", "name": "LG유플러스"},
    {"code": "003550", "ticker": "003550.KS", "name": "LG"},
    {"code": "034220", "ticker": "034220.KS", "name": "LG디스플레이"},
    {"code": "018260", "ticker": "018260.KS", "name": "삼성에스디에스"},
    {"code": "028260", "ticker": "028260.KS", "name": "삼성물산"},
    {"code": "000810", "ticker": "000810.KS", "name": "삼성화재"},
    {"code": "009150", "ticker": "009150.KS", "name": "삼성전기"},
    {"code": "088980", "ticker": "088980.KS", "name": "맥쿼리인프라"},
    {"code": "012330", "ticker": "012330.KS", "name": "현대모비스"},
    {"code": "006400", "ticker": "006400.KS", "name": "삼성SDI"},
    {"code": "207940", "ticker": "207940.KS", "name": "삼성바이오로직스"},
    {"code": "068270", "ticker": "068270.KS", "name": "셀트리온"},
    {"code": "096770", "ticker": "096770.KS", "name": "SK이노베이션"},
    {"code": "034730", "ticker": "034730.KS", "name": "SK"},
    {"code": "011200", "ticker": "011200.KS", "name": "HMM"},
    {"code": "010950", "ticker": "010950.KS", "name": "S-Oil"},
    {"code": "000270", "ticker": "000270.KS", "name": "기아"},
    {"code": "015760", "ticker": "015760.KS", "name": "한국전력"},
    {"code": "003490", "ticker": "003490.KS", "name": "대한항공"},
    {"code": "047050", "ticker": "047050.KS", "name": "포스코인터내셔널"},
    {"code": "005490", "ticker": "005490.KS", "name": "POSCO홀딩스"},
    {"code": "000100", "ticker": "000100.KS", "name": "유한양행"},
    {"code": "090430", "ticker": "090430.KS", "name": "아모레퍼시픽"},
    {"code": "033780", "ticker": "033780.KS", "name": "KT&G"},
    {"code": "004020", "ticker": "004020.KS", "name": "현대제철"},
    {"code": "138040", "ticker": "138040.KS", "name": "메리츠금융지주"},
    {"code": "267250", "ticker": "267250.KS", "name": "HD현대"},
    {"code": "042660", "ticker": "042660.KS", "name": "한화오션"},
    {"code": "009830", "ticker": "009830.KS", "name": "한화솔루션"},
    {"code": "000720", "ticker": "000720.KS", "name": "현대건설"},
    {"code": "011780", "ticker": "011780.KS", "name": "금호석유"},
    {"code": "071050", "ticker": "071050.KS", "name": "한국금융지주"},
    {"code": "000815", "ticker": "000815.KS", "name": "삼성화재우"},
    {"code": "009155", "ticker": "009155.KS", "name": "삼성전기우"},
    {"code": "034725", "ticker": "034725.KS", "name": "SK우"},
    {"code": "096775", "ticker": "096775.KS", "name": "SK이노베이션우"},
    {"code": "051915", "ticker": "051915.KS", "name": "LG화학우"},
    {"code": "446720", "ticker": "446720.KS", "name": "SOL 미국배당다우존스"},
    {"code": "458730", "ticker": "458730.KS", "name": "TIGER 미국배당다우존스"},
    {"code": "461250", "ticker": "461250.KS", "name": "ACE 미국배당다우존스"},
    {"code": "360200", "ticker": "360200.KS", "name": "TIGER 미국배당+3%프리미엄다우존스"},
    {"code": "458760", "ticker": "458760.KS", "name": "TIGER 미국배당+7%프리미엄다우존스"},
    {"code": "447770", "ticker": "447770.KS", "name": "KODEX 미국배당커버드콜액티브"},
    {"code": "476080", "ticker": "476080.KS", "name": "TIME Korea플러스배당액티브"},
    {"code": "161510", "ticker": "161510.KS", "name": "PLUS 고배당주"},
    {"code": "479620", "ticker": "479620.KS", "name": "KODEX 200타겟위클리커버드콜"},
    {"code": "474220", "ticker": "474220.KS", "name": "SOL 코리아고배당"},
    {"code": "379800", "ticker": "379800.KS", "name": "KODEX 미국S&P500TR"},
    {"code": "379810", "ticker": "379810.KS", "name": "KODEX 미국나스닥100TR"},
]

def get_recent_biz_day():
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    if yesterday.weekday() == 5:
        yesterday = today - timedelta(days=2)
    elif yesterday.weekday() == 6:
        yesterday = today - timedelta(days=3)
    return yesterday.strftime("%Y%m%d")

def update_krx_master_data():
    global cached_krx_master
    basDd = get_recent_biz_day()
    
    headers = {
        "Authorization": "Bearer " + KRX_AUTH_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        res = requests.get(KRX_API_URL, headers=headers, params={"basDd": basDd}, verify=False, timeout=8)
        if res.status_code != 200 or "OutBlock_1" not in res.text:
            res = requests.post(KRX_API_URL, headers=headers, json={"basDd": basDd}, verify=False, timeout=8)
            
        out_block = res.json().get("OutBlock_1", [])
        new_master = []
        for item in out_block:
            code_str = item.get("ISU_CD", "")
            name = item.get("ISU_NM", "")
            mkt = item.get("MKT_NM", "")
            short_code = code_str[3:9] if code_str.startswith("KR7") else code_str[:6]
            suffix = ".KQ" if "KOSDAQ" in mkt or "코스닥" in mkt else ".KS"
            new_master.append({
                "code": short_code,
                "ticker": short_code + suffix,
                "name": name
            })
            
        if new_master:
            cached_krx_master = new_master
            print("✅ KRX 종목 마스터 업데이트 완료! 총 {0}개 (기준일: {1})".format(len(new_master), basDd))
        else:
            print("⚠️ KRX 응답은 왔지만 종목 데이터가 비어있음. 내장 사전으로 대체.")
            cached_krx_master = BUILTIN_KR_STOCKS
    except Exception as e:
        print("⚠️ KRX 마스터 데이터 갱신 실패 (내장 사전 연결): " + str(e))
        if not cached_krx_master:
            cached_krx_master = BUILTIN_KR_STOCKS

threading.Thread(target=update_krx_master_data, daemon=True).start()

@app.route('/api/search_ticker')
def search_ticker():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({"quotes": []})
    
    query_lower = query.lower() 
    quotes = []
    
    search_pool = cached_krx_master if cached_krx_master else BUILTIN_KR_STOCKS
    for stock in search_pool:
        name_match = query in stock["name"]              
        code_match = query_lower in stock["code"]        
        ticker_match = query_lower in stock["ticker"].lower()  
        
        if name_match or code_match or ticker_match:
            quotes.append({
                "shortname": stock["name"],
                "longname": stock["name"],
                "symbol": stock["ticker"],
                "exchange": "KOR"
            })
        if len(quotes) >= 15:
            break
    
    if query_lower.isascii() or not quotes:
        try:
            yahoo_url = "https://query2.finance.yahoo.com/v1/finance/search"
            yahoo_params = {'q': query, 'quotesCount': 10, 'newsCount': 0}
            yahoo_res = requests.get(
                yahoo_url, params=yahoo_params,
                headers={'User-Agent': 'Mozilla/5.0'}, timeout=3
            )
            yahoo_data = yahoo_res.json()
            
            existing_symbols = {x['symbol'] for x in quotes}
            if 'quotes' in yahoo_data:
                for q in yahoo_data['quotes']:
                    if q.get('symbol') not in existing_symbols:
                        quotes.append(q)
        except Exception as e:
            print("Yahoo API 검색 에러:", str(e))

    return jsonify({"quotes": quotes})

# =========================================================================
# 🛠️ 테이블 자동 생성 API (최초 1회 셋업용)
# =========================================================================
@app.route('/api/init_db')
def init_db():
    """최초 1회 실행: DB에 게시판 테이블을 생성합니다."""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS board (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nickname VARCHAR(40) NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    title VARCHAR(120) NOT NULL,
                    content TEXT NOT NULL,
                    image_url VARCHAR(255),
                    likes INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        return jsonify({"message": "✅ 게시판 테이블 세팅이 완벽하게 끝났습니다! 이제 게시판을 맘껏 즐겨보세요."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
