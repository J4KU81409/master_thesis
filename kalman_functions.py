import numpy as np
import pandas as pd
from pykalman import KalmanFilter
import matplotlib.pyplot as plt
import statsmodels.api as sm
from cointegration_functions import *



def estimate_model(stocks_formation, portfolio):
    """
    Parameters: should be portfolio and stocks formation, 
    Y observed is defined as logx1 - logx2.
    Takes formation period spread (= observed y) and learns the parameters of the state-observation model (A,B,C,D) using EM algorithm.
    Estimates the model for each pair of the trading portfolio in the formation period.
    """
    portfolio_models = pd.DataFrame(columns=["A", "B", "C", "D"])

    for pair in portfolio.index:
        
        stock1, stock2 = pair.split("_")
        print("processing pair ", stock1, "and", stock2)

        data = pd.concat([stocks_formation[stock1], stocks_formation[stock2]], axis=1).dropna()  # Drop NaN values
        x = data[stock1]  # No sm.add_constant()
        y = data[stock2]
        
        model = sm.OLS(y,x).fit()
        y_obs = pd.Series(model.resid) #spread = P2 - beta * P1. 
        
        # Define the Kalman Filter
        kf = KalmanFilter(
            n_dim_obs=1, 
            n_dim_state=1, 
            em_vars=['transition_matrices', 'transition_offsets', 
                    'transition_covariance', 'observation_covariance']
        )

        print("estimating model....")

        # Estimate Parameters Using EM
        kf = kf.em(y_obs, n_iter=20)

        # Extract Learned Parameters
        A_est = kf.transition_offsets       # Estimated A
        B_est = kf.transition_matrices      # Estimated B
        C_est = np.sqrt(kf.transition_covariance)  # Estimated C (since Q = C^2)
        D_est = np.sqrt(kf.observation_covariance)  # Estimated D (since R = D^2)


        portfolio_models.loc[pair, "A"] = A_est.item()
        portfolio_models.loc[pair, "B"] = B_est.item()
        portfolio_models.loc[pair, "C"] = C_est.item()
        portfolio_models.loc[pair, "D"] = D_est.item()
        portfolio_models.loc[pair, "beta"] = model.params.iloc[0]
        print("params of the spread for :", pair, "are ", A_est.item(), B_est.item(), C_est.item(), D_est.item(), model.params.iloc[0])
      
        
    return portfolio_models


