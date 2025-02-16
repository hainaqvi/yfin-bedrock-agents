from .base_yahoo_finance_service import BaseYahooFinanceService
import json

class MutualFundsService(BaseYahooFinanceService):
    
    
    def get_days_top_lists(self):
        
        result = {}
        result['DaysTopGainers'] =  self.get_top_gainers()
        result['DaysTopPerforming'] =  self.get_top_performing()
        result['DaysTopLosers'] =  self.get_top_losers()
                
        return result

    
    def get_best_performing(self):
        
        result = {}
        result['BestHistoricalPerforming'] =  self.get_best_historical_performance()
        result['OverallBestMutualFunds'] =  self.get_best_mutual_fund()
        
                
        return result
    
    def get_top_gainers(self):
        site = "https://finance.yahoo.com/markets/mutualfunds/gainers/"
        return self.get_yahoo_table(site)

    def get_top_losers(self):
        site = "https://finance.yahoo.com/markets/mutualfunds/losers/"
        return self.get_yahoo_table(site)

    def get_top_performing(self):
        site = "https://finance.yahoo.com/markets/mutualfunds/top-performing/"
        return self.get_yahoo_table(site)

    def get_best_historical_performance(self):
        site = "https://finance.yahoo.com/markets/mutualfunds/best-historical-performance/"
        return self.get_yahoo_table(site)

    def get_best_mutual_fund(self):
        site = "https://finance.yahoo.com/markets/mutualfunds/top/"
        return self.get_yahoo_table(site)

