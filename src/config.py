import sqlite3
# 웹소켓 url
uri = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"

# DB 설정
conn = sqlite3.connect('returns.db')
c = conn.cursor()

# 수수료 설정

# 초기 Balance 설정

