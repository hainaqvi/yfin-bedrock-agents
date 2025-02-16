import json
from time import time
from typing_extensions import Annotated
from aws_lambda_powertools.event_handler.openapi.params import Query
from service.stock_info_service import StockInfoService 
from service.etf_service import ETFService 
from service.mutual_funds_service import MutualFundsService
from service.forex_service import ForexService
from service.sector_service import SectorsService
from service.industry_service import IndustryService
from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import BedrockAgentResolver
from aws_lambda_powertools.utilities.typing import LambdaContext

tracer = Tracer()
logger = Logger()
app = BedrockAgentResolver()
stock_info_service = StockInfoService()
etf_service = ETFService()
mutual_funds_service = MutualFundsService()
forex_service = ForexService()
sector_service = SectorsService()
industry_service = IndustryService()

@app.get("/current_time", description="Gets the current time in seconds")
@tracer.capture_method
def current_time() -> dict:
    return {
        "messageVersion": "1.0",
        "response": {
            "timeInSeconds": int(time())
        }
    }


@app.get("/ticker_detail", description="Get given symbol's detail")  
@tracer.capture_method
def get_ticker_detail( symbol: Annotated[str, Query(description="Get given symbol's detail")], ):
    """Handler for retrieving ticker details."""
    try:
        #symbol = event.get("queryStringParameters", {}).get("symbol", "AAPL")
        result = stock_info_service.get_ticker_detail(symbol)
        logger.info(f"Successfully retrieved ticker detail for {symbol} size is {len(json.dumps(result)) }")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": result
        }
    except Exception as e:
        logger.error(f"Error in get_ticker_detail {symbol}: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}



@app.get("/balance_sheet", description="Get stocks's balance sheet")  
@tracer.capture_method
def get_blance_sheet( symbol: Annotated[str, Query(description="Get stocks's balance sheet")], ):
    """Handler for retrieving balance_sheet."""
    try:
        #symbol = event.get("queryStringParameters", {}).get("symbol", "AAPL")
        result = stock_info_service.get_balance_sheet(symbol)
        logger.info(f"Successfully retrieved balance sheet for {symbol} size is {len(json.dumps(result)) }")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": result
        }
    except Exception as e:
        logger.error(f"Error in get_balance_sheet {symbol}: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}



@app.get("/cash_flow", description="Get Stock's cash flow")  
@tracer.capture_method
def get_cash_flow( symbol: Annotated[str, Query(description="Get Stock's cash flow")], ):
    """Handler for retrieving cash flow."""
    try:
        result = stock_info_service.get_cash_flow(symbol)
        logger.info(f"Successfully retrieved cash flow for {symbol} size is {len(json.dumps(result)) }")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": result
        }
    except Exception as e:
        logger.error(f"Error in get_cash_flow {symbol}: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}



@app.get("/income_stmt", description="Get Stock's income statement")  
@tracer.capture_method
def get_income_stmt( symbol: Annotated[str, Query(description="Get Stock's income statement")], ):
    """Handler for retrieving income statment."""
    try:
        result = stock_info_service.get_income_stmt(symbol)
        logger.info(f"Successfully retrieved income statement for {symbol} size is {len(json.dumps(result)) }")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": result
        }
    except Exception as e:
        logger.error(f"Error in get_income_stmt {symbol}: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}



@app.get("/stock_news", description="Get stock news for given symbol")  
@tracer.capture_method
def get_stock_news(symbol: Annotated[str, Query(description="Get stock news for given symbol.")], ):
    """Handler for retrieving stock news."""
    try:
        result = stock_info_service.get_stock_news(symbol)
        logger.info(f"Successfully retrieved stock news for {symbol} size is {len(json.dumps(result)) }")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": result
        }
    except Exception as e:
        logger.error(f"Error in get_stock_news {symbol}: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

    
    
@app.get("/day_gainers", description="Days top gaining tickers")  
@tracer.capture_method
def get_day_gainers():
    """Handler for retrieving day gainers."""
    try:
        result = stock_info_service.get_day_gainers()
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": result
        }
    except Exception as e:
        logger.error(f"Error in get_day_gainers: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


@app.get("/day_losers", description="Days top losing tickers")
@tracer.capture_method
def get_day_losers():
    """Handler for retrieving day losers."""
    try:
        result = stock_info_service.get_day_losers()
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": result
        }
    except Exception as e:
        logger.error(f"Error in get_day_losers: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


@app.get("/most_active", description="Days most active tickers")
@tracer.capture_method
def get_day_most_active():
    """Handler for retrieving most active stocks of the day."""
    try:
        result = stock_info_service.get_day_most_active()
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": result
        }
    except Exception as e:
        logger.error(f"Error in get_day_most_active: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


@app.get("/top_etf_lists", description="Day's Top ETF lists, TopGainers and TopPerformig")
@tracer.capture_method
def get_top_etf_lists():
    """Handler for retrieving ETF market data."""
    try:
        result = etf_service.get_top_etf_lists()
        logger.info(f"Successfully retrieved ETF Lists size is {len(json.dumps(result)) }")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": result
        }
    except Exception as e:
        logger.error(f"Error in get_etf_lists: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


@app.get("/losing_etfs", description="Day's losting ETFss")
@tracer.capture_method
def get_losing_etfs():
    """Handler for retrieving ETF market data."""
    try:
        result = etf_service.get_etf_hist()
        logger.info(f"Successfully retrieved losing ETFs size is {len(json.dumps(result)) }")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": result
        }
    except Exception as e:
        logger.error(f"Error in get_losing_etfs: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

@app.get("/trending_etf_lists", description="MostActive and Trending ETF lists")
@tracer.capture_method
def get_trending_etf_lists():
    """Handler for retrieving ETF market data."""
    try:
        result = etf_service.get_trending_etf_lists()
        logger.info(f"Successfully retrieved get_trending_etf_lists size is {len(json.dumps(result)) }")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": result
        }
    except Exception as e:
        logger.error(f"Error in get_trending_etf_lists: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}



@app.get("/etf_hist", description="Historical Performance and Top ETFs")
@tracer.capture_method
def get_etf_hist():
    """Handler for retrieving ETF market data."""
    try:
        result = etf_service.get_etf_hist()
        logger.info(f"Successfully retrieved get_trending_etf_lists size is {len(json.dumps(result)) }")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": result
        }
    except Exception as e:
        logger.error(f"Error in get_etf_hist: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

@app.get("/mf_days_top_lists", description="Mutual Funds Day's Top Lists top gainers, top performing, Top Losers")
@tracer.capture_method
def get_mf_days_top_lists():
    """Handler for retrieving ETF market data."""
    try:
        result = mutual_funds_service.get_days_top_lists()
        logger.info(f"Successfully retrieved get_mf_days_top_lists size is {len(json.dumps(result)) }")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": result
        }
    except Exception as e:
        logger.error(f"Error in get_mf_days_top_lists: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

@app.get("/mf_best_performing", description="Overall Best performing lists such as BestHistoricalPerforming and OverallBestPerformingMutual")
@tracer.capture_method
def get_mf_best_performing():
    """Handler for retrieving ETF market data."""
    try:
        result = mutual_funds_service.get_best_performing()
        logger.info(f"Successfully retrieved get_mf_best_performing size is {len(json.dumps(result)) }")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": result
        }
    except Exception as e:
        logger.error(f"Error in get_mf_best_performing: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


@app.get("/days_forex", description="Day's currencies performance")
@tracer.capture_method
def get_days_forex():
    """Handler for retrieving Forex market data."""
    try:
        result = forex_service.get_currencies()
        logger.info(f"Successfully retrieved get_days_forex size is {len(json.dumps(result)) }")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": result
        }
    except Exception as e:
        logger.error(f"Error in get_days_forex: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
    
    
@app.get("/futures", description="futures market tickers")
@tracer.capture_method
def get_futures():
    """Handler for retrieving futures market data."""
    try:
        result = stock_info_service.get_futures()
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": result
        }
    except Exception as e:
        logger.error(f"Error in get_futures: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


@app.get("/bonds", description="markets bonds tickers")
@tracer.capture_method
def get_bonds():
    """Handler for retrieving bonds market data."""
    try:
        result = stock_info_service.get_bonds()
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": result
        }
    except Exception as e:
        logger.error(f"Error in get_bonds: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


@app.get("/top_crypto", description="Days top crypto ")
@tracer.capture_method
def get_top_crypto():
    """Handler for retrieving top cryptocurrencies."""
    try:
        result = stock_info_service.get_top_crypto()
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": result
        }
    except Exception as e:
        logger.error(f"Error in get_top_crypto: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

@app.get("/market_indices", description="market indices status ")
@tracer.capture_method
def get_market_indices():
    """Handler for retrieving market indices data."""
    try:
        result = stock_info_service.get_world_indices()
        # Filter only necessary fields
        result = [{
            'symbol': item['symbol'],
            'name': item['name'],
            'price': item['price'],
            'change': item['change']
            # Add only the fields you need
        } for item in result]
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": result
        }
    except Exception as e:
        logger.error(f"Error in get_market_indices: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


@app.get("/sectors", description="Get list of sectors ")
@tracer.capture_method
def get_sectors():
    """Handler for retrieving Forex market data."""
    try:
        result = sector_service.get_sectors()
        logger.info(f"Successfully retrieved get_sectors size is {len(json.dumps(result)) }")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": result
        }
    except Exception as e:
        logger.error(f"Error in get_sectors: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


@app.get("/sector_detail", description="Get Sector detail ")
@tracer.capture_method
def get_sector_detail( sector: Annotated[str, Query(description="Get given sectors's detail")]):
    """Handler for retrieving Sector detail"""
    try:
        logger.info(f"**Get get_sector_detail for {sector}")
        result = sector_service.get_sector_detail(sector)
        logger.info(f"Successfully retrieved get_sector_detail size is {len(json.dumps(result)) }")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": result
        }
    except Exception as e:
        logger.error(f"Error in get_sector_detail: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

@app.get("/industry_detail", description="Get Industry detail ")
@tracer.capture_method
def get_industry_detail(industry: Annotated[str, Query(description="Get given industry's detail")]):
    """Handler for retrieving industry detail"""
    try:
        result = industry_service.get_industry_data_by_name(industry)
        logger.info(f"Successfully retrieved get_industry_detail size is {len(json.dumps(result)) }")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": result
        }
    except Exception as e:
        logger.error(f"Error in get_industry_detail: {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}

@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext):
    return app.resolve(event, context)


if __name__ == "__main__":  
    print(app.get_openapi_json_schema())