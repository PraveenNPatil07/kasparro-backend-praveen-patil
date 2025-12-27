from sqlalchemy.orm import Session
from app.core.models import CanonicalAsset, AssetMapping
from typing import Optional

def normalize_symbol(symbol: str) -> str:
    """Normalize symbol to uppercase and trim whitespace."""
    if not symbol:
        return "UNKNOWN"
    return symbol.strip().upper()

def resolve_canonical_id(
    db: Session, 
    source: str, 
    external_id: str, 
    symbol: str, 
    name: str
) -> int:
    """
    Resolves a source-specific asset to a canonical ID.
    1. Check for existing mapping.
    2. If not found, find or create canonical asset.
    3. Create mapping if missing.
    """
    normalized_symbol = normalize_symbol(symbol)
    
    # 1. Check for existing mapping
    mapping = db.query(AssetMapping).filter(
        AssetMapping.source == source,
        AssetMapping.external_id == external_id
    ).first()
    
    if mapping:
        return mapping.canonical_id
    
    # 2. Find or create canonical asset by symbol
    # In a real system, we might use more complex matching logic (name similarity, etc.)
    canonical_asset = db.query(CanonicalAsset).filter(
        CanonicalAsset.symbol == normalized_symbol
    ).first()
    
    if not canonical_asset:
        canonical_asset = CanonicalAsset(
            symbol=normalized_symbol,
            name=name
        )
        db.add(canonical_asset)
        db.flush()  # Get the ID
    
    # 3. Create mapping
    new_mapping = AssetMapping(
        source=source,
        external_id=external_id,
        canonical_id=canonical_asset.id
    )
    db.add(new_mapping)
    db.flush()
    
    return canonical_asset.id
