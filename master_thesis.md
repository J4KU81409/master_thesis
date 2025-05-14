# Profitability of pairs trading strategies - cointegration approach versus partial information dynamic model

## Table of contents 

1. Introduction
    - Literature review on PTS, why are PTSs relevant, economic rationale and motivation for both models, what are we going to do, and          why 
    - What are the sections about
2. Data
    - Source, time period, periodicity, why SP500 and liquid stocks? 
4. Methodology
    1. Explain the time period, formation, and trading periods, overlapping portfolios each month, and the design of the research
    2. Pair formation
        - Explain how the stocks are selected, the Engle-Granger two-step model to establish cointegration, and explain the ADF test
    3. Cointegration Strategy 
        - Explain how the spread is modelled (in detail) and the economic rationale behind this, define the return of the trade
        - Trading framework - learning (formation) period and trading period, when to enter/exit trade, assumptions on position size
        - Show some graphs of the stationary paths and thresholds where the trades would be entered and exited
    4. Kalman Filter Strategy
        - Define (in detail) the state and observation equation for the spread model as an OU process that comes in noise, define the       return of the trade
        - EM algorithm - Why suitable for our setup, how does it work, and why is it necessary
        - Kalman Filter - Define the algorithm
        - Trading Framework - learning (formation) period and trading period, trading rules and algorithm
        - Show example price path with signals, and when the trade would be entered
    5. Transaction Costs
        - explain where they come from, commissions + market impact (slippage costs), why they are important, our assumptions
5. Results
    1. Profitability
        - How is the profitability calculated and why (industry practice), no reinvestment, brute force closing positions
    2. Cointegration Strategy vs Kalman Filter Strategy 
        - returns distribution (daily) before and after transaction costs
        - Trade Counts for both strategies + Positive vs negative results 
        - cumulative return of 1$ investment into the strategy before and after transaction costs
        - (Risk adjusted) Monthly performance before and after transaction costs
        - Compare the monthly average performance before and after transaction costs
        - Crisis vs Non-crisis period comparison + Sharpe ratio  before and after transaction costs
6. Conclusion
    - Recap - tested a large volume of data over a 35-year time span, tested the Kalman Method application in real-world daily data, provided reusable and well-documented code facilitating further research or practical implementation
    - The potential use of both methods, their benefits, pitfalls, and characteristics
    - What could be improved


# Data 

For the purposes of our study we use the daily close stock prices starting from April 2nd, 1990 to March 28th 2025, obtained through a python library yfinance. To limit our stock universe for pairs selection due to the computational hardware requirements, we consider the constituent stocks of S&P 500 index as of March 28th 2025. Because these stocks are actively traded and liquid, we also ensure that the transaction costs are mitigated. The evident survivorship bias, as only stocks that have remained in the index over 35 years are considered, is the trade-off we need to undertake for computational feasability.


# Methodology

We test two distinct pairs trading strategies and to ensure constistency and comparability, we split each strategy into two periods while keeping the parameters constant. In our case, we use 24 months as a stock selection period. During this period, we select pairs to trade and estimate the parameters which are assumed to be constant for the next time period, called the trading period. This period is set to be 6 months and this is when the selected stock pairs are monitored for potential trading opportunities.  

During the stock selection period, we check all possible combinations of stock pairs and select a portfolio 20 pairs that are marked as cointegrated based on the sum of squared differences of their normalized prices and the Engle-Granger two step selection method. 

We use a rolling window method for stock selection and trading, where each 24 month stock selection period is followed by a 6 month trading period. The first stock selection period starts on April 1st, 1990 and concludes on April 1st, 1992. Then, on the next day, a trading period starts and trades are entered based on the respective trading criteria of the two strategies. This trading period lasts 6 months, until October 1st, 1992. Importantly, we do not wait until the trading period finishes, and after one month, a new stock selection period is formed. Now, this period starts on May 1st, 1990 and ends on May 1st, 1992. This is the next 24 month rolling window, and in this way we iterate until the last day of our observed time period. Because the trading period lasts 6 months, each month we have 6 overlapping portfolios which are simultaneously monitored for trading. 

# Pair Selection 

To form pairs, we follow a method that was used in the study of Hossein (2016) which combines the cointegration framework of (Vidyamurthy,2004) and the sum of squared differences in normalized prices. Firstly, we rank all possible combinations of stocks in our universe based on the sum of squared differences of their normalized price time series. The normalized price is calculated by dividing the whole time series by its first value, effectively scaling each stock to $1 at the beggining. 

Then, we go through these pairs and select those that pass the Engle-Granger two step method to establish cointegration relationship. First, we regress the price series of first stock in the pair on the price series of the second stock. Then, if a linear relationship is established, we test the residuals using Augmented Dickey-Fuller test to check the stationarity. Since we are effectively modelling the spread in the selection period as residuals of the linear regression, we want this to be stationary to be able to profit from the temporary deviations in the equilibrium relationship. (Engle-Granger).

The pair selection methodology is the same for both strategies, ensuring that the strategies are tested on exactly the same pairs of stocks for comparability. 


# Cointegration Strategy 
