import websocket
import json
import numpy as np
import threading

price_list = np.array([])
lock = threading.Lock()
class MaPool:
    def __init__(self, ma_min: int, ma_max: int):
        self.pool = {}
        for i in range(ma_min, ma_max+1):
            self.pool[f"ma_{i}"] = None

# 스레드에서 실행될 함수
def worker(i):
    global price_list
    while True:
        # 공유 리소스에 대한 락 획득
        lock.acquire()
        # 평균 계산
        mean_price = price_list[-i:].mean()
        # print(f"Thread {threading.current_thread().name} {i} : {mean_price}")
        # 공유 리소스에 대한 락 해제
        lock.release()


# WebSocket에서 데이터를 가져오는 함수
def on_message(ws, message):
    global price_list
    data = json.loads(message)
    print(data)
    timestamp = int(data['k']['t'])
    close_price = float(data['k']['c'])
    price_list = np.append(price_list, close_price)
    price_list = price_list[-120:]


if __name__ == '__main__':
    # 스레드 생성 및 실행
    for i in range(10):
        t = threading.Thread(target=worker, args=[i])
        t.start()

    # WebSocket 연결 설정
    ws = websocket.WebSocketApp('wss://stream.binance.com:9443/ws/btcusdt@kline_1m',
                                on_message=on_message)
    ws.run_forever()