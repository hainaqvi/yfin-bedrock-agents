import pandas as pd
import numpy as np
import requests, logging
from bs4 import BeautifulSoup
import yfinance as yf


# Define a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class BaseYahooFinanceService:
    def __init__(self):
        print(f"{self.__class__.__name__} initialized")

    def get_yahoo_tables(self, site, headers={'User-agent': 'Mozilla/5.0'}, nbr_of_tbl=4):
        """Fetches and processes tables from Yahoo Finance."""
        try:
            tables = pd.read_html(requests.get(site, headers=headers).text)
            response = tables[1]
            for col in response.columns:
                print(f"- {col}")
            first_row = response.iloc[0]
            for col, value in first_row.items():
                print(f"{col}: {value}")

            return self.sanitize_data(response)
        except Exception as e:
            logger.error(f"Error fetching data from {site}: {e}")
            raise


    def get_yahoo_table(self, site, headers={'User-agent': 'Mozilla/5.0'}, rename=True):
        """Fetches and processes a table from Yahoo Finance."""
        try:
            tables = pd.read_html(requests.get(site, headers=headers).text)
            
            response = tables[0]
            #for col in response.columns:
                #print(f"- {col}")
            first_row = response.iloc[0]
            #for col, value in first_row.items():
                #print(f"{col}: {value}")
            if rename:
                if 'Price' in response:
                    response['Price'] = response['Price'].astype(str).str.split().str[0]
                response = response.rename(columns={
                    'Symbol': 'symbol', 'Name': 'name', 'Price': 'price', 'Change': 'change',
                    'Change %': 'changePercent', 'Volume': 'volume', 'Avg Vol (3M)': 'avgVolume',
                    'Market Cap': 'marketCap', 'P/E Ratio (TTM)': 'peRatio', '52 Wk Change %': 'weekRange'
                })
            return self.sanitize_data(response)
        except Exception as e:
            logger.error(f"Error fetching data from {site}: {e}")
            raise
        
    def get_sector_data(self, site):
        sector_data = {}
        headers={'User-agent': 'Mozilla/5.0'}
        try:
            tables = pd.read_html(requests.get(site, headers=headers).text)
            industries = tables[1]
            self.sanitize_data(industries)
            sector_data['industries'] = industries.to_dict(orient="records")  # Convert DataFrame to list of dicts
            
            large_equities = tables[2]
            self.sanitize_data(large_equities)
            sector_data['large_equities'] = large_equities.to_dict(orient="records")
            
            etf_opportunities = tables[3]
            self.sanitize_data(etf_opportunities)
            sector_data['etf_opportunities'] = etf_opportunities.to_dict(orient="records")
            
            fund_opportunities = tables[4]
            self.sanitize_data(fund_opportunities)
            sector_data['fund_opportunities'] = fund_opportunities.to_dict(orient="records")
            
            return sector_data

        except Exception as e:
            logging.error(f"Error fetching data from {site}: {e}")
            raise

    
    def get_industry_data(self, industry):
        industry_response = {}
        industry_data  = yf.Industry(industry)
        industry_response['top_performing_companies'] = industry_data.top_performing_companies.to_dict(orient="records")
        industry_response['top_growth_companies'] = industry_data.top_growth_companies.to_dict(orient="records")
        return industry_response



        
    def get_industry_data_bsoup(self, site):
        sector_data = {}
        headers = {'User-agent': 'Mozilla/5.0'}
        
        try:
            response = requests.get(site, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Example parsing tables with BeautifulSoup if available
            tables = pd.read_html(response.text)
            
            industries = tables[1]
            self.sanitize_data(industries)
            sector_data['industries'] = industries.to_dict(orient="records")

            large_equities = tables[2]
            self.sanitize_data(large_equities)
            sector_data['large_equities'] = large_equities.to_dict(orient="records")

            etf_opportunities = tables[3]
            self.sanitize_data(etf_opportunities)
            sector_data['etf_opportunities'] = etf_opportunities.to_dict(orient="records")

            fund_opportunities = tables[4]
            self.sanitize_data(fund_opportunities)
            sector_data['fund_opportunities'] = fund_opportunities.to_dict(orient="records")

            return sector_data

        except Exception as e:
            logging.error(f"Error fetching data from {site}: {e}")
            raise

    @staticmethod
    def sanitize_data(data):
        """Sanitizes data by replacing NaN and Inf values."""
        if isinstance(data, pd.DataFrame):
            data = data.replace({np.nan: "", np.inf: "", -np.inf: ""}).to_dict(orient='records')
        elif isinstance(data, list):
            for item in data:
                for key, value in item.items():
                    if isinstance(value, float) and (np.isnan(value) or np.isinf(value)):
                        item[key] = ""
        return data
