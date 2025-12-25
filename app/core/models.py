from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float
from sqlalchemy.sql import func
from app.core.database import Base

class ETLCheckpoint(Base):
    __tablename__ = "etl_checkpoints"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, unique=True, index=True)
    last_processed_at = Column(DateTime(timezone=True), nullable=True)
    last_run_id = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ETLRun(Base):
    __tablename__ = "etl_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, index=True)
    source = Column(String, index=True)
    status = Column(String)  # success, failure, in_progress
    records_processed = Column(Integer, default=0)
    duration_ms = Column(Float, nullable=True)
    error_message = Column(String, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)

class RawData(Base):
    __tablename__ = "raw_data"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True)
    external_id = Column(String, index=True)
    content = Column(JSON)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())

class UnifiedData(Base):
    __tablename__ = "unified_data"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True)
    external_id = Column(String, unique=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    data = Column(JSON)  # Store normalized extra fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
