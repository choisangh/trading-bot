import asyncio
import json
import websockets
import sqlite3
from src.strategy.ma import MaPare
import numpy as np
from src.db import DB_PATH, create_table
import sqlite3

conn = sqlite3.connect(DB_PATH)

create_table()

price_queue = np.array([])
last_close_time = None  # 분봉 업데이트, push를 위한 변수

async def push_price_queue(price, close_time):
    global price_queue, last_close_time
    if last_close_time and last_close_time == close_time:
        # 분봉 기준으로 같은 시간인 경우, 마지막 가격 데이터를 업데이트
        price_queue[-1] = price
    else:
        # 다른 시간인 경우, 새로운 가격 데이터를 추가
        price_queue = np.append(price_queue, price)
        last_close_time = close_time
    # 메모리 관리를 위해 price queue length가 MA 최대 시간 범위를 넘어선 경우 crop
    if len(price_queue) > 120:
        price_queue = price_queue[-120:]


async def handle_message(message, strategies):
    # 메시지 처리를 위한 콜백 함수
    message = json.loads(message)
    if message["e"] == "error":
        print(message["m"])
    elif message["e"] == "kline":
        # 가격 정보 업데이트
        close_time = message['k']['t']
        close_price = float(message['k']['c'])
        await push_price_queue(close_price, close_time)
        for strategy in strategies:
            strategy.check_signal(price_queue)  # 종가


async def run_ws(strategies):
    # 웹소켓 연결 생성
    uri = "wss://stream.binance.com:9443/ws/btcusdt@kline_1m"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                # 가격 정보를 수신하는 루프
                async for message in websocket:
                    await handle_message(message, strategies)
        except websockets.exceptions.ConnectionClosed:
            # 웹소켓 연결이 끊겼을 경우 재시도
            print("WebSocket connection closed. Reconnecting...")
            await asyncio.sleep(5)


async def main():
    # 전략풀 init
    strategies = [MaPare(a, a+10, 10000) for a in range(10, 111, 1)]

    # 웹소켓 실행을 위한 태스크 생성
    ws_task = asyncio.create_task(run_ws(strategies))

    # 메인 루프 실행
    await ws_task


if __name__ == "__main__":
    asyncio.run(main())