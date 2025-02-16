from .base_yahoo_finance_service import BaseYahooFinanceService

class ForexService(BaseYahooFinanceService):
    
    def get_currencies(self):
        site = "https://finance.yahoo.com/markets/currencies/"
        return self.get_yahoo_table(site)
    
    

