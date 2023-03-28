import dash
from dash import dash_table
import pandas as pd
import sqlite3

# SQLite DB 연결
conn = sqlite3.connect('returns.db')

# 쿼리문 실행하여 데이터프레임 생성
df = pd.read_sql_query("SELECT * from trades", conn)

conn.close()

# Dash 애플리케이션 생성
app = dash.Dash(__name__)

# 데이터프레임을 출력하기 위한 테이블 생성
table = dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict('records'),
)

# 애플리케이션 레이아웃 설정
app.layout = table

if __name__ == '__main__':
    app.run_server(debug=True)