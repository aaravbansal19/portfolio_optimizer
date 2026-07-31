import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as mtick

tickers = []

number_of_stocks = int(input("How many stocks do you want to add to the portfolio? "))

for i in range(number_of_stocks):
    ticker = input(f"Enter the stock ticker #{i + 1}: ").upper()
    tickers.append(ticker)

tickers = list(dict.fromkeys(tickers))


period = input("Enter a period (6mo, 1y, 2y, 5y): ")
number_of_simulations = int(input("Enter number of portfolio simulations: "))

stock_data = {}

for ticker in tickers:
    data = yf.download(ticker, period=period, interval="1d")
    data.columns = data.columns.droplevel(1)
    stock_data[ticker] = data["Close"]

portfolio_df = pd.DataFrame(stock_data)

portfolio_df = portfolio_df.dropna()

daily_returns = portfolio_df.pct_change()
daily_returns = daily_returns.dropna()

weights = [1 / len(tickers)] * len(tickers)
portfolio_daily_returns = daily_returns.dot(weights)
portfolio_growth = (1 + portfolio_daily_returns).cumprod()
portfolio_volatility = portfolio_daily_returns.std() * np.sqrt(252)

correlation_matrix = daily_returns.corr()

first_date = portfolio_df.index[0]
last_date = portfolio_df.index[-1]
trading_days = len(portfolio_df)

initial_investment = float(input("Enter your initial investment amount: $"))

starting_normalization = float(input("Enter starting normalization value: "))


print()
print("First Trading Date:", first_date)
print("Last Trading Date:", last_date)
print("Trading Days:", trading_days)
print()
print("Latest Prices:")
for stock in portfolio_df.columns:
    print(f"    {stock}: ${portfolio_df[stock].iloc[-1]:.2f}")
returns = {}
print()
for stock in portfolio_df.columns:
    starting_price = portfolio_df[stock].iloc[0]
    ending_price = portfolio_df[stock].iloc[-1]
    return_percent = (ending_price - starting_price)/starting_price
    returns[stock] = return_percent
sorted_returns = dict(sorted(returns.items(), key=lambda item: item[1], reverse=True))
print()

print("Best Performing Stocks")
for i, (stock, return_value) in enumerate(sorted_returns.items()):
    print(f"{i+1}. {stock}: {return_value:.2%}")
print()
print(f"Best Performer: {max(returns, key=returns.get)} at {max(returns.values()):.2%}")
print(f"Worst Performer: {min(returns, key=returns.get)} at {min(returns.values()):.2%}")
print()

def plot_stocks(portfolio_df):
    plt.figure(figsize=(14, 7))
    for stock in portfolio_df.columns:
        plt.plot(portfolio_df.index, portfolio_df[stock], label=stock)

    plt.legend()
    plt.title("Stock Price Comparison")
    plt.xlabel('Date')
    plt.ylabel("Price ($)")
    plt.grid()
    plt.savefig("portfolio_prices.png")
    plt.show()

plot_stocks(portfolio_df)

normalized_prices = (portfolio_df / portfolio_df.iloc[0]) * starting_normalization
portfolio_value = (normalized_prices.mean(axis=1) / starting_normalization) * initial_investment
portfolio_average = normalized_prices.mean(axis=1)
ending_normalized_values = normalized_prices.iloc[-1].to_dict()
ranked_stocks = dict(sorted(ending_normalized_values.items(), key=lambda item: item[1], reverse=True))
print("Portfolio Performance (Normalized)")
for i, (stock, value) in enumerate(ranked_stocks.items()):
    print(f"{i + 1}. {stock}: ${value:.2f} (starting value ${starting_normalization})")
print()
print(f"Best Performer (Normalized): {max(ending_normalized_values, key=ending_normalized_values.get)} at {max(ending_normalized_values.values()):.2f}")
print(f"Worst Performer (Normalized): {min(ending_normalized_values, key=ending_normalized_values.get)} at {min(ending_normalized_values.values()):.2f}")
print()

def plot_normalized(normalized_prices, portfolio_average, starting_normalization):
    plt.figure(figsize=(14, 7))
    for stock in normalized_prices.columns:
        plt.plot(normalized_prices.index, normalized_prices[stock], label=stock)
        plt.scatter(normalized_prices.index[-1], normalized_prices[stock].iloc[-1])
    plt.plot(portfolio_average.index, portfolio_average, label="Portfolio Average", linewidth = 2)

    plt.legend()
    plt.title("Normalized Stock Performance")
    plt.xlabel('Date')
    plt.ylabel(f"Portfolio Growth (Starting Value = ${starting_normalization})")    
    plt.grid()
    plt.savefig("normalized_prices.png")
    plt.show()

