import streamlit as st
import pandas as pd
import mysql.connector


conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="test"
)


st.title("📊 Cross Market Analysis")
st.subheader("Crypto • Oil • Stocks Dashboard")

st.markdown("*Welcome* to **Cross Market Analysis** 🚀")

st.markdown("""
:red[We analyse] :green[Crypto] :blue[Oil] :violet[Stocks]
""")


queries = {

# ---------------- CRYPTO (coins_df + merged_df) ----------------

"1.Find the top 3 cryptocurrencies by market cap":
("""
SELECT name, symbol, market_cap
FROM coins_df
ORDER BY market_cap DESC
LIMIT 3
"""),

"2.List all coins where circulating supply exceeds 90% of total supply":
("""
SELECT name, symbol, circulating_supply, total_supply
FROM coins_df
WHERE circulating_supply >= 0.9 * total_supply
"""),

"3.Get coins that are within 10% of their all-time-high (ATH)":
("""
SELECT name, symbol, current_price, ath
FROM coins_df
WHERE current_price >= 0.9 * ath
"""),

"4.Find the average market cap rank of coins with volume above $1B":
("""
SELECT AVG(market_cap_rank) AS avg_rank
FROM coins_df
WHERE total_volume > 1000000000
"""),

"5.Get the most recently updated coin":
("""
SELECT *
FROM coins_df
ORDER BY date DESC
LIMIT 1
"""),

"6.Find the highest daily price of Bitcoin in the last 365 days":
("""
SELECT MAX(price_inr) AS highest_price_inr
FROM merged_df
WHERE coin_id = 'bitcoin'
  AND date >= CURDATE() - INTERVAL 365 DAY
"""),

"7.Calculate the average daily price of Ethereum in the past 1 year":
("""
SELECT AVG(price_inr) AS avg_price_inr
FROM merged_df
WHERE coin_id = 'ethereum'
  AND date >= CURDATE() - INTERVAL 365 DAY
"""),

"8.Show the daily price trend of Bitcoin in January 2025":
("""
SELECT date, price_inr
FROM merged_df
WHERE coin_id = 'bitcoin'
  AND date >= '2025-03-01'
  AND date <  '2025-04-01'
ORDER BY date
"""),

"9.Find the coin with the highest average price over 1 year":
("""
SELECT coin_id, AVG(price_inr) AS avg_price_inr
FROM merged_df
WHERE date >= CURDATE() - INTERVAL 365 DAY
GROUP BY coin_id
ORDER BY avg_price_inr DESC
LIMIT 1
"""),

"10.Get the % change in Bitcoin’s price between Sep 2024 and Sep 2025":
("""
SELECT
  ((sep.price_inr - start.price_inr) / start.price_inr) * 100 AS percent_change
FROM
  (SELECT price_inr
   FROM merged_df
   WHERE coin_id = 'bitcoin'
   ORDER BY date ASC
   LIMIT 1) AS start,
     
  (SELECT price_inr
   FROM merged_df
   WHERE coin_id = 'bitcoin'
     AND date >= '2025-09-01'
     AND date <  '2026-02-01'
   ORDER BY date DESC
   LIMIT 1) AS sep
"""),

# ---------------- OIL (oil_sy) ----------------

"11.Find the highest oil price in the last 5 years":
("""
SELECT MAX(price_inr) AS highest_price
FROM oil_sy
WHERE date >= CURDATE() - INTERVAL 5 YEAR
"""),

"12.Get the average oil price per year":
("""
SELECT 
    YEAR(date) AS year,
    AVG(price_inr) AS avg_price_inr
FROM oil_sy
GROUP BY YEAR(date)
ORDER BY year
"""),

"13.Show oil prices during COVID crash (March–April 2020)":
("""
SELECT 
    date,
    price_inr,
    LAG(price_inr) OVER (ORDER BY date) AS prev_price,
    ROUND(
        100 * (price_inr - LAG(price_inr) OVER (ORDER BY date)) 
        / LAG(price_inr) OVER (ORDER BY date),
        2
    ) AS pct_change
FROM oil_sy
ORDER BY pct_change ASC
LIMIT 10
"""),

"14.Find the lowest price of oil in the last 10 years":
("""
SELECT MIN(price_inr) AS lowest_price
FROM oil_sy
WHERE date >= CURDATE() - INTERVAL 10 YEAR
"""),

"15.Calculate the volatility of oil prices (max-min difference per year)":
("""
SELECT 
    YEAR(date) AS year,
    MAX(price_inr) AS max_price,
    MIN(price_inr) AS min_price,
    MAX(price_inr) - MIN(price_inr) AS volatility
FROM oil_sy
GROUP BY YEAR(date)
ORDER BY year
"""),

# ---------------- STOCKS (stocks_df) ----------------

"16.Get all stock prices for a given ticker":
("""
SELECT *
FROM stocks_df
WHERE ticker='NSEI'
ORDER BY date
"""),

"17.Find the highest closing price for NASDAQ (^IXIC)":
("""
SELECT MAX(close) AS highest_close
FROM stocks_df
WHERE ticker = 'IXIC'
"""),

"18.List top 5 days with highest price difference (high - low) for S&P 500 (^GSPC)":
("""
SELECT 
    date,
    high,
    low,
    high - low AS price_diff
FROM stocks_df
WHERE ticker = 'GSPC'
ORDER BY price_diff DESC
LIMIT 5
"""),

"19.Get monthly average closing price for each ticker":
("""
SELECT 
    ticker,
    YEAR(date) AS year,
    MONTH(date) AS month,
    AVG(close) AS avg_close
FROM stocks_df
GROUP BY ticker, YEAR(date), MONTH(date)
ORDER BY ticker, year, month
"""),

"20.Get average trading volume of NSEI in 2024":
("""
SELECT AVG(volume) AS avg_volume
FROM stocks_df
WHERE ticker = 'NSEI'
  AND YEAR(date) = 2024
"""),

# ---------------- CROSS-ASSET ----------------

"21.Compare Bitcoin vs Oil average price in 2025":
("""
SELECT
  (SELECT AVG(price_inr)
   FROM merged_df
   WHERE coin_id = 'bitcoin'
     AND YEAR(date) = 2025) AS bitcoin_avg_2025,

  (SELECT AVG(price_inr)
   FROM oil_sy
   WHERE YEAR(date) = 2025) AS oil_avg_2025
""")
,

"22.Check if Bitcoin moves with S&P 500 (correlation idea)":
("""
SELECT 
    b.date,
    b.price_inr AS btc_price,
    s.close AS sp500_close
FROM merged_df b
JOIN stocks_df s
  ON b.date = s.date
WHERE b.coin_id = 'bitcoin'
  AND s.ticker = 'GSPC'
ORDER BY b.date
"""),

"23.Compare Ethereum and NASDAQ daily prices for 2025":
("""
SELECT 
    c.date,
    c.price_inr AS eth_price,
    s.close AS nasdaq_close
FROM merged_df c
JOIN stocks_df s
  ON c.date = s.date
WHERE c.coin_id = 'ethereum'
  AND s.ticker = 'IXIC'
  AND YEAR(c.date) = 2025
ORDER BY c.date
"""),

"24.Find days when oil price spiked and compare with Bitcoin price change":
("""
SELECT *
FROM (
    SELECT 
        o.date,
        o.price_inr AS oil_price,

        ROUND(
            100 * (o.price_inr - LAG(o.price_inr) OVER (ORDER BY o.date))
            / LAG(o.price_inr) OVER (ORDER BY o.date),
            2
        ) AS oil_pct_change,

        b.price_inr AS btc_price,

        ROUND(
            100 * (b.price_inr - LAG(b.price_inr) OVER (ORDER BY b.date))
            / LAG(b.price_inr) OVER (ORDER BY b.date),
            2
        ) AS btc_pct_change

    FROM oil_sy o
    JOIN merged_df b
      ON o.date = b.date
    WHERE b.coin_id = 'bitcoin'
) t
WHERE oil_pct_change >= 5
ORDER BY date
"""),

"25.Compare top 3 coins daily price trend vs Nifty (^NSEI)":
("""
SELECT 
    c.date,
    c.coin_id,
    c.price_inr AS coin_price,
    s.close AS nifty_close
FROM merged_df c
JOIN stocks_df s
  ON c.date = s.date
WHERE c.coin_id IN ('bitcoin','ethereum','tether')
  AND s.ticker = 'NSEI'
ORDER BY c.date
"""),

"26.Compare stock prices (^GSPC) with crude oil prices on the same dates":
("""
SELECT 
    s.date,
    s.close AS sp500_close,
    o.price_inr AS oil_price
FROM stocks_df s
JOIN oil_sy o
  ON s.date = o.date
WHERE s.ticker = 'GSPC'
ORDER BY s.date
"""),

"27.Correlate Bitcoin closing price with crude oil closing price (same date)":
("""
SELECT 
    b.date,
    b.price_inr AS btc_price,
    o.price_inr AS oil_price
FROM merged_df b
JOIN oil_sy o
  ON b.date = o.date
WHERE b.coin_id = 'bitcoin'
ORDER BY b.date
"""),

"28.Compare NASDAQ (^IXIC) with Ethereum price trends":
("""
SELECT 
    c.date,
    c.price_inr AS eth_price,
    s.close AS nasdaq_close
FROM merged_df c
JOIN stocks_df s
  ON c.date = s.date
WHERE c.coin_id = 'ethereum'
  AND s.ticker = 'IXIC'
ORDER BY c.date
"""),

"29.Join top 3 crypto coins with stock indices for 2025":
("""
SELECT 
    c.date,
    c.coin_id AS asset,
    c.price_inr AS price,
    'crypto' AS asset_type
FROM merged_df c
WHERE c.coin_id IN ('bitcoin','ethereum','tether')
  AND YEAR(c.date) = 2025

UNION ALL

SELECT 
    s.date,
    s.ticker AS asset,
    s.close AS price,
    'stock_index' AS asset_type
FROM stocks_df s
WHERE s.ticker IN ('GSPC','IXIC','NSEI')
  AND YEAR(s.date) = 2025

ORDER BY date, asset;
"""),

"30.Multi-join: stock prices, oil prices, and Bitcoin prices for daily comparison":
("""
SELECT 
    s.date,
    s.close AS sp500_close,
    o.price_inr AS oil_price,
    b.price_inr AS btc_price

FROM stocks_df s
JOIN oil_sy o
  ON s.date = o.date
JOIN merged_df b
  ON s.date = b.date

WHERE s.ticker = 'GSPC'
  AND b.coin_id = 'bitcoin'

ORDER BY s.date
""")
}



option = st.selectbox(
    " Please select a query",
    list(queries.keys())
)

st.write("You selected:", option)


if st.button("Run Query"):

    sql = queries[option]

    df = pd.read_sql(sql, conn)

    st.subheader("📊 Result")

    st.dataframe(df)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        st.line_chart(df.set_index("date"))

conn.close()

