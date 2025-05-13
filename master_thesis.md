# Profitability of pairs trading strategies - cointegration approach versus partial information dynamic model

## Table of contents 

1. Introduction
    - Literature review on PTS, why are PTSs relevant, economic rationale and motivation for both models, what are we going to do and          why 
    - What are the sections about
2. Data
    - Source, timeperiod, periodicity, why sp500 and liquid stocks ? 
4. Methodology
    1. Explain time period, formation and trading perionds, overlapping portfolios each month, the design of the research
    2. Pairs formation
        - Explain how the stocks are selected, Engle-Kranger two step model to establish cointegration, explain ADF test
    3. Cointegration Strategy 
        - Explain how the spread is modelled (in detail) and economic rationale behind this, define the return of the trade
        - Trading framework - learning (formation) period and trading period, when to enter/exit trade, assumptions on positions size
        - Show some graphs of the stationary paths and thresholds where the trades would be entered and exited
    4. Kalman Filter Strategy
        - Define (in detail) the state and observation equation for the spread model as OU process that comes in noise, define the       return of the trade
        - EM algorithm - Why suitable for our setup, how does it work, why is it neccessary
        - Kalman Filter - Define the algorithm
        - Trading Framework - learning (formation) period and trading period, trading rules and algorithm
        - show example price path with signals and when the trade would be entered
    5. Transaction Costs
        - explain where they come from, comissions + market impact (slippage costs) why they are important, our assumptions
5. Results
    1. Profitability
        - How is the profitability calculated and why (indsutry practice), no reinvestment, brute force closing positions
    2. Cointegration Strategy vs Kalman Filter Strategy 
        - returns distribution (daily) before and after transaction costs
        - cumulative return of 1$ investment into the strategy before and after transaction costs
        - (Risk adjusted) Monthly performance before and after transaction costs
        - Compare Performance monthly average each year before and after transaction costs
        - Crisis vs Non.crisis period comparison + Sharpe ratio  before and after transaction costs
6. Conclusion    