plot_normalized(normalized_prices, portfolio_average, starting_normalization)

portfolio_return = (portfolio_value.iloc[-1] - initial_investment) / initial_investment
print("Equal Weight Portfolio Performance")
print(f"Starting Value: ${initial_investment:.2f}")
print(f"Ending Value: ${portfolio_value.iloc[-1]:.2f}")
print(f"Portfolio Return: {portfolio_return:.2%}")
print(f"Portfolio Volatility: {portfolio_volatility:.2%}")
print()

print()
print("Correlation Matrix")
print(correlation_matrix.round(2))

def plot_correlation_heatmap(correlation_matrix):
    plt.figure(figsize=(8, 6))
    plt.imshow(correlation_matrix, cmap="coolwarm", vmin=-1, vmax=1)
    plt.colorbar(label="Correlation")
    plt.xticks(range(len(correlation_matrix.columns)), correlation_matrix.columns, rotation=45)
    plt.yticks(range(len(correlation_matrix.columns)), correlation_matrix.columns)
    for i in range(len(correlation_matrix)):
        for j in range(len(correlation_matrix.columns)):
            plt.text(j, i, f"{correlation_matrix.iloc[i, j]:.2f}", ha="center", va="center", fontsize=9)
    plt.title("Stock Correlation Heatmap")

    plt.savefig("correlation_heatmap.png")
    plt.show()

plot_correlation_heatmap(correlation_matrix)

correlation_pairs = correlation_matrix.copy()

for stock in correlation_pairs.columns:
    correlation_pairs.loc[stock, stock] = None

most_correlated = correlation_pairs.stack().idxmax()
highest_correlation = correlation_pairs.stack().max()
least_correlated = correlation_pairs.stack().idxmin()
lowest_correlation = correlation_pairs.stack().min()
print()
print("Most Correlated Pair")
print(f"{most_correlated[0]} and {most_correlated[1]}")
print(f"Correlation: {highest_correlation:.2f}")
print()
print("Least Correlated Pair")
print(f"{least_correlated[0]} and {least_correlated[1]}")
print(f"Correlation: {lowest_correlation:.2f}")
print()


print("Individual Stock Performance")
for stock in daily_returns.columns:
    stock_volatility = daily_returns[stock].std() * np.sqrt(252)
    stock_return = returns[stock]

    print(stock)
    print(f"Return: {stock_return:.2%}")
    print(f"Volatility: {stock_volatility:.2%}")
    print()


def plot_portfolio_growth(portfolio_growth, initial_investment):
    plt.figure(figsize=(14, 7))
    portfolio_value = portfolio_growth * initial_investment
    plt.plot(portfolio_value.index, portfolio_value, label="Portfolio")
    plt.legend()
    plt.title("Portfolio Growth Over Time")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value ($)")
    plt.grid()
    plt.savefig("portfolio_growth.png")
    plt.show()

plot_portfolio_growth(portfolio_growth, initial_investment)

def optimize_portfolio():
    portfolio_returns = []
    portfolio_volatilities = []
    portfolio_sharpe_ratios = []
    portfolio_weights = []
    for i in range(number_of_simulations):
        weights = np.random.random(len(tickers))
        weights = weights / weights.sum()

        daily_expected_return = (daily_returns.mean() * weights).sum()
        daily_expected_volatility = (daily_returns.cov().dot(weights).dot(weights)) ** 0.5
        annual_return = (1 + daily_expected_return) ** 252 - 1
        annual_volatility = daily_expected_volatility * np.sqrt(252)
        annual_volatility = daily_expected_volatility * np.sqrt(252)

if annual_volatility == 0:
    sharpe_ratio = 0
