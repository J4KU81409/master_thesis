import pandas as pd
import yfinance as yf


#Get the data of SP500 stocks for the past 10 years
webpage = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
tickers_df = webpage[0]

tickers = tickers_df['Symbol']
print(tickers)


stock_data = []
stock_data = yf.download(['AAPL','MSFT'],period="1y")
print(stock_data)