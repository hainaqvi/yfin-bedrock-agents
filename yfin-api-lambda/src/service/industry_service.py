from .base_yahoo_finance_service import BaseYahooFinanceService
import pandas as pd
import numpy as np
import requests, logging
import json



class IndustryService(BaseYahooFinanceService):




    def get_industry_data_by_name(self, industry):
        return self.get_industry_data(industry)
       


  