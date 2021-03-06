from pandas_datareader import data as pdr
import yfinance as yf
import datetime
import pandas as pd

def generate_data_frame(number_of_days_back, number_of_stocks, names_of_stocks, sector = ''):
    """
    Input: stock_trading_infographics_report(number of days, number of stocks in a generated portfolio, names of stocks in list form, sector)
    For names of stocks, if left as an empty list then there is an option to choose the sector that the report will generate its stock names from.
    Sectors to choose from are 'Industrials', 'Health Care', 'Consumer Discretionary', 'Information Technology', 'Energy', 'Financials', 'Real Estate', 'Communication Services', 'Utilities', 'Materials', 'Consumer Staples'
    Output: outputs a report 'ASX Trading Infrographics.pdf'
    """
    names = ['ASX']
    names.extend(names_of_stocks)
    start_date = datetime.datetime.now() - datetime.timedelta(days=number_of_days_back)
    end_date = datetime.datetime.now()
    
    if len(names) == 1:
        #Run this for running whole market
        asx_companies = pd.read_csv('asx_companies.csv')
        asx_companies['names'] = asx_companies['Code'].apply(lambda x: x + '.AX')
        for i in range(len(asx_companies['Sector'])):
            if asx_companies['Sector'][i] == sector:
                names.append(asx_companies['names'][i])
    
    print('Pulling data...')
    yf.pdr_override()
    df = pdr.get_data_yahoo(names, start_date, end_date)
    print('Data Pulling complete')
    df = df['Adj Close']
    df = df.fillna(method='ffill')
    
    normalized_df = (df - df.mean()) / df.std()
    normalized_benchmark = normalized_df['ASX']
    df = df.drop(columns=['ASX'])
    
    return names, normalized_df, normalized_benchmark, df

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import math