else:
    sharpe_ratio = annual_return / annual_volatility

        portfolio_returns.append(annual_return)
        portfolio_volatilities.append(annual_volatility)
        portfolio_sharpe_ratios.append(sharpe_ratio)
        portfolio_weights.append(weights)

    best_sharpe_index = portfolio_sharpe_ratios.index(max(portfolio_sharpe_ratios))
    best_return = portfolio_returns[best_sharpe_index]
    best_volatility = portfolio_volatilities[best_sharpe_index]
    best_weights = portfolio_weights[best_sharpe_index]

    optimized_portfolio = pd.DataFrame({
    "Ticker": tickers,
    "Weight": best_weights
    })

    optimized_portfolio.to_csv("optimized_portfolio.csv", index=False)

    best_sharpe = portfolio_sharpe_ratios[best_sharpe_index]

    lowest_volatility_index = portfolio_volatilities.index(min(portfolio_volatilities))
    lowest_volatility_return = portfolio_returns[lowest_volatility_index]
    lowest_volatility = portfolio_volatilities[lowest_volatility_index]
    lowest_volatility_weights = portfolio_weights[lowest_volatility_index]
    lowest_volatility_sharpe = portfolio_sharpe_ratios[lowest_volatility_index]

    highest_return_index = portfolio_returns.index(max(portfolio_returns))
    highest_return = portfolio_returns[highest_return_index]
    highest_return_volatility = portfolio_volatilities[highest_return_index]
    highest_return_weights = portfolio_weights[highest_return_index]
    highest_return_sharpe = portfolio_sharpe_ratios[highest_return_index]

    print()
    print("Optimal Portfolio (Highest Sharpe Ratio)")
    print(f"Expected Return: {best_return:.2%}")
    print(f"Volatility: {best_volatility:.2%}")
    print(f"Sharpe Ratio: {best_sharpe:.2f}")
    print()

    for stock, weight in zip(tickers, best_weights):
        investment_amount = initial_investment * weight
        print(f"{stock}: {weight:.2%} (${investment_amount:,.2f})")

    print()

    optimized_daily_returns = daily_returns.dot(best_weights)
    optimized_growth = (1 + optimized_daily_returns).cumprod()
    optimized_final_value = initial_investment * optimized_growth.iloc[-1]
    optimized_return = optimized_growth.iloc[-1] - 1
    optimized_volatility = optimized_daily_returns.std() * np.sqrt(252)

    print("Optimized Portfolio Performance")
    print(f"Starting Value: ${initial_investment:.2f}")
    print(f"Ending Value: ${optimized_final_value:.2f}")
    print(f"Total Return: {optimized_return:.2%}")
    print(f"Volatility: {optimized_volatility:.2%}")
    print(f"Sharpe Ratio: {best_sharpe:.2f}")

    print()
    print("Lowest Volatility Portfolio")
    print(f"Expected Return: {lowest_volatility_return:.2%}")
    print(f"Volatility: {lowest_volatility:.2%}")
    print(f"Sharpe Ratio: {lowest_volatility_sharpe:.2f}")
    print()

    for stock, weight in zip(tickers, lowest_volatility_weights):
        investment_amount = initial_investment * weight
        print(f"{stock}: {weight:.2%} (${investment_amount:,.2f})")

    print()

    vol_optimized_daily_returns = daily_returns.dot(lowest_volatility_weights)
    vol_optimized_growth = (1 + vol_optimized_daily_returns).cumprod()
    vol_optimized_final_value = initial_investment * vol_optimized_growth.iloc[-1]
    vol_optimized_return = vol_optimized_growth.iloc[-1] - 1
    vol_optimized_volatility = vol_optimized_daily_returns.std() * np.sqrt(252)

    print("Lowest Volatility Portfolio Performance")
    print(f"Starting Value: ${initial_investment:.2f}")
    print(f"Ending Value: ${vol_optimized_final_value:.2f}")
    print(f"Total Return: {vol_optimized_return:.2%}")
    print(f"Volatility: {vol_optimized_volatility:.2%}")
    print(f"Sharpe Ratio: {lowest_volatility_sharpe:.2f}")


    print()
    print("Highest Return Portfolio")
    print(f"Expected Return: {highest_return:.2%}")
    print(f"Volatility: {highest_return_volatility:.2%}")
    print(f"Sharpe Ratio: {highest_return_sharpe:.2f}")
    print()

    for stock, weight in zip(tickers, highest_return_weights):
        investment_amount = initial_investment * weight
        print(f"{stock}: {weight:.2%} (${investment_amount:,.2f})")

    print()

    ret_optimized_daily_returns = daily_returns.dot(highest_return_weights)
    ret_optimized_growth = (1 + ret_optimized_daily_returns).cumprod()
    ret_optimized_final_value = initial_investment * ret_optimized_growth.iloc[-1]
    ret_optimized_return = ret_optimized_growth.iloc[-1] - 1
    ret_optimized_volatility = ret_optimized_daily_returns.std() * np.sqrt(252)

    print("Highest Return Portfolio Performance")
    print(f"Starting Value: ${initial_investment:.2f}")
    print(f"Ending Value: ${ret_optimized_final_value:.2f}")
    print(f"Total Return: {ret_optimized_return:.2%}")
    print(f"Volatility: {ret_optimized_volatility:.2%}")
    print(f"Sharpe Ratio: {highest_return_sharpe:.2f}")


    summary = pd.DataFrame({
    "Portfolio": [
        "Equal Weight",
        "Highest Sharpe",
        "Lowest Volatility",
        "Highest Return"
    ],
    "Return": [
        portfolio_return,
        optimized_return,
        vol_optimized_return,
        ret_optimized_return
    ],
    "Volatility": [
        portfolio_volatility,
        optimized_volatility,
        vol_optimized_volatility,
        ret_optimized_volatility
    ],
    "Sharpe Ratio": [
        portfolio_return / portfolio_volatility,
        best_sharpe,
        lowest_volatility_sharpe,
        highest_return_sharpe
    ]
})

    summary.to_csv("portfolio_summary.csv", index=False)

    return (
    portfolio_returns,
    portfolio_volatilities,
    portfolio_sharpe_ratios,
    best_return,
    best_volatility,
    best_sharpe,
    lowest_volatility_return,
    lowest_volatility,
    lowest_volatility_sharpe,
    highest_return,
    highest_return_volatility,
    highest_return_sharpe, 
    optimized_return, 
    optimized_growth, 
    vol_optimized_return, 
    ret_optimized_return
)

