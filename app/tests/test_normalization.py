import pytest
from app.ingestion.api_source import CoinPaprikaExtractor, CoinGeckoExtractor
from app.ingestion.csv_source import CSVExtractor
from app.core.models import CanonicalAsset, UnifiedData, AssetMapping
import pandas as pd
import os

def test_canonical_identity_resolution(db):
    # 1. Mock data for CoinPaprika
    # {id, name, symbol, last_updated, quotes: {USD: {price, ...}}}
    paprika_data = {
        'id': 'btc-bitcoin',
        'name': 'Bitcoin',
        'symbol': 'BTC',
        'rank': 1,
        'last_updated': '2023-12-27T10:00:00Z',
        'quotes': {'USD': {'price': 42000.0, 'market_cap': 800000000.0}}
    }
    
    # 2. Mock data for CoinGecko
    # {id, symbol, name, current_price, market_cap, last_updated, ...}
    gecko_data = {
        'id': 'bitcoin',
        'symbol': 'btc',
        'name': 'Bitcoin',
        'current_price': 42100.0,
        'market_cap': 810000000.0,
        'market_cap_rank': 1,
        'last_updated': '2023-12-27T10:05:00Z'
    }
    
    # 3. Mock data for CSV
    csv_path = "test_crypto.csv"
    csv_df = pd.DataFrame({
        'id': ['BTC'],
        'symbol': ['BTC'],
        'name': ['Bitcoin'],
        'price': [42050.0],
        'created_at': ['2023-12-27T10:10:00Z']
    })
    csv_df.to_csv(csv_path, index=False)
    
    try:
        # Run Extractors
        paprika = CoinPaprikaExtractor(db)
        gecko = CoinGeckoExtractor(db)
        csv = CSVExtractor(db, csv_path)
        
        # Manually trigger transform and storage (or mock extract and run)
        # For simplicity, we'll just test the resolve_canonical_id logic via the extractors' transform
        
        paprika_unified = paprika.transform(paprika_data)
        db.add(UnifiedData(**paprika_unified.model_dump()))
        db.commit()
        
        gecko_unified = gecko.transform(gecko_data)
        db.add(UnifiedData(**gecko_unified.model_dump()))
        db.commit()
        
        csv_unified = csv.transform(csv_df.iloc[0].to_dict())
        db.add(UnifiedData(**csv_unified.model_dump()))
        db.commit()
        
        # VERIFY
        # 1. There should be exactly ONE CanonicalAsset for BTC
        canonical_assets = db.query(CanonicalAsset).all()
        assert len(canonical_assets) == 1
        assert canonical_assets[0].symbol == 'BTC'
        
        # 2. There should be THREE AssetMappings pointing to the same canonical asset
        mappings = db.query(AssetMapping).all()
        assert len(mappings) == 3
        for m in mappings:
            assert m.canonical_id == canonical_assets[0].id
            
        # 3. There should be THREE UnifiedData records pointing to the same canonical asset
        unified_records = db.query(UnifiedData).all()
        assert len(unified_records) == 3
        for r in unified_records:
            assert r.canonical_id == canonical_assets[0].id
            
        # 4. Check specific external IDs in mappings
        sources = {m.source: m.external_id for m in mappings}
        assert sources['coinpaprika_crypto'] == 'btc-bitcoin'
        assert sources['coingecko_crypto'] == 'bitcoin'
        assert sources['csv_crypto'] == 'BTC'
        
    finally:
        if os.path.exists(csv_path):
            os.remove(csv_path)

def test_normalization_logic(db):
    from app.core.identity import normalize_symbol
    assert normalize_symbol(" btc ") == "BTC"
    assert normalize_symbol("Eth") == "ETH"
    assert normalize_symbol(None) == "UNKNOWN"