def generate_graphs(number_of_days_back, number_of_stocks, names, normalized_df, normalized_benchmark, df):
    #Finds the combination of available portfolios given the number of stocks available and number of stocks wanted
    sample_size = math.factorial(len(names[1:])) // (math.factorial(len(names[1:]) - number_of_stocks) * math.factorial(number_of_stocks))
    print('Number of portfolios to be generated: ' + str(sample_size))
    
    #Creating an array of zeros with sample size x
    percent_vols = np.zeros((sample_size, 1))
    percent_ret = np.zeros((sample_size, 1))
    
    #Empty Lists
    w_list = []
    names_list = []
    
    from itertools import combinations
    
    #Choosing all possible combinations of stock choices
    combinations = list(combinations(names[1:], number_of_stocks))
    
    for idx in range(len(combinations)):
        port = df[list(combinations[idx])]
        
    #Daily simple returns
        returns = port.pct_change()
    #Assigning weights to the stock to create a portfolio
        r = np.array(np.mean(returns, axis=0))
    #Covariance matrix between stocks (in array)
        S = np.array(returns.cov())
    #Vector of 1's equal in length to r
        e = np.ones(len(r))
    
        def objective(w):
            return np.matmul(np.matmul(w,S),w)
    
    #Set initial weight values
        w = np.random.random(len(r))
    #Define Constraints
        const = ({'type' : 'eq' , 'fun' : lambda w: np.dot(w,e) - 1})    # sum(w) - 1 = 0
    #Create Bounds
    #Creates a tuple of tuples to pass to minimize
    #to ensure all weights are betwen [0, inf]
        non_neg = []
        for i in range(len(r)):
            non_neg.append((0,None))
        non_neg = tuple(non_neg)
    
    #Run optimization with SLSQP solver
        solution = minimize(fun=objective, x0=w, method='SLSQP',constraints=const,bounds=non_neg)
        w = solution.x.round(6)
        
    #Assign values into the empty list
        w_list.append(w)
        names_list.append(list(returns.columns[w > 0.0]))
    
    #Find co-variance to see how much each stock varies
        cov_matrix_annual = returns.cov() * 252 
    #Expected portfolio variance= WT * (Covariance Matrix) * W
        port_variance = np.dot(w.T, np.dot(cov_matrix_annual, w))
    #Expected portfolio volatility= SQRT (WT * (Covariance Matrix) * W)
        port_volatility = np.sqrt(port_variance)
    #Portfolio annual simple return
        portfolioSimpleAnnualReturn = np.sum(returns.mean() * w) * 252
        
    #Annual return and volatility.
        percent_vols[idx] = port_volatility * 100
        percent_ret[idx] = portfolioSimpleAnnualReturn * 100
        
    #appending array into a dataframe
    generated_portfolios = pd.DataFrame(columns = ['return', 'volatility'])
    generated_portfolios['return'] = percent_ret[:,0]
    generated_portfolios['volatility'] = percent_vols[:,0]
    
    #Finding the Portfolio with the maximum gradient
    generated_portfolios['gradient'] = generated_portfolios['return'] / generated_portfolios['volatility']
    generated_portfolios['names'] = names_list
    generated_portfolios['weights'] = w_list
    
    generated_portfolios = generated_portfolios.sort_values(by='gradient', ascending=False)
    Optimal_portfolio = generated_portfolios.head(9)
    Optimal_portfolio_ids = Optimal_portfolio.index
        
    print('Portfolios generated')
    print('Generating graphs...')
    if number_of_days_back <= 30:
        df_SMA = pd.DataFrame()
        for i in Optimal_portfolio_ids:
            #optimal_portfolio_graphs
            fig, ax = plt.subplots(figsize=(16,8))
            plt.title('Normalized Optimal Portfolios')
            ax.plot(normalized_df.index, normalized_benchmark, label = 'ASX')
            for j in range(len(Optimal_portfolio['names'][i])):
                ax.plot(normalized_df.index, normalized_df[Optimal_portfolio['names'][i][j]], label = Optimal_portfolio['names'][i][j])
            ax.legend()
            plt.savefig(r'optimal_portfolio_graphs/normalized_optimal_portfolios' + str(i) + '.png')
            for j in range(len(Optimal_portfolio['names'][i])):
                name = Optimal_portfolio['names'][i][j]
                df_SMA[name] = df[name].rolling(window=7).mean()
        for i in range(len(df_SMA.columns)):
            #rolling_average_graphs
            fig, ax = plt.subplots(figsize=(16,8))
            plt.title('Weekly Rolling Average of Optimal Stocks')
            ax.plot(df_SMA[6:].index, df_SMA[6:][df_SMA.columns[i]], label = df_SMA.columns[i] + '_SMA')
            ax.plot(df[6:].index, df[6:][df_SMA.columns[i]], label = df_SMA.columns[i])
            ax.legend()
            plt.savefig(r'rolling_average_graphs/rolling_average_of_optimal_stocks' + str(i) + '.png')
            
    if number_of_days_back > 30 and number_of_days_back < 365:
        df_SMA = pd.DataFrame()
        for i in Optimal_portfolio_ids:
            #optimal_portfolio_graphs
            fig, ax = plt.subplots(figsize=(16,8))
            plt.title('Normalized Optimal Portfolios')
            ax.plot(normalized_df.index, normalized_benchmark, label = 'ASX')
            for j in range(len(Optimal_portfolio['names'][i])):
                ax.plot(normalized_df.index, normalized_df[Optimal_portfolio['names'][i][j]], label = Optimal_portfolio['names'][i][j])
            ax.legend()
            plt.savefig(r'optimal_portfolio_graphs/normalized_optimal_portfolios' + str(i) + '.png')
            for j in range(len(Optimal_portfolio['names'][i])):
                name = Optimal_portfolio['names'][i][j]
                df_SMA[name] = df[name].rolling(window=30).mean()
        for i in range(len(df_SMA.columns)):
            #rolling_average_graphs
            fig, ax = plt.subplots(figsize=(16,8))
            plt.title('Monthly Rolling Average of Optimal Stocks')
            ax.plot(df_SMA[29:].index, df_SMA[29:][df_SMA.columns[i]], label = df_SMA.columns[i] + '_SMA')
            ax.plot(df[29:].index, df[29:][df_SMA.columns[i]], label = df_SMA.columns[i])
            ax.legend()
            plt.savefig(r'rolling_average_graphs/rolling_average_of_optimal_stocks' + str(i) + '.png')
            
    if number_of_days_back >= 365:
        
        df_SMA = pd.DataFrame()
        for i in Optimal_portfolio_ids:
            #optimal_portfolio_graphs
            fig, ax = plt.subplots(figsize=(16,8))
            plt.title('Normalized Optimal Portfolios')
            ax.plot(normalized_df.index, normalized_benchmark, label = 'ASX')
            for j in range(len(Optimal_portfolio['names'][i])):
                ax.plot(normalized_df.index, normalized_df[Optimal_portfolio['names'][i][j]], label = Optimal_portfolio['names'][i][j])
            ax.legend()
            plt.savefig(r'optimal_portfolio_graphs/normalized_optimal_portfolios' + str(i) + '.png')
            for j in range(len(Optimal_portfolio['names'][i])):
                name = Optimal_portfolio['names'][i][j]
                df_SMA[name] = df[name].rolling(window=90).mean()
        for i in range(len(df_SMA.columns)):
            #rolling_average_graphs
            fig, ax = plt.subplots(figsize=(16,8))
            plt.title('Quarterly Rolling Average of Optimal Stocks')
            ax.plot(df_SMA[89:].index, df_SMA[89:][df_SMA.columns[i]], label = df_SMA.columns[i] + '_SMA')
            ax.plot(df[89:].index, df[89:][df_SMA.columns[i]], label = df_SMA.columns[i])
            ax.legend()
            plt.savefig(r'rolling_average_graphs/rolling_average_of_optimal_stocks' + str(i) + '.png')
            
    print('Graphs generated')
    print('Generating report...')
    
    return Optimal_portfolio, Optimal_portfolio_ids, df_SMA
    
    