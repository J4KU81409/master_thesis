import pandas as pd 
from cointegration_functions import * 
from kalman_functions import *

stocks_1990_2025 = pd.read_csv("./stocks_1990_2025.csv", index_col = 0)

# First run without transaction costs
# Cointegration Hossein 
"""
backtest_cointegration_returns_nocost, backtest_cointegration_tradecount_nocost  = run_strategy_hossein(stocks_1990_2025, useTransactionCosts=False)
backtest_cointegration_returns_nocost.to_csv("./results/backtest_cointegration_returns_nocost.csv")
backtest_cointegration_tradecount_nocost.to_csv("./results/backtest_cointegration_tradecount_nocost.csv")

# Kalman method 
backtest_kalman_returns_nocost, backtest_kalman_tradecount_nocost  = run_strategy_kalman(stocks_1990_2025, useTransactionCosts=False)
backtest_kalman_returns_nocost.to_csv("./results/backtest_kalman_returns_nocost.csv")
backtest_kalman_tradecount_nocost.to_csv("./results/backtest_kalman_tradecount_nocost.csv")


# Then run including transaction costs 
backtest_cointegration_returns, backtest_cointegration_tradecount  = run_strategy_hossein(stocks_1990_2025, useTransactionCosts=True)
backtest_cointegration_returns.to_csv("./results/backtest_cointegration_returns.csv")
backtest_cointegration_tradecount.to_csv("./results/backtest_cointegration_tradecount.csv")
""" 
# Kalman method
backtest_kalman_returns, backtest_kalman_tradecount = run_strategy_kalman(stocks_1990_2025, useTransactionCosts=True)
backtest_kalman_returns.to_csv("./results/backtest_kalman_returns.csv")
backtest_kalman_tradecount.to_csv("./results/backtest_kalman_tradecount.csv")
