import yfinance as yf
import utils.stock_info as si
from typing import Any, Dict, List
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from model.ticker import TickerDetail, TickerMetrics
import logging, time, sys, traceback, os
from decimal import Decimal
import json, feedparser


logger = logging.getLogger(__name__)

yf.set_tz_cache_location("yf/cache/")

class StockInfoService:

    def get_ticker_detail_raw(self, symbol: str) -> Dict[str, Any]:
        stock = yf.Ticker(symbol)
        return json.dumps(stock)

    def get_ticker_detail(self, symbol: str) -> TickerDetail:
        try:
            stock = yf.Ticker(symbol)
            print(stock.fast_info)
            ticker_detail = TickerDetail(
                symbol=symbol,
                stock_info=dict(stock.fast_info),
                holders=stock.major_holders.to_dict() if stock.major_holders is not None else {},
                #data=self.get_history_for_year(symbol),
                #balance_sheet=self.sanitize_data_transposed(stock.balance_sheet),
                #cashflow=self.sanitize_data_transposed(stock.cashflow),
                #income_statement=self.sanitize_data_transposed(stock.financials) if stock.financials is not None else {},
                update_dt=datetime.now()
            )
            cleaned_result = self.convert_timestamp_keys(ticker_detail.model_dump())
            return cleaned_result
        except Exception as e:
            logger.error(f"Error in get_ticker_detail for ticker {symbol}: {e}")
            raise

    def get_cash_flow(self, symbol: str) -> Dict:
        try:
            stock = yf.Ticker(symbol)
            cashflow=self.sanitize_data_transposed(stock.cashflow)
            cleaned_result = self.convert_timestamp_keys(cashflow)
            
            return cleaned_result
        except Exception as e:
            logger.error(f"Error in get_cash_flow for ticker {symbol}: {e}")
            raise
        
    def get_income_stmt(self, symbol: str) -> Dict:
        try:
            stock = yf.Ticker(symbol)
            income_statement=self.sanitize_data_transposed(stock.financials) if stock.financials is not None else {}

            cleaned_result = self.convert_timestamp_keys(income_statement)
            
            return cleaned_result
        except Exception as e:
            logger.error(f"Error in get_income_statement for ticker {symbol}: {e}")
            raise


    def get_balance_sheet(self, symbol: str) -> Dict:
        try:
            stock = yf.Ticker(symbol)
            balance_sheet=self.sanitize_data_transposed(stock.balance_sheet)
            cleaned_result = self.convert_timestamp_keys(balance_sheet)
            return cleaned_result
        except Exception as e:
            logger.error(f"Error in get_ticker_detail for ticker {symbol}: {e}")
            raise
        
        
    def get_stock_news(self, ticker):
        import json
        from datetime import datetime
        
        yf_rss_url = 'https://feeds.finance.yahoo.com/rss/2.0/headline?s=%s&region=US&lang=en-US'
        MAX_SIZE = 25 * 1024  # 24KB in bytes
        
        try:
            feed = feedparser.parse(yf_rss_url % ticker)
            
            # Sort entries by date (most recent first)
            sorted_entries = sorted(
                feed.entries,
                key=lambda x: datetime.strptime(x.published, '%a, %d %b %Y %H:%M:%S %z'),
                reverse=True
            )
            
            filtered_entries = []
            current_size = 0
            
            for entry in sorted_entries:
                # Create a simplified entry with essential fields
                simplified_entry = {
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published,
                    'summary': entry.summary
                }
                
                # Calculate size of this entry
                entry_size = len(json.dumps(simplified_entry).encode('utf-8'))
                
                # Check if adding this entry would exceed size limit
                if current_size + entry_size <= MAX_SIZE:
                    filtered_entries.append(simplified_entry)
                    current_size += entry_size
                else:
                    break
            
            return filtered_entries
            
        except Exception as e:
            print(f"Error fetching news for {ticker}: {str(e)}")
            return []



    def get_history_for_days(self, ticker: str, days: int) -> Dict[str, Any]:
        try:
            stock = yf.Ticker(ticker)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            history = stock.history(start=start_date, end=end_date)
            # Remove columns with any null/empty values
            history = history.dropna(axis=1, how='any')

            return history.to_dict()
        except Exception as e:
            logger.error(f"Error in get_history_for_year for ticker {ticker}: {e}")
            raise

    def get_day_gainers(self):
        try:
            day_gainers = si.get_day_gainers()
            print("Columns in the day_gainers DataFrame:")
            for col in day_gainers.columns:
                print(f"- {col}")
            first_row = day_gainers.iloc[0]
            for col, value in first_row.items():
                print(f"{col}: {value}")
            
            #'symbol', 'name', 'price', 'change', 'changePercent', 'volume', 'avgVolume', 'marketCap', 'peRatio', 'weekRange'
    
            day_gainers = day_gainers.rename(columns={
                'Symbol': 'symbol', 'Name': 'name', 'Price': 'price', 'Change': 'change',
                'Change %': 'changePercent', 'Volume': 'volume', 'Avg Vol (3M)': 'avgVolume',
                'Market Cap': 'marketCap', 'P/E Ratio (TTM)': 'peRatio', '52 Wk Change %': 'weekRange'
            })
            # Extract only the first value from the 'price' column
            day_gainers['price'] = day_gainers['price'].astype(str).str.split().str[0]
            # Remove columns with any null/empty values
            day_gainers = day_gainers.dropna(axis=1, how='any')

            # Remove the 'Unnamed: 2' column if it exists
            if 'Unnamed: 2' in day_gainers.columns:
                day_gainers = day_gainers.drop('Unnamed: 2', axis=1)

            if len(day_gainers) > 20:
                day_gainers = day_gainers.head(20)

            day_gainers = self.sanitize_data(day_gainers)
            return day_gainers
        except Exception as e:
            logger.error(f"Error in get_day_gainers: {e}")
            raise

    def get_day_losers(self):
        try:
            response = si.get_day_losers('100')
            response = response.rename(columns={
                'Symbol': 'symbol', 'Name': 'name', 'Price': 'price', 'Change': 'change',
                'Change %': 'changePercent', 'Volume': 'volume', 'Avg Vol (3M)': 'avgVolume',
                'Market Cap': 'marketCap', 'P/E Ratio (TTM)': 'peRatio', '52 Wk Change %': 'weekRange'

            })
            response['price'] = response['price'].astype(str).str.split().str[0]

            # Remove columns with any null/empty values
            response = response.dropna(axis=1, how='any')

            # Remove the 'Unnamed: 2' column if it exists
            if 'Unnamed: 2' in response.columns:
                response = response.drop('Unnamed: 2', axis=1)

            if len(response) > 20:
                response = response.head(20)
            response = self.sanitize_data(response)
            
            
            return response
        except Exception as e:
            logger.error(f"Error in get_day_losers: {e}")
            raise

    def get_day_most_active(self):
        try:
            response = si.get_day_most_active('100')
            response = response.rename(columns={
                'Symbol': 'symbol', 'Name': 'name', 'Price': 'price', 'Change': 'change',
                'Change %': 'changePercent', 'Volume': 'volume', 'Avg Vol (3M)': 'avgVolume',
                'Market Cap': 'marketCap', 'P/E Ratio (TTM)': 'peRatio', '52 Wk Change %': 'weekRange'

            })
            response['price'] = response['price'].astype(str).str.split().str[0]
            # Remove columns with any null/empty values
            response = response.dropna(axis=1, how='any')

            # Remove the 'Unnamed: 2' column if it exists
            if 'Unnamed: 2' in response.columns:
                response = response.drop('Unnamed: 2', axis=1)

            if len(response) > 20:
                response = response.head(20)
            response = self.sanitize_data(response)

            return response
        except Exception as e:
            logger.error(f"Error in get_day_most_active: {e}")
            exc_type, exc_value, exc_tb = sys.exc_info()
            print("An exception occurred:")
            traceback.print_exception(exc_type, exc_value, exc_tb)

            raise

    def get_futures(self):
        try:
            response = si.get_futures()
            
            print("Columns in the futures DataFrame:")
            for col in response.columns:
                print(f"- {col}")
            first_row = response.iloc[0]
            for col, value in first_row.items():
                print(f"{col}: {value}")
            
            #'symbol', 'name', 'price', 'change', 'changePercent', 'volume', 'avgVolume', 'marketCap', 'peRatio', 'weekRange'
    
            
            response = response.rename(columns={
                'Symbol': 'symbol', 'Name': 'name', 'Price': 'price', 'Change': 'change',
                'Change %': 'changePercent', 'Volume': 'volume','Market Time': 'marketTime', 'Open Interest': 'openInterest'

            })
            response['price'] = response['price'].astype(str).str.split().str[0]
            # Remove columns with any null/empty values
            response = response.dropna(axis=1, how='any')

            # Remove the 'Unnamed: 2' column if it exists
            if 'Unnamed: 2' in response.columns:
                response = response.drop('Unnamed: 2', axis=1)

            if len(response) > 20:
                response = response.head(20)
            response = self.sanitize_data(response)
            return response
        except Exception as e:
            logger.error(f"Error in get_futures: {e}")
            raise

    def get_bonds(self):
        try:
            response = si.get_bonds()
            
            print("Columns in the bonds DataFrame:")
            for col in response.columns:
                print(f"- {col}")
            first_row = response.iloc[0]
            for col, value in first_row.items():
                print(f"{col}: {value}")
            
            #'symbol', 'name', 'price', 'change', 'changePercent', 'volume', 'avgVolume', 'marketCap', 'peRatio', 'weekRange'
    
            
            response = response.rename(columns={
                'Symbol': 'symbol', 'Name': 'name', 'Price': 'price', 'Change': 'change',
                'Change %': 'changePercent', 'Volume': 'volume','Market Time': 'marketTime', 'Open Interest': 'openInterest'

            })
            response['price'] = response['price'].astype(str).str.split().str[0]
            # Remove columns with any null/empty values
            response = response.dropna(axis=1, how='any')

            # Remove the 'Unnamed: 2' column if it exists
            if 'Unnamed: 2' in response.columns:
                response = response.drop('Unnamed: 2', axis=1)

            if len(response) > 20:
                response = response.head(20)

            response = self.sanitize_data(response)
            return response
        except Exception as e:
            logger.error(f"Error in get_bonds: {e}")
            raise



    def get_top_crypto(self):
        try:
            response = si.get_top_crypto()
            response = response.rename(columns={
                'Symbol': 'symbol', 'Name': 'name', 'Price': 'price', 'Change': 'change',
                'Change %': 'changePercent', 'Volume': 'volume', 'Avg Vol (3M)': 'avgVolume',
                'Market Cap': 'marketCap', 'P/E Ratio (TTM)': 'peRatio', '52 Wk Change %': 'weekRange'

            })
            response['price'] = response['price'].astype(str).str.split().str[0]
            # Remove columns with any null/empty values
            response = response.dropna(axis=1, how='any')

            # Remove the 'Unnamed: 2' column if it exists
            if 'Unnamed: 2' in response.columns:
                response = response.drop('Unnamed: 2', axis=1)

            if len(response) > 20:
                response = response.head(20)

            response = self.sanitize_data(response)
            return response
        except Exception as e:
            logger.error(f"Error in get_top_crypto: {e}")
            raise

    def get_world_indices(self):
        try:
            response = si.get_world_indices()
            print("Columns in the world_indices DataFrame:")
            for col in response.columns:
                print(f"- {col}")
            first_row = response.iloc[0]
            for col, value in first_row.items():
                print(f"{col}: {value}")
            response = response.rename(columns={
                'Symbol': 'symbol', 'Name': 'name', 'Price': 'price', 'Change': 'change',
                'Change %': 'changePercent', 'Volume': 'volume', 'Avg Vol (3M)': 'avgVolume',
                'Market Cap': 'marketCap', 'P/E Ratio (TTM)': 'peRatio', '52 Wk Change %': 'weekRange'

            })
            response['price'] = response['price'].astype(str).str.split().str[0]

            response = self.sanitize_data(response)
            return response
        except Exception as e:
            logger.error(f"Error in get_world_indices: {e}")
            raise
        


    @staticmethod
    def new_sanitize_data(data):
        if data is not None:
            return data.fillna(0).to_dict()
        return {}

    @staticmethod
    def sanitize_data(data):
        if isinstance(data, pd.DataFrame):
            data = data.replace({np.nan: "", np.inf: "", -np.inf: ""}).to_dict(orient='records')
        elif isinstance(data, list):
            for item in data:
                for key, value in item.items():
                    if isinstance(value, float):
                        if np.isnan(value) or np.isinf(value):
                            item[key] = ""
        return data

    @staticmethod
    def sanitize_data_transposed(data):
        if data is not None:
            transposed_data = data.T
            return transposed_data.fillna(0).to_dict()
        return {}
    
    def convert_timestamp_keys(self, obj):
        """Recursively convert dictionary keys that are Timestamps into strings."""
        if isinstance(obj, dict):
            return {str(k) if isinstance(k, pd.Timestamp) else k: self.convert_timestamp_keys(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_timestamp_keys(i) for i in obj]
        else:
            return obj


def main():
    try:
        # Create an instance of StockInfoService
        stock_service = StockInfoService()
        
        # Example stock symbol (e.g., AAPL for Apple)
        symbol = "AAPL"
        
        # Get stock information
        stock_info = stock_service.get_stock_news(symbol)
        # Get ticker details
        ticker_detail = stock_service.get_ticker_detail(symbol)
        
        # Print the results
        print(f"\nTicker Details for {symbol}:")
        print(f"Symbol: {ticker_detail.symbol}")
        print(f"Update Date: {ticker_detail.update_dt}")
        
        # Print some key information from stock_info
        if ticker_detail.stock_info:
            print("\nStock Information:")
            for key in ['shortName', 'sector', 'industry', 'marketCap', 'currentPrice']:
                if key in ticker_detail.stock_info:
                    print(f"{key}: {ticker_detail.stock_info[key]}")
        
        # Print recent recommendations if available
        if ticker_detail.recommendations is not None:
            print("\nRecent Recommendations:")
            print(ticker_detail.recommendations)
        
        # Print major holders if available
        if ticker_detail.holders:
            print("\nMajor Holders:")
            print(ticker_detail.holders)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
    
