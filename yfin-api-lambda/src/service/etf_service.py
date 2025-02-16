from .base_yahoo_finance_service import BaseYahooFinanceService
import json

class ETFService(BaseYahooFinanceService):
    
    def get_top_etf_lists(self):
        result = {}
        result['TopGainers'] =  self.get_top_gainers()
        result['TopPerforming'] =  self.get_top_performing()

        return result

    def get_losing_etfs(self):
        result = {}
        result['TopLosers'] = self.get_top_losers()    

        return result
    
    def get_trending_etf_lists(self):
        result = {}
        result['MostActive'] =  self.get_most_active()
        result['Trending'] =  self.get_trending()

        return result

    
    def get_etf_hist(self):
        result = {}
        result['BestHistoricalPerformance'] =  self.get_best_historical_performance()
        result['TopETF'] =  self.get_top()


        return result

    
    def get_most_active(self):
        site = "https://finance.yahoo.com/markets/etfs/most-active/"
        return self.get_yahoo_table(site)

    def get_top_gainers(self):
        site = "https://finance.yahoo.com/markets/etfs/gainers/"
        return self.get_yahoo_table(site)

    def get_top_losers(self):
        site = "https://finance.yahoo.com/markets/etfs/losers/"
        return self.get_yahoo_table(site)

    def get_top_performing(self):
        site = "https://finance.yahoo.com/markets/etfs/top-performing/"
        return self.get_yahoo_table(site)

    def get_trending(self):
        site = "https://finance.yahoo.com/markets/etfs/trending/"
        return self.get_yahoo_table(site)

    def get_best_historical_performance(self):
        site = "https://finance.yahoo.com/markets/etfs/best-historical-performance/"
        return self.get_yahoo_table(site)

    def get_top(self):
        site = "https://finance.yahoo.com/markets/etfs/top/"
        return self.get_yahoo_table(site)
