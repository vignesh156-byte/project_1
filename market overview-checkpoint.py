import streamlit as st
import pandas as pd
import mysql.connector
import datetime

st.title("📊 Market Overview")

# DB connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="test"
)

# ---------- DATE FILTER ----------

today = datetime.date.today()

date_range = st.date_input(
    "Select date range",
    (today - datetime.timedelta(days=365), today)
)

if len(date_range) == 2:
    start_date, end_date = date_range

    # ---------- KPI QUERIES ----------

    btc_avg = pd.read_sql("""
        SELECT AVG(price_inr)
        FROM merged_df
        WHERE coin_id='bitcoin'
        AND date BETWEEN %s AND %s
    """, conn, params=(start_date, end_date)).iloc[0,0]

    oil_avg = pd.read_sql("""
        SELECT AVG(price_inr)
        FROM oil_sy
        WHERE date BETWEEN %s AND %s
    """, conn, params=(start_date, end_date)).iloc[0,0]

    sp_avg = pd.read_sql("""
        SELECT AVG(close)
        FROM stocks_df
        WHERE ticker='GSPC'
        AND date BETWEEN %s AND %s
    """, conn, params=(start_date, end_date)).iloc[0,0]

    nifty_avg = pd.read_sql("""
        SELECT AVG(close)
        FROM stocks_df
        WHERE ticker='NSEI'
        AND date BETWEEN %s AND %s
    """, conn, params=(start_date, end_date)).iloc[0,0]

    # ---------- DISPLAY KPIs ----------

    st.subheader("📈 Average Prices")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Bitcoin", f"{btc_avg:,.2f}" if btc_avg else "N/A")
    c2.metric("Oil", f"{oil_avg:,.2f}" if oil_avg else "N/A")
    c3.metric("S&P 500", f"{sp_avg:,.2f}" if sp_avg else "N/A")
    c4.metric("NIFTY", f"{nifty_avg:,.2f}" if nifty_avg else "N/A")

    # ---------- SNAPSHOT TABLE ----------

    st.subheader("📊 Daily Market Snapshot")

    snapshot = pd.read_sql("""
        SELECT
            b.date,
            b.price_inr AS bitcoin,
            o.price_inr AS oil,
            sp.close AS sp500,
            nf.close AS nifty
        FROM merged_df b
        JOIN oil_sy o ON b.date = o.date
        JOIN stocks_df sp ON b.date = sp.date AND sp.ticker='GSPC'
        JOIN stocks_df nf ON b.date = nf.date AND nf.ticker='NSEI'
        WHERE b.coin_id='bitcoin'
        AND b.date BETWEEN %s AND %s
        ORDER BY b.date
    """, conn, params=(start_date, end_date))

    st.dataframe(snapshot)

    if not snapshot.empty:
        st.line_chart(snapshot.set_index("date"))

conn.close()