(
    portfolio_returns,
    portfolio_volatilities,
    portfolio_sharpe_ratios,
    best_return,
    best_volatility,
    best_sharpe,
    lowest_volatility_return,
    lowest_volatility,
    lowest_volatility_sharpe,
    highest_return,
    highest_return_volatility,
    highest_return_sharpe, 
    optimized_return, 
    optimized_growth, 
    vol_optimized_return, 
    ret_optimized_return
) = optimize_portfolio()


def plot_efficient_frontier():
    plt.figure(figsize=(14,7))
    plt.scatter(portfolio_volatilities, portfolio_returns, c=portfolio_sharpe_ratios, cmap="viridis")
    plt.scatter(best_volatility, best_return, color="red", marker="*", s=250, label="Highest Sharpe")
    plt.scatter(lowest_volatility, lowest_volatility_return, color="blue", marker="s", s=150, label="Lowest Risk")
    plt.scatter(highest_return_volatility, highest_return, color="green", marker="^", s=150, label="Highest Return")
    plt.colorbar(label="Sharpe Ratio")
    plt.title("Monte Carlo Portfolio Optimization")
    plt.xlabel("Portfolio Volatility")
    plt.ylabel("Expected Return")   
    plt.gca().xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    plt.legend()
    plt.grid(alpha=0.3) 
    plt.savefig("efficient_frontier.png")
    plt.show()

plot_efficient_frontier()

def plot_optimized_vs_equal():
    plt.figure(figsize=(14,7))

    equal_weight_value = portfolio_growth * initial_investment
    optimized_value = optimized_growth * initial_investment

    plt.plot(equal_weight_value.index, equal_weight_value, label="Equal Weight")
    plt.plot(optimized_value.index, optimized_value, label="Optimized")

    plt.legend()
    plt.title("Equal Weight vs Optimized Portfolio")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value ($)")
    plt.grid()
    plt.savefig("optimized_vs_equal_weight.png")
    plt.show()

plot_optimized_vs_equal()

print()
print("Portfolio Summary")
print()
print(f"Stocks: {len(tickers)}")
print(f"Trading Days: {trading_days}")
print(f"Simulations: {number_of_simulations}")
print()
print(f"Equal Weight Return: {portfolio_return:.2%}")
print(f"Highest Sharpe Return: {optimized_return:.2%}")
print(f"Lowest Risk Return: {vol_optimized_return:.2%}")
print(f"Highest Return Portfolio: {ret_optimized_return:.2%}")
print()
print(f"Best Stock: {max(returns, key=returns.get)}")
print(f"Worst Stock: {min(returns, key=returns.get)}")
print()
print(f"Highest Sharpe Ratio: {best_sharpe:.2f}")
print(f"Most Correlated Pair: {most_correlated[0]} & {most_correlated[1]}")
print(f"Least Correlated Pair: {least_correlated[0]} & {least_correlated[1]}")