from src.strategy.interface import Strategy
from src.db import DB_PATH, create_table
import sqlite3

conn = sqlite3.connect(DB_PATH)


class MaPare(Strategy):
    def __init__(self, short_term, long_term, balance):
        """
        :param short_term: 단기 이평선 기간
        :param long_term: 장기 이평선 기간
        :param balance: 계좌 잔액
        """
        self.short_term = short_term
        self.long_term = long_term
        self.init_balance = balance
        self.current_balance = balance
        self.amount = None
        self.init = True
        self.in_position = False
        with conn:
            c = conn.cursor()
            c.execute(
                "INSERT OR REPLACE INTO trades (short_term, long_term, balance, returns) VALUES (?, ?, ?, ?)",
                (self.short_term, self.long_term, self.init_balance, 0))
            conn.commit()

    def check_signal(self, price_queue):
        """
        골드/데드 크로스 체크 후 매수/매도
        :param price_queue: 가격 데이터 queue
        :return:
        """
        # print(f"{price_queue[-1]}")
        # queue에 충분한 데이터가 있을 경우에만 계산
        if len(price_queue) >= self.long_term:
            short_term_ma = price_queue[(-1 * self.short_term):].mean()
            long_term_ma = price_queue[(-1 * self.long_term):].mean()

            print(f"ma{self.short_term}: {short_term_ma},ma{self.long_term}: {long_term_ma}, price_memory: {len(price_queue)}")

            # 연산 시점부터 이미 단기 이평선이 장기 이평선보다 높은 경우(골든 크로스) 바로 매수하는 것을 방지
            if self.init:
                if short_term_ma < long_term_ma:
                    self.init = False
            else:
                current_price = price_queue[-1]
                if not self.in_position and short_term_ma > long_term_ma:
                    print(f"Strategy {self.short_term},{self.long_term}: buy")
                    # 골든 크로스 발생, 매수 진행
                    self.in_position = True
                    self.buy()
                elif self.in_position and short_term_ma < long_term_ma:
                    print(f"Strategy {self.short_term},{self.long_term}: sell")
                    # 데드 크로스 발생, 매도 진행
                    self.in_position = False
                    self.sell()

    def buy(self, current_price):
        buy_price = current_price
        self.amount = self.current_balance / buy_price
        self.current_balance -= (buy_price * self.amount)
        print(f"buy at price: {buy_price}, amount: {self.amount},balance: {self.balance}")

    def sell(self, current_price):
        sell_price = current_price
        self.current_balance += (sell_price * self.amount)
        print(f"sell at price: {sell_price}, amount: {self.amount}, balance: {self.balance}")
        self.amount = 0
        returns = (self.current_balance - self.init_balance) * 100 / self.init_balance
        with conn:
            c = conn.cursor()
            c.execute(
                "INSERT OR REPLACE INTO trades (short_term, long_term, balance, returns) VALUES (?, ?, ?, ?)",
                (self.short_term, self.long_term, self.current_balance, returns))
            conn.commit()

