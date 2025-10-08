"""Financial and market data service."""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

import yfinance as yf
from pycoingecko import CoinGeckoAPI
import httpx

from bot.config import settings
from bot.services.n8n import n8n_service
from bot.utils.metrics import finance_requests


logger = logging.getLogger(__name__)


class FinanceService:
    """Service for financial and market data."""
    
    def __init__(self):
        self.cg = CoinGeckoAPI()
        self.alpha_vantage_key = settings.alpha_vantage_api_key
        self.quickchart_base = "https://quickchart.io/chart"
        
        # Cache for market data
        self._cache = {}
        self._cache_expiry = {}
    
    def _is_cache_valid(self, key: str, ttl_minutes: int = 5) -> bool:
        """Check if cached data is still valid."""
        if key not in self._cache_expiry:
            return False
        
        expiry_time = self._cache_expiry[key]
        return datetime.now() < expiry_time
    
    def _set_cache(self, key: str, data: Any, ttl_minutes: int = 5) -> None:
        """Set cached data with expiry."""
        self._cache[key] = data
        self._cache_expiry[key] = datetime.now() + timedelta(minutes=ttl_minutes)
    
    async def get_stock_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get stock price and basic info."""
        try:
            finance_requests.inc()
            
            cache_key = f"stock_{symbol.upper()}"
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]
            
            # Run in thread pool since yfinance is synchronous
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            info = await loop.run_in_executor(None, ticker.info)
            
            if not info or "regularMarketPrice" not in info:
                return None
            
            stock_data = {
                "symbol": symbol.upper(),
                "name": info.get("longName", symbol),
                "price": info.get("regularMarketPrice"),
                "change": info.get("regularMarketChange"),
                "change_percent": info.get("regularMarketChangePercent"),
                "volume": info.get("regularMarketVolume"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "dividend_yield": info.get("dividendYield"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                "currency": info.get("currency", "USD"),
                "exchange": info.get("exchange"),
                "sector": info.get("sector"),
                "industry": info.get("industry")
            }
            
            self._set_cache(cache_key, stock_data)
            return stock_data
            
        except Exception as e:
            logger.error(f"Error getting stock price for {symbol}: {e}")
            return None
    
    async def get_crypto_price(self, coin_id: str) -> Optional[Dict[str, Any]]:
        """Get cryptocurrency price and info."""
        try:
            finance_requests.inc()
            
            cache_key = f"crypto_{coin_id.lower()}"
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]
            
            # Run in thread pool since pycoingecko is synchronous
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None,
                self.cg.get_price,
                coin_id,
                "usd",
                True,  # include_market_cap
                True,  # include_24hr_vol
                True,  # include_24hr_change
                True   # include_last_updated_at
            )
            
            if coin_id not in data:
                return None
            
            coin_data = data[coin_id]
            
            # Get additional coin info
            coin_info = await loop.run_in_executor(None, self.cg.get_coin, coin_id)
            
            crypto_data = {
                "id": coin_id,
                "symbol": coin_info.get("symbol", "").upper(),
                "name": coin_info.get("name", coin_id),
                "price": coin_data.get("usd"),
                "change_24h": coin_data.get("usd_24h_change"),
                "market_cap": coin_data.get("usd_market_cap"),
                "volume_24h": coin_data.get("usd_24h_vol"),
                "last_updated": coin_data.get("last_updated_at"),
                "rank": coin_info.get("market_cap_rank"),
                "total_supply": coin_info.get("market_data", {}).get("total_supply"),
                "circulating_supply": coin_info.get("market_data", {}).get("circulating_supply"),
                "ath": coin_info.get("market_data", {}).get("ath", {}).get("usd"),
                "atl": coin_info.get("market_data", {}).get("atl", {}).get("usd")
            }
            
            self._set_cache(cache_key, crypto_data)
            return crypto_data
            
        except Exception as e:
            logger.error(f"Error getting crypto price for {coin_id}: {e}")
            return None
    
    async def search_crypto(self, query: str) -> List[Dict[str, Any]]:
        """Search for cryptocurrency by name or symbol."""
        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(None, self.cg.search, query)
            
            coins = results.get("coins", [])[:10]  # Limit to 10 results
            
            return [
                {
                    "id": coin["id"],
                    "name": coin["name"],
                    "symbol": coin["symbol"].upper(),
                    "market_cap_rank": coin.get("market_cap_rank")
                }
                for coin in coins
            ]
            
        except Exception as e:
            logger.error(f"Error searching crypto: {e}")
            return []
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """Get overall market overview."""
        try:
            # Get major indices
            indices = ["^GSPC", "^DJI", "^IXIC", "^VIX"]  # S&P 500, Dow, NASDAQ, VIX
            
            loop = asyncio.get_event_loop()
            market_data = {}
            
            for index in indices:
                ticker = await loop.run_in_executor(None, yf.Ticker, index)
                info = await loop.run_in_executor(None, ticker.info)
                
                if info and "regularMarketPrice" in info:
                    market_data[index] = {
                        "name": info.get("longName", index),
                        "price": info.get("regularMarketPrice"),
                        "change": info.get("regularMarketChange"),
                        "change_percent": info.get("regularMarketChangePercent")
                    }
            
            # Get crypto market overview
            crypto_global = await loop.run_in_executor(None, self.cg.get_global)
            
            market_data["crypto"] = {
                "total_market_cap": crypto_global.get("data", {}).get("total_market_cap", {}).get("usd"),
                "total_volume": crypto_global.get("data", {}).get("total_volume", {}).get("usd"),
                "bitcoin_dominance": crypto_global.get("data", {}).get("market_cap_percentage", {}).get("btc")
            }
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error getting market overview: {e}")
            return {}
    
    async def generate_price_chart(
        self,
        symbol: str,
        period: str = "1mo",
        chart_type: str = "line"
    ) -> Optional[str]:
        """Generate price chart using QuickChart."""
        try:
            # Get historical data
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            hist = await loop.run_in_executor(None, ticker.history, period)
            
            if hist.empty:
                return None
            
            # Prepare data for chart
            dates = [date.strftime("%Y-%m-%d") for date in hist.index]
            prices = hist["Close"].tolist()
            
            # Create chart configuration
            chart_config = {
                "type": chart_type,
                "data": {
                    "labels": dates,
                    "datasets": [{
                        "label": f"{symbol.upper()} Price",
                        "data": prices,
                        "borderColor": "rgb(75, 192, 192)",
                        "backgroundColor": "rgba(75, 192, 192, 0.2)",
                        "fill": chart_type == "line"
                    }]
                },
                "options": {
                    "title": {
                        "display": True,
                        "text": f"{symbol.upper()} - {period.upper()}"
                    },
                    "scales": {
                        "y": {
                            "beginAtZero": False
                        }
                    }
                }
            }
            
            # Generate chart URL
            chart_url = f"{self.quickchart_base}?c={json.dumps(chart_config)}"
            
            return chart_url
            
        except Exception as e:
            logger.error(f"Error generating chart for {symbol}: {e}")
            return None
    
    async def get_technical_indicators(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get technical indicators using Alpha Vantage."""
        if not self.alpha_vantage_key:
            return None
        
        try:
            base_url = "https://www.alphavantage.co/query"
            
            # Get RSI
            async with httpx.AsyncClient() as client:
                rsi_response = await client.get(base_url, params={
                    "function": "RSI",
                    "symbol": symbol,
                    "interval": "daily",
                    "time_period": 14,
                    "series_type": "close",
                    "apikey": self.alpha_vantage_key
                })
                
                rsi_data = rsi_response.json()
                
                # Get MACD
                macd_response = await client.get(base_url, params={
                    "function": "MACD",
                    "symbol": symbol,
                    "interval": "daily",
                    "series_type": "close",
                    "apikey": self.alpha_vantage_key
                })
                
                macd_data = macd_response.json()
            
            indicators = {}
            
            # Parse RSI
            if "Technical Analysis: RSI" in rsi_data:
                rsi_values = rsi_data["Technical Analysis: RSI"]
                latest_date = max(rsi_values.keys())
                indicators["rsi"] = float(rsi_values[latest_date]["RSI"])
            
            # Parse MACD
            if "Technical Analysis: MACD" in macd_data:
                macd_values = macd_data["Technical Analysis: MACD"]
                latest_date = max(macd_values.keys())
                latest_macd = macd_values[latest_date]
                indicators["macd"] = {
                    "macd": float(latest_macd["MACD"]),
                    "signal": float(latest_macd["MACD_Signal"]),
                    "histogram": float(latest_macd["MACD_Hist"])
                }
            
            return indicators if indicators else None
            
        except Exception as e:
            logger.error(f"Error getting technical indicators for {symbol}: {e}")
            return None
    
    async def create_price_alert(
        self,
        user_id: int,
        symbol: str,
        target_price: float,
        condition: str = "above"
    ) -> bool:
        """Create a price alert via n8n."""
        try:
            alert_data = {
                "user_id": user_id,
                "symbol": symbol.upper(),
                "target_price": target_price,
                "condition": condition,
                "created_at": datetime.now().isoformat()
            }
            
            result = await n8n_service.trigger_n8n_workflow("price_alert", alert_data)
            return result is not None
            
        except Exception as e:
            logger.error(f"Error creating price alert: {e}")
            return False


# Global finance service instance
finance_service = FinanceService()
