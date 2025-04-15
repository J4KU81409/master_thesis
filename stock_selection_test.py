import unittest
#from stock_selection_functions import*  

import pandas as pd
import numpy as np
from itertools import combinations
from tqdm import tqdm

def normalize(stocks: pd.DataFrame) -> pd.DataFrame:
    """
    Convert stock price series into cumulative return with 1 as a starting value.
    """
    # Only normalize using the first valid price (starting trading date differs for some stocks)
    first_valid = stocks.apply(lambda col: col[col.first_valid_index()])
    df_result = stocks/first_valid
    return df_result

def calculate_and_sort_ssd(stocks: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate sum of squared differences (SSD) for all unique pairs of stocks.

    Parameters:
    stocks : pd.DataFrame
        Normalized stock dataframe scaled to 1 at the start for each stock.

    Returns:
    pd.DataFrame
        Sorted dataframe containing all possible stock pairs with their SSD values.
    """

    stock_pairs = list(combinations(stocks.columns, 2))  # Unique stock pairs
    ssd_values = {}

    for ticker1, ticker2 in tqdm(stock_pairs, desc="Calculating SSDs"):
        
        # Assign stock price series 
        stock1, stock2 = stocks[ticker1], stocks[ticker2]
        
        # If the stock is not trading yet, skip this pair. 
        if stock1.isna().any() or stock2.isna().any():
            continue
        
        # Compute SSD 
        spread = stock1 - stock2
        ssd = np.sum(np.square(spread)) 

        # Store directly in a dictionary
        ssd_values[f"{ticker1}_{ticker2}"] = ssd  

    # Convert dictionary to DataFrame (much faster than appending)
    df_result = pd.DataFrame.from_dict(ssd_values, orient="index", columns=["SSD"])

    return df_result.sort_values(by="SSD")

class TestStockSelection(unittest.TestCase):

    def setUp(self):
        # Define the stocks_test as a class variable
        self.stocks_test = {
            "MSFT": [100, 105] * 50,
            "AAPL": [100] * 100,
        }
        self.stocks = pd.DataFrame(self.stocks_test)

    def test_normalize(self):
        result = list(normalize(self.stocks)['MSFT'][:2])
        self.assertEqual(result, [1.00,1.05])

    def test_calculate_and_sort_ssd(self):
        result = float(calculate_and_sort_ssd(normalize(self.stocks)).iloc[0].item())
        self.assertAlmostEqual(result, 0.125, delta = 0.00001)

if __name__ == '__main__':
  unittest.main()