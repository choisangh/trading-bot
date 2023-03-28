import sqlite3
# DB 설정
DB_PATH = 'returns.db'


def create_table():
    conn = sqlite3.connect(DB_PATH)
    with conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS trades
                         (short_term INTEGER NOT NULL,
                          long_term INTEGER NOT NULL,
                          balance TEXT NOT NULL,
                          returns REAL NOT NULL,
                          PRIMARY KEY (short_term, long_term))''')

        conn.commit()

