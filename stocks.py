import streamlit as st
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import plotly.express as px

# Load the Excel data
stock_data = pd.read_excel('nifty_stocks.xlsx')

# Extract company names and corresponding symbols
company_names = stock_data['Company Name'].tolist()
company_to_symbol = stock_data.set_index('Company Name')['Symbol'].to_dict()

st.title('STOCK DASHBOARD')

# Sidebar inputs
selected_company = st.sidebar.selectbox("Select Company", company_names)
exchange = st.sidebar.selectbox('Exchange', ["NSE", "BSE", "NYSE"]) 
start_date = st.sidebar.date_input('Start Date')
end_date = st.sidebar.date_input("End Date")

# Retrieve the symbol for the selected company
selected_symbol = company_to_symbol.get(selected_company, None)
selected_symbol_unchanged=selected_symbol
# Append the correct suffix based on selected exchange
if selected_symbol:
    ticker = selected_symbol
    if exchange == 'NSE':
        ticker += '.NS'
    elif exchange == 'BSE':
        ticker += ".BO"
    else:
        ticker += '' 

    # Display company name
    st.write(f"Company Name: {selected_company}")

    # Download stock data
    data = yf.download(ticker, start=start_date, end=end_date)

    # Display the stock data plot
    fig = px.line(data, x=data.index, y='Adj Close')
    st.plotly_chart(fig)

    # Define tabs
    fundamentals, tech_indicator = st.tabs([
        'Fundamentals', 'Technical Analysis'
    ])

    with fundamentals:
        def get_html_content(url):
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()  # Raise an error for bad status codes
                return response.content
            except requests.exceptions.RequestException as e:
                st.error(f"Error fetching data: {e}")
                return None

        def parse_pl_statement(html_content):
            soup = BeautifulSoup(html_content, 'html.parser')
        
            # Find the specific div containing the P&L statement
            div_pl = soup.find('section', {'id': 'profit-loss'})
        
            if div_pl:
                # Find the table within the section
                table = div_pl.find('table', {'class': 'data-table responsive-text-nowrap'})
                
                if table:
                    # Extract headers
                    headers = [th.text.strip() for th in table.find('thead').find_all('th')]
                    
                    # Extract rows
                    rows = []
                    for tr in table.find('tbody').find_all('tr'):
                        cells = [td.text.strip() for td in tr.find_all('td')]
                        rows.append(cells)
                    
                    # Create a DataFrame
                    df = pd.DataFrame(rows, columns=headers)
                    
                    # global current_net_profit=df['TTM'].iloc[-1]
                    return df
                else:
                    st.warning("Could not find the P&L statement table.")
                    return None
            else:
                st.warning("Could not find the P&L statement section.")
                return None
        
        def parse_quarterly_results(html_content):
            soup = BeautifulSoup(html_content, 'html.parser')
        
            # Find the specific div containing the quarterly results
            div_quarterly = soup.find('section', {'id': 'quarters'})
        
            if div_quarterly:
                # Find the table within the section
                table = div_quarterly.find('table', {'class': 'data-table responsive-text-nowrap'})
                
                if table:
                    # Extract headers
                    headers = [th.text.strip() for th in table.find('thead').find_all('th')]
                    
                    # Extract rows
                    rows = []
                    for tr in table.find('tbody').find_all('tr'):
                        cells = [td.text.strip() for td in tr.find_all('td')]
                        rows.append(cells)
                    
                    # Create a DataFrame
                    df = pd.DataFrame(rows, columns=headers)
                    return df
                else:
                    st.warning("Could not find the quarterly results table.")
                    return None
            else:
                st.warning("Could not find the quarterly results section.")
                return None
        
        url = f'https://www.screener.in/company/{selected_symbol_unchanged}/consolidated/#chart'

        # Fetching data
        html_content = get_html_content(url)
        
        if html_content:
            # Parsing P&L Statement
            df_pl_statement = parse_pl_statement(html_content)
            if df_pl_statement is not None:
                st.subheader("Profit & Loss (P&L) Statement")
                st.dataframe(df_pl_statement)
            
            # Parsing Quarterly Results
            df_quarterly_results = parse_quarterly_results(html_content)
            if df_quarterly_results is not None:
                st.subheader("Quarterly Results")
                st.dataframe(df_quarterly_results)

    with tech_indicator:
        st.header('Technical Analysis')

        def calculate_support(df, window=40):
            df['Support'] = df['Low'].rolling(window=window).min()
            return df

        def calculate_resistance(df, window=20):
            df['Resistance'] = df['High'].rolling(window=window).max()
            return df

        def identify_buying_levels(df, threshold=0.02):
            df['Buy Level'] = np.where(df['Close'] <= df['Support'] * (1 + threshold), df['Close'], np.nan)
            return df

        # Calculate support and resistance levels
        data = calculate_support(data)
        data = calculate_resistance(data)
        data = identify_buying_levels(data)

        # Calculate the midpoint of support and resistance
        data['Midpoint'] = (data['Support'] + data['Resistance']) / 2

        # Plotting with Plotly
        fig = px.line(data, x=data.index, y='Close', title='Stock Price with Support and Resistance Levels')

        # Adding support and resistance levels to the plot
        fig.add_scatter(x=data.index, y=data['Support'], mode='lines', name='Support', line=dict(color='green'))
        fig.add_scatter(x=data.index, y=data['Resistance'], mode='lines', name='Resistance', line=dict(color='red'))

        # Adding midpoint to the plot
        # fig.add_scatter(x=data.index, y=data['Midpoint'], mode='lines', name='Midpoint', line=dict(color='purple', dash='dash'))

        # Adding buying levels to the plot
        fig.add_scatter(x=data.index, y=data['Buy Level'], mode='markers', name='Buy Level', marker=dict(color='blue', symbol='circle'))

        # Display the plot in Streamlit
        st.plotly_chart(fig)

        # Check for recommendations
        if not data.empty and 'Close' in data.columns and 'Resistance' in data.columns and 'Support' in data.columns:
            latest_close = data['Close'].iloc[-1].round(0)
            latest_resistance = data['Resistance'].iloc[-1].round(0)
            latest_support = data['Support'].iloc[-1].round(0)
            latest_midpoint = data['Midpoint'].iloc[-1].round(0)

            # Display recommendation based on latest close price
            if latest_close > latest_resistance:
                st.write('Recommend : Sell')
            elif latest_close >= latest_midpoint:
                st.write('Recommend : Hold')
                st.write(f"Resistance: {latest_resistance}")
                st.write(f"Support: {latest_support}")
            else:
                st.write('Recommend : Buy')
                st.write(f"Support: {latest_support}")
                # st.write(current_net_profit)

else:
    st.write("Please select a valid company.")
