from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class ETLCheckpoint(Base):
    __tablename__ = "etl_checkpoints"
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, unique=True, index=True)
    last_processed_at = Column(DateTime(timezone=True))
    last_run_id = Column(String)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ETLRun(Base):
    __tablename__ = "etl_runs"
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, unique=True, index=True)
    source = Column(String, index=True)
    status = Column(String)  # success, failure
    records_processed = Column(Integer, default=0)
    duration_ms = Column(Float)
    error_message = Column(String, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))

class RawData(Base):
    __tablename__ = "raw_data"
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True)
    external_id = Column(String, index=True)
    content = Column(JSON)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())

class CanonicalAsset(Base):
    __tablename__ = "canonical_assets"
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)  # e.g., BTC, ETH
    name = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    mappings = relationship("AssetMapping", back_populates="canonical_asset")
    unified_data = relationship("UnifiedData", back_populates="canonical_asset")

class AssetMapping(Base):
    __tablename__ = "asset_mappings"
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True)  # e.g., coingecko, coinpaprika, csv
    external_id = Column(String, index=True)  # e.g., bitcoin, btc-bitcoin
    canonical_id = Column(Integer, ForeignKey("canonical_assets.id"), index=True)
    
    canonical_asset = relationship("CanonicalAsset", back_populates="mappings")

class UnifiedData(Base):
    __tablename__ = "unified_data"
    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True)
    external_id = Column(String, index=True)
    canonical_id = Column(Integer, ForeignKey("canonical_assets.id"), index=True, nullable=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    data = Column(JSON)  # Store normalized extra fields like price, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    canonical_asset = relationship("CanonicalAsset", back_populates="unified_data")