def trade_portfolio_kalman(portfolio_models: pd.DataFrame, stocks_trading: pd.DataFrame, useTransactionCosts: bool = False, transaction_cost: float = 0.006, threshold_factor: float = 1.0):
    """ 
    This performs the recursive kalman filter based on the parameterss A,B,C,D state-observation model estimated before.
    Takes the trading period stocks and performs the trading algorithm 
    """
    result_df = pd.DataFrame(index = stocks_trading.index)
    x_est_df = pd.DataFrame(index = stocks_trading.index)
    R_est_df = pd.DataFrame(index = stocks_trading.index)
    y_obs_df = pd.DataFrame(index = stocks_trading.index)
    trade_counts_df = pd.DataFrame(index = stocks_trading.index)

    n_diverged = 0
    
    
    # Process each pair
    for pair in portfolio_models.index:
        entered_trade = False
        stock1, stock2 = pair.split("_")

        print("proccesing pair: \n",  pair, "\n", 100*"-")
        A,B,C,D,beta = portfolio_models.loc[pair]
       
        # Spread for a given pair 
        y_obs = stocks_trading[stock2] - beta * stocks_trading[stock1]
       
        # x0 = y0 
        x_est = [y_obs.iloc[0]]  
        R_est = [D**2]
        K_hist  = [(B**2) * R_est[-1] + C**2  / ((B**2) * R_est[-1] + C**2 + D**2)]

        print("Params A,B,C,D are", A,B,C,D)
        
        pair_result = {}
        spread_t = 0
        pair_result[y_obs.index[0]] = 0.0
        
        print("Current observed spread is: ",  y_obs.iloc[0], "and Current filtered spread is", x_est[0])
        
        # Direction variable 1 long -1 short 
        direction = 0
        n_trades = 0 
        # proces spread each day for this pair 
        for i in range(1, len(y_obs.index)):
            
            date = stocks_trading.index[i]

            # y observed
            observed_y = y_obs.iloc[i] 

            # Kalman Filter recursion
            x = A + B * x_est[-1]
            R = (B**2) * R_est[-1] + C**2
            K = R / (R + D**2)
            x_hat = x + K * (observed_y - x)
            R_hat = R - K*R  #(D**2) * K
            
            x_est.append(x_hat)
            R_est.append(R_hat)
            K_hist.append(K)

            print(40*"-", "\nprocessing date", date)
            print("Current observed spread is: ",  y_obs.iloc[i], "and Current filtered spread is", x_est[i])
            # trade logic here, we compare prediction and signal 
            threshold = np.sqrt(R_hat) * threshold_factor # threshold to enter the trade
            
            # Entering trade
            if observed_y > x_hat + threshold and not entered_trade:
                #observed spread is too large, enter trade 
                print("Observed spread ", observed_y ," is too big, short trade entered...")
                spread_t = observed_y
                direction = -1
                n_trades += 1
                entered_trade = True
            
            elif observed_y < x_hat - threshold and not entered_trade:
                # observed spread is too small, enter trade 
                print("Observed spread is too small, long trade entered...")
                spread_t = observed_y
                direction = +1
                n_trades += 1
                entered_trade = True

            # Closing Trade
            # current spread drops below the estimate -+ threshold, exit and save delta_spread = spread_t+n - spread_t
            if direction == -1 and observed_y < x_hat - threshold  and entered_trade:
                entered_trade = False  
                spread_diff = observed_y - spread_t
                delta_spread = direction * spread_diff
                print("Short trade was exited...return is :", delta_spread)    
                
            elif direction == +1 and observed_y > x_hat + threshold and entered_trade:
                entered_trade = False 
                spread_diff = observed_y - spread_t
                delta_spread = direction * spread_diff
                print("Long trade was exited...return is :", delta_spread)    
            else: 
                # if trade is not entered or spread of the entered trade did not return to 0
                delta_spread = 0.0 

            #last day of trading
            if i == len(y_obs.index) - 1:
                date = stocks_trading.index[i]
                print("\n LAST DAY OF THE TRADING....", date)
                print("Last observed spread is:", observed_y, "and last filtered spread is:", x_est[i])

                if entered_trade:
                    spread_diff = observed_y - spread_t
                    print("Brute force close - observed vs. entry:", observed_y, spread_t)

                    # Determine profit/loss based on trade direction
                    delta_spread = direction * spread_diff
                    print("Final delta_spread:", delta_spread)

                    if delta_spread < 0:
                        n_diverged += 1

            # Save the delta spread, account for transaction costs
            if useTransactionCosts and delta_spread != 0:
                pair_result[date] =  delta_spread - transaction_cost 
            else: 
                pair_result[date] = delta_spread

        # append to result df 
        result_df[pair] = pair_result
        trade_counts_df[pair] = [1 if r != 0.0 else 0 for r in pair_result.values()]
        x_est_df[pair] = x_est
        R_est_df[pair] = R_est
        y_obs_df[pair] = y_obs
        print("\n number of completed round trip trades: ", sum(trade_counts_df[pair]), "\n",100*"-")    

    return x_est_df, y_obs_df, R_est_df, result_df, trade_counts_df


