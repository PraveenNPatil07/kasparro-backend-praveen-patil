from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import time
import uuid
from sqlalchemy.orm import Session
from app.core.models import ETLCheckpoint, ETLRun, RawData, UnifiedData
from app.schemas.data import RawDataCreate, UnifiedDataCreate

class BaseExtractor(ABC):
    def __init__(self, source_name: str, db: Session, run_id: Optional[str] = None):
        self.source_name = source_name
        self.db = db
        self.run_id = run_id or str(uuid.uuid4())

    @abstractmethod
    def extract(self, last_checkpoint: Optional[datetime]) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def transform(self, raw_data: Dict[str, Any]) -> UnifiedDataCreate:
        pass

    def get_checkpoint(self) -> Optional[datetime]:
        checkpoint = self.db.query(ETLCheckpoint).filter(ETLCheckpoint.source == self.source_name).first()
        return checkpoint.last_processed_at if checkpoint else None

    def run(self):
        start_time = time.time()
        records_processed = 0
        status = "success"
        error_message = None
        
        # Ensure we have a unique run_id for this specific execution
        current_run_id = str(uuid.uuid4())

        # Record start of run
        etl_run = ETLRun(
            run_id=current_run_id,
            source=self.source_name,
            status="in_progress",
            started_at=datetime.now(timezone.utc)
        )
        self.db.add(etl_run)
        self.db.commit()
        etl_run_id = etl_run.id

        try:
            # Use a savepoint for the actual work so we can rollback work without rolling back the ETLRun record
            with self.db.begin_nested():
                last_checkpoint = self.get_checkpoint()
                raw_records = self.extract(last_checkpoint)
                
                latest_timestamp = last_checkpoint

                for raw_record in raw_records:
                    # 1. Store Raw Data
                    external_id = str(raw_record.get('id') or raw_record.get('guid') or uuid.uuid4())
                    
                    # Check if raw data already exists for this source and external_id
                    existing_raw = self.db.query(RawData).filter(
                        RawData.source == self.source_name,
                        RawData.external_id == external_id
                    ).first()

                    if not existing_raw:
                        new_raw = RawData(
                            source=self.source_name,
                            external_id=external_id,
                            content=raw_record
                        )
                        self.db.add(new_raw)
                    
                    # 2. Transform and Store Clean Data
                    unified_schema = self.transform(raw_record)
                    
                    # UPSERT logic for UnifiedData
                    existing_unified = self.db.query(UnifiedData).filter(
                        UnifiedData.source == unified_schema.source,
                        UnifiedData.external_id == unified_schema.external_id
                    ).first()

                    if existing_unified:
                        existing_unified.title = unified_schema.title
                        existing_unified.description = unified_schema.description
                        existing_unified.data = unified_schema.data
                        existing_unified.canonical_id = unified_schema.canonical_id
                    else:
                        new_unified = UnifiedData(
                            source=unified_schema.source,
                            external_id=unified_schema.external_id,
                            canonical_id=unified_schema.canonical_id,
                            title=unified_schema.title,
                            description=unified_schema.description,
                            data=unified_schema.data
                        )
                        self.db.add(new_unified)

                    records_processed += 1
                    
                    # Update latest_timestamp if available in record
                    record_ts_str = raw_record.get('last_updated') or raw_record.get('created_at') or raw_record.get('published')
                    if record_ts_str:
                        try:
                            if isinstance(record_ts_str, str):
                                record_ts = datetime.fromisoformat(record_ts_str.replace('Z', '+00:00'))
                            else:
                                record_ts = record_ts_str
                            
                            if record_ts.tzinfo is None:
                                record_ts = record_ts.replace(tzinfo=timezone.utc)
                                
                            if not latest_timestamp or record_ts > latest_timestamp:
                                latest_timestamp = record_ts
                        except (ValueError, TypeError):
                            pass

                if latest_timestamp:
                    self.update_checkpoint_internal(latest_timestamp, current_run_id)
            
            status = "success"
        except Exception as e:
            status = "failure"
            error_message = str(e)
            raise e
        finally:
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            
            # Get a fresh instance to avoid detached/expired issues
            etl_run = self.db.get(ETLRun, etl_run_id)
            if etl_run:
                etl_run.status = status
                etl_run.records_processed = records_processed
                etl_run.duration_ms = duration_ms
                etl_run.error_message = error_message
                etl_run.ended_at = datetime.now(timezone.utc)
                self.db.commit()

    def update_checkpoint_internal(self, last_processed_at: datetime, run_id: str):
        checkpoint = self.db.query(ETLCheckpoint).filter(ETLCheckpoint.source == self.source_name).first()
        if not checkpoint:
            checkpoint = ETLCheckpoint(source=self.source_name)
            self.db.add(checkpoint)
        
        checkpoint.last_processed_at = last_processed_at
        checkpoint.last_run_id = run_id
        self.db.flush()
