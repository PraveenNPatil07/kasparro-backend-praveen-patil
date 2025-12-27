import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.ingestion.base import BaseExtractor
from app.schemas.data import UnifiedDataCreate
from app.core.identity import resolve_canonical_id
import os

class CSVExtractor(BaseExtractor):
    def __init__(self, db, file_path: str, run_id: Optional[str] = None):
        super().__init__(source_name="csv_crypto", db=db, run_id=run_id)
        self.file_path = file_path

    def extract(self, last_checkpoint: Optional[datetime]) -> List[Dict[str, Any]]:
        if not os.path.exists(self.file_path):
            return []
        
        df = pd.read_csv(self.file_path)
        # Convert created_at to datetime (aware) for filtering
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'], utc=True)
            
            if last_checkpoint:
                from datetime import timezone
                if last_checkpoint.tzinfo is None:
                    last_checkpoint = last_checkpoint.replace(tzinfo=timezone.utc)
                
                # Convert to pandas Timestamp for reliable comparison with datetime64[ns, UTC]
                ts_checkpoint = pd.Timestamp(last_checkpoint)
                # Filter for records newer than the checkpoint
                df = df[df['created_at'] > ts_checkpoint]
        
        # Convert all timestamps to ISO strings before to_dict
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        return df.to_dict('records')

    def transform(self, raw_data: Dict[str, Any]) -> UnifiedDataCreate:
        # Expected CSV columns: id, symbol, name, price, created_at
        symbol = raw_data.get('symbol', 'UNKNOWN')
        name = raw_data.get('name', symbol)
        external_id = str(raw_data.get('id', symbol))
        
        canonical_id = resolve_canonical_id(
            db=self.db,
            source=self.source_name,
            external_id=external_id,
            symbol=symbol,
            name=name
        )
        
        return UnifiedDataCreate(
            source=self.source_name,
            external_id=f"csv_{external_id}",
            canonical_id=canonical_id,
            title=f"{name} ({symbol})",
            description=f"CSV Price: {raw_data.get('price', 0)}",
            data={
                "price": float(raw_data.get('price', 0)),
                "symbol": symbol,
                "original_created_at": str(raw_data.get('created_at', ''))
            }
        )
