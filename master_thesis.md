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

We test two distinct pairs trading strategies and to ensure constistency and comparability, we split each strategy into two periods while keeping the parameters constant. In our case, we use 24 months as a stock selection period. During this period, we select pairs to trade and estimate the parameters neccessary for the trading algoritms, which are assumed to be constant for the next time period, called the trading period. These parameters differ for both strategies and are explained later. The stock selection period is set to be 6 months and the selected stock pairs are monitored for potential trading opportunities.  

During the stock selection period, we check all possible combinations of stock pairs and select a portfolio 20 pairs that are marked as cointegrated based on the sum of squared differences of their normalized prices and the Engle-Granger two step method. 

We use a rolling window method for stock selection and trading, where each 24 month stock selection period is followed by a 6 month trading period. The first stock selection period starts on April 1st, 1990 and concludes on April 1st, 1992. Then, on the next day, a trading period starts and trades are entered based on the respective trading criteria of the two strategies. This trading period lasts 6 months, until October 1st, 1992. Importantly, we do not wait until the trading period finishes, and after one month, a new stock selection period is formed. Now, this period starts on May 1st, 1990 and ends on May 1st, 1992. This is the next 24 month rolling window, and in this way we iterate until the last day of our observed time period. Because the trading period lasts 6 months, each month we have 6 overlapping portfolios which are simultaneously monitored for trading. 

## Pair Selection 

To form pairs, we follow a method that was used in the study of Hossein (2016) which combines the cointegration framework of Vidyamurthy (2004) and the sum of squared differences (SSD) in normalized prices. Firstly, we rank all possible combinations of stocks in our universe based on the sum of squared differences of their normalized price time series, starting from the lowest value of SSD. The normalized price is calculated by dividing the whole time series by its first value, effectively scaling each stock to $1 at the beggining. 

Then, we go through these pairs and select those that pass the Engle-Granger two step method to establish cointegration relationship. First, we regress the price series of first stock $y_t$ of the pair on the price series of the other $x_t$, so called co-integrating regression (Engle-Granger, p. 261), 
$$ y_t = \beta x_t + u_t$$ 
where $u_t$ are the residuals. In second step, we test the residuals of the cointegration regression using Augmented Dickey-Fuller test, as recommended by Engle and Granger (1987, p.269), to check the stationarity. In general, the ADF test regresses the changes in residuals

$$ \Delta u_t = \rho u_{t-1} + \sum_{i=1}^{p} \alpha_i \Delta u_{t-i} + \varepsilon_t$$

where $\rho$ is the coefficient that is tested in $H_0: \rho = 0$, which represents non-stationarity and hence no cointegration, while the alternative is $H_1: \rho < 0$, $p$ is the number of residual lags included to ensure white noise residuals $\varepsilon_t$. 
Since we are effectively modelling the spread in the selection period as residuals of the linear regression, we want the spread to be stationary to be able to profit from the temporary deviations in the equilibrium relationship. (Engle-Granger, p. 268-269).

We continue testing the previously ordered list of pairs based on SSD until we select 20 pairs that are cointegrated in accordance with Hossein (2016). Thus, we have a portfolio of 20 pairs that are monitored for trading signals. The pair selection methodology is the same for both strategies, ensuring that the strategies are tested on exactly the same pairs of stocks for comparability. Where th


## Cointegration Strategy 

Let $y_t$ and $x_t$ be the time series that are stationary after first differencing. If there exists a $\beta \neq 0 $ such that a linear combination  $$y_t - \beta x_t =  u_t$$
is stationary, then the series $y_t$ and $x_t$ are cointegrated. (Engle Granger, p.253)

The central idea behind cointegration dynamics is the error correction, which means that the linear combination of two cointegrated series has a long-run equilibrium, and if there is a deviation, one or both time series changes such that the linear combination returns to equilibrium. Formally, we can write $$\Delta y_t = \alpha_y (y_{t-1} - \beta x_{t-1}) + \varepsilon_{y_t}$$ 

$$\Delta x_t = \alpha_x (x_{t-1} - \beta y_{t-1}) + \varepsilon_{x_t}$$ 
where $\varepsilon_{y_t}$ and $\varepsilon_{x_t}$ are the white noise processes of series $y_t$ and $x_t$, respectively. The $\alpha_y$ and $\alpha_x$ are the rates of error correction. Based on this representation, we can see that the change in the time series is consists of the error correction term which reverts the series back to its equilibrium and the white noise part. This concept can be used in implementing the pairs trading strategies.
(Vidyamurthy, 2004, p.76)

Let us now model the spread as a linear combination of two stock price series $x_t$ and $y_t$,  
$$spread_t = y_t - \beta x_t$$
Now, assume that we form a spread portfolio by going long in one share of stock $y$ and short selling $\beta$ shares of stock $x$. Then, the profit of this portfolio from time $t$ to time $t+1$ is calculated by $$(y_{t+1}-y_{t}) - \beta (x_{t+1}-x_{t})$$
Conveniently, this can be further rearranged, and we have 
$$
( y_{t+1}-  \beta x_{t+1} ) - (y_{t}-\beta x_{t}) = spread_{t+1} - spread_{t}
$$
so the return of this portfolio is determined by the changes in the spread of the two stock price series. (Hossein, 2016)

