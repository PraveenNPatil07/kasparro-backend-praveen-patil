import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.ingestion.base import BaseExtractor
from app.schemas.data import UnifiedDataCreate
from app.core.config import settings

class CoinPaprikaExtractor(BaseExtractor):
    def __init__(self, db, run_id: Optional[str] = None):
        super().__init__(source_name="coinpaprika_crypto", db=db, run_id=run_id)
        self.base_url = "https://api.coinpaprika.com/v1/tickers"

    def extract(self, last_checkpoint: Optional[datetime]) -> List[Dict[str, Any]]:
        headers = {}
        if settings.COINPAPRIKA_API_KEY:
            headers["Authorization"] = settings.COINPAPRIKA_API_KEY
        
        response = requests.get(self.base_url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        # Take top 50 for performance
        return data[:50]

    def transform(self, raw_data: Dict[str, Any]) -> UnifiedDataCreate:
        # CoinPaprika format: {id, name, symbol, last_updated, quotes: {USD: {price, ...}}}
        quotes = raw_data.get('quotes', {}).get('USD', {})
        
        return UnifiedDataCreate(
            source=self.source_name,
            external_id=f"cp_{raw_data['id']}",
            title=f"{raw_data['name']} ({raw_data['symbol']})",
            description=f"Market Cap: ${quotes.get('market_cap', 0):,.2f}",
            data={
                "price_usd": quotes.get('price'),
                "symbol": raw_data['symbol'],
                "rank": raw_data['rank'],
                "last_updated": raw_data['last_updated']
            }
        )

class CoinGeckoExtractor(BaseExtractor):
    def __init__(self, db, run_id: Optional[str] = None):
        super().__init__(source_name="coingecko_crypto", db=db, run_id=run_id)
        self.base_url = "https://api.coingecko.com/api/v3/coins/markets"

    def extract(self, last_checkpoint: Optional[datetime]) -> List[Dict[str, Any]]:
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 50,
            "page": 1,
            "sparkline": False
        }
        
        response = requests.get(self.base_url, params=params)
        response.raise_for_status()
        
        return response.json()

    def transform(self, raw_data: Dict[str, Any]) -> UnifiedDataCreate:
        # CoinGecko format: {id, symbol, name, current_price, market_cap, last_updated, ...}
        return UnifiedDataCreate(
            source=self.source_name,
            external_id=f"cg_{raw_data['id']}",
            title=f"{raw_data['name']} ({raw_data['symbol'].upper()})",
            description=f"Market Cap Rank: {raw_data.get('market_cap_rank')}",
            data={
                "price_usd": raw_data['current_price'],
                "symbol": raw_data['symbol'].upper(),
                "market_cap": raw_data['market_cap'],
                "last_updated": raw_data['last_updated']
            }
        )