def run_strategy_kalman(stocks: pd.DataFrame, useTransactionCosts: bool = False):
    
    os.makedirs("logs", exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"logs/backtest_kalman_{timestamp}.log"
    sys.stdout = open(log_filename, "w")
    
    stocks.index = pd.to_datetime(stocks.index)
    time_frame = stocks.index

    months = pd.Series(time_frame).dt.to_period('M').unique()  # Extract unique months

    # This is the main dataframe, that stores the daily returns of each portfolio 
    returns_dictionary = {}
    trade_counts_dictionary = {} 

    n_trading_periods = 0 

    # Iterate through months instead of days
    for start_idx in tqdm(range(len(months)), desc= "Running Kalman backtest"):

        formation_start = pd.Timestamp(months[start_idx].start_time)
        formation_end = formation_start + pd.DateOffset(months=24)-pd.DateOffset(days=1)  # 24 months later
        trading_start = formation_start + pd.DateOffset(months=24)
        trading_end = formation_end + pd.DateOffset(months=6)  # Next 6 months
        
        # Ensure we don't exceed the timeframe
        if trading_end > time_frame[-1]:
            break
        
        # The backtest algorithm starts here:
        # 1. normalize the stock data at the start of the formation period to 1$  
        stocks_normalized = normalize(stocks.loc[formation_start:trading_end])

        # Select formation period data   
        stocks_formation = stocks_normalized.loc[formation_start:formation_end]
        # Select testing data (next 6 months)
        stocks_trading = stocks_normalized.loc[trading_start:trading_end]
        
        # Formation part 
        # 2. sort by ssd ~ 1 minute
        print("\nSorting all combinations by SSD...\n")
        print("=" * 80)
        pairs_sorted = calculate_and_sort_ssd(stocks_formation)

        print(f"Formation Start:\n{stocks_formation.index[0]}")
        print("X" * 80)

        # 3. Select 20 cointegrated pairs 
        print("\nSelecting cointegrated pairs using Engle-Kranger method...\n")
        print("=" * 80)
        portfolio = select_cointegrated_pairs(stocks_formation, pairs_sorted)

        # 4. Estimate the state - observation model parameters
        print("\nEstimating the state - observation model parameters...\n")
        print("=" * 80)
        portfolio_models = estimate_model(stocks_formation=stocks_formation,portfolio=portfolio)
        
        print(f"Formation End:\n{stocks_formation.index[-1]}")
        print("-" * 80)
        print(f"Trading Start:\n{stocks_trading.index[0]}")

        # Trading part
        # 5. Trade portfolio
        print("\nPortfolio is trading...\n")
        print("=" * 80)
        _, _, _, result_df, trade_counts_df = trade_portfolio_kalman(portfolio_models, 
                                                                     stocks_trading=stocks_trading, 
                                                                     useTransactionCosts= useTransactionCosts
                                                                     threshold_factor = 1.0)

        print(f"Trading End:\n{stocks_trading.index[-1]}\n")
        print("X" * 80)

        # 6. Calculate daily returns of each portfolio and append this column for each trading period
        # calculated as a row sums of the daily returns of 20 pairs 
        # Also sum up the number trades on that day over the 6 portfolios
        returns_dictionary[f"Portfolio_{trading_start}"] = result_df.sum(axis=1)
        trade_counts_dictionary[f"Portfolio_{trading_start}"] = trade_counts_df.sum(axis=1)
        n_trading_periods += 1
        print("Number of trading periods: ", n_trading_periods, "\n transaction costs apply:" , useTransactionCosts) 

    sys.stdout.close()
    sys.stdout = sys.__stdout__
    print("Done ... logs saved into", log_filename)
    return pd.DataFrame(returns_dictionary), pd.DataFrame(trade_counts_dictionary)

def plot_kalman(pair, x_est, y_obs, R_est, result):
    """
    Plot Kalman Filter spread for on portfolio pair estimate with ±1σ bands.
    
    Parameters:
        pair (str): Name of the spread column to visualize, e.g., "AEP_PCG"
        x_est (DataFrame): Kalman filtered estimate of the spread
        y_obs (DataFrame): Observed spread values
        R_est (DataFrame): Estimated variance 
    """
    # Compute upper and lower 1σ bands
    upper_band = x_est[pair] + np.sqrt(R_est[pair].values)
    lower_band = x_est[pair] - np.sqrt(R_est[pair].values)
    # Compute residuals
    returns = result[pair]
    # Indices where residuals are non-zero
    nonzero_mask = returns != 0
    pos_mask = (returns > 0) & nonzero_mask
    neg_mask = (returns < 0) & nonzero_mask
    # Plotting
    plt.figure(figsize=(12, 6))
    plt.scatter(y_obs[pair].index, y_obs[pair].values, label='Observed Spread', color='red', s=4)
    plt.plot(x_est[pair].index, x_est[pair].values, label='Filtered Spread (Kalman)', color='blue', linestyle='--')
    plt.fill_between(x_est[pair].index, lower_band, upper_band, color='gray', alpha=0.3, label='±1σ Band')
    # Plot residual markers
    plt.scatter(returns.index[pos_mask], y_obs[pair][pos_mask], marker='x', color='green', label='Return')
    plt.scatter(returns.index[neg_mask], y_obs[pair][neg_mask], marker='x', color='red', label='Loss')
    # Formatting
    plt.title(f'Kalman Filter Estimate for {pair}', fontsize=14)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Spread', fontsize=12)
    #plt.legend(loc='upper right', fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

