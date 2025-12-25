from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any, Dict
from datetime import datetime

class RawDataCreate(BaseModel):
    source: str
    external_id: str
    content: Dict[str, Any]

class UnifiedDataCreate(BaseModel):
    source: str
    external_id: str
    title: str
    description: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)

class UnifiedDataRead(UnifiedDataCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ETLStats(BaseModel):
    source: str
    records_processed: int
    status: str
    duration_ms: float
    last_run_at: Optional[datetime]
    error_message: Optional[str] = None

class HealthStatus(BaseModel):
    db_connected: bool
    last_etl_run: Optional[datetime]
    total_runs: int
    success_runs: int
    status: str
