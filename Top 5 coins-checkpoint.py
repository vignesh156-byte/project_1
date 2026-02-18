import streamlit as st
import pandas as pd
import mysql.connector
import datetime

st.title("💎 Top Cryptocurrency Analysis")

# ---------------- DATABASE CONNECTION ----------------

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="test"
)

# ---------------- GET TOP 3 COINS ----------------

top_coins_query = """
SELECT id
FROM coins_df
ORDER BY market_cap DESC
LIMIT 3
"""

top_coins_df = pd.read_sql(top_coins_query, conn)

coin_list = top_coins_df["id"].tolist()

# ---------------- COIN SELECTION ----------------

selected_coin = st.selectbox(
    "Select Cryptocurrency",
    coin_list
)

# ---------------- DATE FILTER ----------------

st.subheader("📅 Select Date Range")

today = datetime.date.today()

date_range = st.date_input(
    "Choose start and end dates",
    (today - datetime.timedelta(days=365), today)
)

# ---------------- SHOW DATA ----------------

if len(date_range) == 2:

    start_date, end_date = date_range

    query = """
    SELECT date, price_inr
    FROM merged_df
    WHERE coin_id = %s
      AND date BETWEEN %s AND %s
    ORDER BY date
    """

    df = pd.read_sql(
        query,
        conn,
        params=(selected_coin, start_date, end_date)
    )

    st.subheader(f"📊 Daily Price Data — {selected_coin.upper()}")

    # -------- TABLE --------
    st.dataframe(df)

    # -------- OPTIONAL CHART --------
    if not df.empty:
        st.subheader("📈 Daily Price Trend")

        df["date"] = pd.to_datetime(df["date"])
        st.line_chart(df.set_index("date"))

conn.close()