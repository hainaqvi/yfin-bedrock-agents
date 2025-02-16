import json
import pytest
import subprocess
from typing import Dict


class TestApiEndpoints:
    @pytest.fixture
    def invoke_lambda(self):
        def _invoke_lambda(event_file: str) -> Dict:
            try:
                result = subprocess.run(
                    ['sam', 'local', 'invoke', 'ApiFunction', '-e', f'events/{event_file}'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                return json.loads(result.stdout)
            except subprocess.CalledProcessError as e:
                print(f"Command failed with error: {e.stderr}")
                return None
            except json.JSONDecodeError as e:
                print(f"Failed to parse response: {e}")
                return None
        return _invoke_lambda

    def validate_response(self, response):
        """Helper method to validate response structure"""
        assert response is not None
        assert 'messageVersion' in response
        assert 'response' in response
        
        response_data = response['response']
        assert 'httpStatusCode' in response_data
        assert 'httpMethod' in response_data
        assert response_data['httpStatusCode'] == 200
        
        if 'body' in response_data:
            body = json.loads(response_data['body'])
            assert isinstance(body, dict)
            return body
        return response_data

    def test_world_indices(self, invoke_lambda):
        response = invoke_lambda('world-indices-event.json')
        body = self.validate_response(response)

    def test_day_gainers(self, invoke_lambda):
        response = invoke_lambda('day-gainers-event.json')
        body = self.validate_response(response)

    def test_day_most_active(self, invoke_lambda):
        response = invoke_lambda('day-most-active-event.json')
        body = self.validate_response(response)

    def test_day_losers(self, invoke_lambda):
        response = invoke_lambda('day-losers-event.json')
        body = self.validate_response(response)

    def test_bonds(self, invoke_lambda):
        response = invoke_lambda('bonds-event.json')
        body = self.validate_response(response)

    def test_ticker_detail(self, invoke_lambda):
        response = invoke_lambda('ticker-detail-event.json')
        body = self.validate_response(response)

    def test_stock_news(self, invoke_lambda):
        response = invoke_lambda('stock-news-event.json')
        body = self.validate_response(response)

    def test_cash_flow(self, invoke_lambda):
        response = invoke_lambda('cash-flow-event.json')
        body = self.validate_response(response)

    def test_income_statement(self, invoke_lambda):
        response = invoke_lambda('income-stmt-event.json')
        body = self.validate_response(response)

    def test_balance_sheet(self, invoke_lambda):
        response = invoke_lambda('balance-sheet-event.json')
        body = self.validate_response(response)

    def test_days_forex(self, invoke_lambda):
        response = invoke_lambda('days_forex.json')
        body = self.validate_response(response)

    def test_mf_best_performing(self, invoke_lambda):
        response = invoke_lambda('mf-best-perform-event.json')
        body = self.validate_response(response)

    def test_mf_top_lists(self, invoke_lambda):
        response = invoke_lambda('mf-top-lists-event.json')
        body = self.validate_response(response)

    def test_etf_hist(self, invoke_lambda):
        response = invoke_lambda('etf-hist-event.json')
        body = self.validate_response(response)

    def test_etf_trend_lists(self, invoke_lambda):
        response = invoke_lambda('etf-trend-lists-event.json')
        body = self.validate_response(response)

    def test_etf_losing(self, invoke_lambda):
        response = invoke_lambda('etf-losing-event.json')
        body = self.validate_response(response)

    def test_sector_detail(self, invoke_lambda):
        response = invoke_lambda('sector-detail-event.json')
        body = self.validate_response(response)
