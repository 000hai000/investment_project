from functions import generate_data_frame
from functions import generate_graphs

def stock_trading_infographics_report(number_of_days_back, number_of_stocks, names_of_stocks, sector = ''):
    """
    Input: stock_trading_infographics_report(number of days, number of stocks in a generated portfolio, names of stocks in list form, sector)
    For names of stocks, if left as an empty list then there is an option to choose the sector that the report will generate its stock names from.
    Sectors to choose from are 'Industrials', 'Health Care', 'Consumer Discretionary', 'Information Technology', 'Energy', 'Financials', 'Real Estate', 'Communication Services', 'Utilities', 'Materials', 'Consumer Staples'
    Output: outputs a report 'ASX Trading Infrographics.pdf'
    """
    names, normalized_df, normalized_benchmark, df = generate_data_frame(number_of_days_back, number_of_stocks, names_of_stocks, sector = '')
    Optimal_portfolio, Optimal_portfolio_ids, df_SMA = generate_graphs(number_of_days_back, number_of_stocks, names, normalized_df, normalized_benchmark, df)
    
    from fpdf import FPDF
    import yfinance as yf
    
    WIDTH = 210
    HEIGHT = 297
    
    pdf = FPDF()
    
    def new_page():
        pdf.add_page()
        pdf.image('images/asx_trading_infographics_banner.png', x=0, y=0, w=WIDTH)
    
    def graph_optimal_portfolio(y_position, index):
        pdf.image('optimal_portfolio_graphs/normalized_optimal_portfolios' + str(i) + '.png', x=0, y=y_position, w=140)
            
        pdf.set_font('Arial', '', 6)
        pdf.set_xy(130, y_position+10)
        pdf.cell(0, 0, 'Name: ' + str(Optimal_portfolio['names'][index]))
        pdf.set_xy(130, y_position+15)
        pdf.cell(0, 0, 'Weights: ' + str(Optimal_portfolio['weights'][index]))
        pdf.set_xy(130, y_position+20)
        pdf.cell(0, 0, 'Return: ' + str(round(Optimal_portfolio['return'][index], 2)) + '%')
        pdf.set_xy(130, y_position+25)
        pdf.cell(0, 0, 'Volatility: ' + str(round(Optimal_portfolio['volatility'][index], 2)) + '%')
        pdf.set_xy(130, y_position+30)
        pdf.cell(0, 0, 'Gradient: ' + str(round(Optimal_portfolio['gradient'][index], 2)) + '%')
        pdf.set_xy(130, y_position+35)
    
    add_new_page_index_optimal_portfolios = 0
    y_position = 0
    for i in Optimal_portfolio_ids:
        if add_new_page_index_optimal_portfolios % 4 == 0:
            y_position = 60
            new_page()
                
        add_new_page_index_optimal_portfolios += 1
        graph_optimal_portfolio(y_position, i)
        y_position += 65
        
    add_new_page_index_optimal_stocks = 0
    for i in range(len(df_SMA.columns)):
        if add_new_page_index_optimal_stocks % 1 == 0:
            y_position = 60
            new_page()
        add_new_page_index_optimal_stocks += 1
        pdf.image('rolling_average_graphs/rolling_average_of_optimal_stocks' + str(i) + '.png', x=0, y=y_position, w=WIDTH)
        
        ticker = yf.Ticker(df_SMA.columns[i])
        json_data = ticker.info
        
        try:
            json_longName = json_data['longName']
        except:
            json_LongName = 'None'
        y_position += 105
        pdf.set_font('Arial', 'B', 6)
        pdf.set_xy(10, y_position)
        pdf.cell(0, 0, json_longName)
        
        try:
            json_country = json_data['country']
        except:
            json_country = ''
        try:
            json_city = json_data['city']
        except:
            json_city = ''
        try:
            json_address1 = json_data['address1']
        except:
            json_address1 = ''
        try:
            json_address2 = json_data['address2']
        except:
            json_address2 = ''
        y_position += 5
        address = 'Address: ' + json_address2 + ', ' + json_address1 + ', ' + json_city + ', ' + json_country
        pdf.set_font('Arial', '', 6)
        pdf.set_xy(10, y_position)
        pdf.cell(0, 0, address)
        
        try:
            json_sector = json_data['sector']
        except:
            json_sector = 'None'
        try:
            json_industry = json_data['industry']
        except:
            json_industry: 'None'
        y_position += 5
        industry_and_sector = 'Industry and Sector: ' + json_industry + ', ' + json_sector
        pdf.set_xy(10, y_position)
        pdf.cell(0, 0, industry_and_sector)
        
        try:
            json_fullTimeEmployees = json_data['fullTimeEmployees']
        except: 
            json_fullTimeEmployees = 'None'
        y_position += 5
        full_time_employees = 'Full Time Employees: ' + str(json_fullTimeEmployees)
        pdf.set_xy(10, y_position)
        pdf.cell(0, 0, full_time_employees)
        
        try:
            json_marketCap = json_data['marketCap']
        except:
            json_marketCap = 'None'
        y_position += 5
        market_cap = 'Market Cap: ' + '$' + str(json_marketCap)
        pdf.set_xy(10, y_position)
        pdf.cell(0, 0, market_cap)
        
        market_size = ''
        if json_marketCap > 200000000000:
            market_size = "Mega Cap"
        if 10000000000 < json_marketCap <= 200000000000:
            market_size = "Large Cap"
        if 2000000000 < json_marketCap <= 10000000000:
            market_size = "Mid Cap"
        if 300000000 < json_marketCap <= 2000000000:
            market_size = "Small Cap"
        if 50000000 < json_marketCap <= 300000000:
            market_size = "Micro Cap"
        y_position += 3
        cap_size = 'Cap Size: ' + market_size
        pdf.set_xy(10, y_position)
        pdf.cell(0, 0, cap_size)
        
        y_position += 5
        pdf.set_xy(10, y_position)
        pdf.cell(0, 0, 'Major Holders:')
        
        y_position += 3
        for j in range(len(ticker.major_holders[0])):
            holders = '- ' + ticker.major_holders[0][j] + ' ' + ticker.major_holders[1][j].replace('% ', '')
            pdf.set_xy(10, y_position)
            y_position += 3
            pdf.cell(0, 0, holders)
        
        try:
            json_longBusinessSummary = json_data['longBusinessSummary']
        except:
            json_longBusinessSummary = 'None'
        pdf.set_y(y_position)
        pdf.write(3, json_longBusinessSummary)
            
    pdf.output('ASX Trading Infographics.pdf', 'F')
 
    import os
    
    directory_optimal_portfolio = 'optimal_portfolio_graphs'
    for f in os.listdir(directory_optimal_portfolio):
        os.remove(os.path.join(directory_optimal_portfolio, f))
    
    directory_rolling_average = 'rolling_average_graphs'
    for f in os.listdir(directory_rolling_average):
        os.remove(os.path.join(directory_rolling_average, f))
    
    print('Report generated')
