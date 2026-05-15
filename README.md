📊 Project Description — CMA (Cross-Market Analysis)
What This Project Does
This is a Cross-Market Financial Data Analysis project that collects, stores, and analyzes data from three major financial markets — Cryptocurrency, Crude Oil, and Stock Indices — to find patterns, trends, and correlations between them.

🔄 Data Pipeline (ETL)
SourceData CollectedTool UsedCoinGecko APITop 1250 cryptocurrencies (market cap, price, volume, ATH, ATL)requestsCoinGecko API365-day historical prices for Top 5 coins (BTC, ETH, Tether, BNB, XRP)requestsGitHub DatasetWTI Crude Oil daily prices (last 5 years)pandasYahoo FinanceStock indices — S&P 500, NASDAQ, Nifty 50 (2020–2026)yfinance
All data is stored in a MySQL database with 4 relational tables:
coins_df, merged_df (crypto prices), oil_sy, stocks_df

🔍 Analysis Performed (20+ SQL Queries)
Crypto: Top coins by market cap, coins near ATH, high-volume coins, circulating supply analysis
Oil: Highest/lowest prices, yearly average, annual volatility, biggest price crashes
Stocks: Highest closing prices, monthly averages, most volatile days, trading volume trends
Cross-Market Joins:

Bitcoin vs S&P 500 correlation
Ethereum vs NASDAQ price trend
Oil price spikes vs Bitcoin reaction
Top 3 crypto coins vs Nifty 50 normalized performance
Triple join: S&P 500 + Oil + Bitcoin daily comparison