### Trading Algorithm
We established the model for the spread as a linear combination of two stock price series and the calculation of the return for the spread of portfolio consisting in trades going opposite directions. The trading strategy is consistent with the framework proposed by Vidyamurthy (2004) and the implementation of Hossein (2016), except the length of the stock selection period, where 12 month period was used. During our 24 month stock selection period, besides nominating 20 pairs for the trading period, we also estimate the parameters neccesary for the trading algorithm of the cointegration strategy, namely the mean of the spread $\mu_{spread}$ and the standard deviation $\sigma_{spread}$. To obtain signals, we use the normalized spread 
$$
spread_{norm} = \frac{spread-\mu_{spread}}{\sigma_{spread}}
$$
By using the normalized spread we get the sense of how the spread diverged considering its standard deviation. The trading algorithm is as follows: if the normalized spread increases above 2, we consider the stock $x$ as relatively underpriced and stock $y$ overpriced, so we buy 1 dollar stock $x$ and sell 1/$\beta$ dollar worth of stock $y$. In the other case, when normalized spread decreases below -2, we sell $\beta$ dollar worth of stock $x$ and buy 1 dollar of stock $y$. To exit the trade by closing both positions, we wait until the spread returns to its long-term equilibrium level of 0. (Hossein, 2016)

Then, if we enter the trade at time $t$ and exit the long-short trades at time $t+1$, the return to this trade can be calculated as $spread_{t+1} - spread_t$ in the case of long direction, i.e. the normalized spread was below -2 threshold and we bet on the spread increasing. In the other case, when the normalized spread exceeds 2, we short the spread portfolio and the return is calculated as $spread_{t} - spread_{t+1}$. Note that in the case that the two underlying stocks diverge and do not converge at least to the 2 standard deviations range until the end of the 6 month trading period, we brute force close all the positions and realize a loss.

## Kalman Filter Strategy 

In the cointegration strategy, we defined the spread of two securities as a linear combination of their prices, provided that it is stationary. Now, we will assume a dynamic mean reverting model for the spread, where the equilibrium level is not constant as was the case in the cointegration strategy. Moreover, we will assume that the spread follows a Ornstein-Uhlenbeck process that comes in noise, thus forming a state-observation model. 

Let us now define this formally according to Elliot (2005). Let the spread be a state process $x_k$ for $k = 0,1,2, \dots$ at time $t_k = k\tau$ such that 
$$
x_{k+1} - x_k= (a - b x_k)\tau + \sigma\sqrt{\tau} \, \varepsilon_{k+1}$$

where $ \varepsilon_k \sim \mathcal{N}(0, 1) $ is an i.i.d. standard normal random variable, $\sigma \geq 0 $, $b > 0$ and $ a \in \mathbb{R}  $

Now, let $A = a\tau$, $B = 1-b\tau$ and $C=\sigma \tau$. Then, this equation can be also expressed as $$x_{k+1} = A + Bx_k + C \varepsilon_{k+1} $$
which is convenient form of the state process Kalman filtering setup.  

Next we define an observation process of $x_k$ as 

$$
y_k = x_k + D \omega_k ,
$$

where 
where $D > 0$, $ \omega_k \sim \mathcal{N}(0, 1) $ is an i.i.d. standard normal random variable independent of $\varepsilon_k$.
In Kalman filtering, we want to compute the best estimates of the state process given the observation process. We have 
$$
\hat{x}_k = \mathbb{E}[x_k \mid \mathcal{Y}_k]$$ 
where the information from observing $y_k$ is $\mathcal{Y}_k = \sigma\{y_1,y_2, \dots, y_k\}$. Let 
$$ R_k = \mathbb{E}[(x_k-\hat{x}_k)^2 \mid \mathcal{Y}_k ].$$   

Our state-observation model is defined by the following equations,
$$
x_{k+1} = A + Bx_k + C \varepsilon_{k+1} 
$$
$$
y_k = x_k + D \omega_k ,
$$
for $k = 0,1,2, \dots.$ 

The values ($\hat{x}_k ,R_k$) can be calculated recursively. First set $\hat{x}_0 = y_0$ and $R_0 = D^2$. Then, 

$$
\begin{aligned}
\hat{x}_{k+1|k} &= A + B \hat{x}_{k|k}  \\
R_{k+1|k} &= B^2 R_{k|k} + C^2 \\
\mathcal{K}_{k+1} &= \frac{R_{k+1|k}}{R_{k+1|k} + D^2} \\
\hat{x}_{k+1|k+1} &= \hat{x}_{k+1|k} + \mathcal{K}_{k+1} \left( y_{k+1} - \hat{x}_{k+1|k} \right) \\
R_{k+1|k+1} &= (1 - \mathcal{K}_{k+1}) R_{k+1|k} = D^2 \mathcal{K}_{k+1}.
\end{aligned}
$$

Before the Kalman filtering can be applied, we need to estimate our state-observation model parameters $ \theta = (A,B,C,D)$.