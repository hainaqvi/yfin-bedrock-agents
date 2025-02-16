from .base_yahoo_finance_service import BaseYahooFinanceService

class SectorsService(BaseYahooFinanceService):
    BASE_URL = "https://finance.yahoo.com/sectors/"
    
    SECTOR_URLS = {
        "technology": "technology",
        "financial-services": "financial-services",
        "consumer-cyclical": "consumer-cyclical",
        "healthcare": "healthcare",
        "communication-services": "communication-services",
        "basic-materials": "basic-materials",
        "consumer-defensive": "consumer-defensive",
        "energy": "energy",
        "industrials": "industrials",
        "real-estate": "real-estate",
        "utilities": "utilities"
    }



    def get_sectors(self):
        site = "https://finance.yahoo.com/sectors/"
        return self.get_yahoo_table(site)

    def get_sector_detail(self, sector_name):
        if sector_name not in self.SECTOR_URLS:
            raise ValueError(f"Invalid sector name: {sector_name}")
            
        url = f"{self.BASE_URL}{self.SECTOR_URLS[sector_name]}/"
        return self.get_sector_data(url)

    
    def get_technology_sector(self):
        site = "https://finance.yahoo.com/sectors/technology/"
        return self.get_sector_data(site)


    def get_financial_services_sector(self):
        site = "https://finance.yahoo.com/sectors/financial-services/"
        return self.get_sector_data(site)


    def get_consumer_cyclical_sector(self):
        site = "https://finance.yahoo.com/sectors/consumer-cyclical/"
        return self.get_sector_data(site)

    def get_healthcare_sector(self):
        site = "https://finance.yahoo.com/sectors/healthcare/"
        return self.get_sector_data(site)

    def get_communication_services_sector(self):
        site = "https://finance.yahoo.com/sectors/communication-services/"
        return self.get_sector_data(site)

    def get_basic_materials_sector(self):
        site = "https://finance.yahoo.com/sectors/basic-materials/"
        return self.get_sector_data(site)

    def get_consumer_defensive_sector(self):
        site = "https://finance.yahoo.com/sectors/consumer-defensive/"
        return self.get_sector_data(site)

    def get_energy_sector(self):
        site = "https://finance.yahoo.com/sectors/energy/"
        return self.get_sector_data(site)

    def get_industrials_sector(self):
        site = "https://finance.yahoo.com/sectors/industrials/"
        return self.get_sector_data(site)

    def get_real_estate_sector(self):
        site = "https://finance.yahoo.com/sectors/real-estate/"
        return self.get_sector_data(site)

    def get_utilities_sector(self):
        site = "https://finance.yahoo.com/sectors/utilities/"
        return self.get_sector_data(site)



    def get_industry_detail(self, industry):
        site = "https://finance.yahoo.com/sectors/technology/semiconductors/"
        return self.get_industry_data_bsoup(site)
