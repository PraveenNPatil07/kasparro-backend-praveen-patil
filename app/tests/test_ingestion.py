import pytest
from datetime import datetime, timedelta
from app.ingestion.csv_source import CSVExtractor
from app.core.models import UnifiedData, ETLCheckpoint, ETLRun, RawData
import os
import pandas as pd

def test_csv_extraction_incremental(db):
    # Create a temporary CSV file
    csv_path = "test_products.csv"
    data = {
        'id': [1, 2],
        'title': ['P1', 'P2'],
        'description': ['D1', 'D2'],
        'price': [10.0, 20.0],
        'created_at': ['2023-01-01T10:00:00Z', '2023-01-02T10:00:00Z']
    }
    pd.DataFrame(data).to_csv(csv_path, index=False)

    extractor = CSVExtractor(db, csv_path)
    
    # 1. First run - should ingest 2 records
    extractor.run()
    
    assert db.query(UnifiedData).count() == 2
    checkpoint = db.query(ETLCheckpoint).filter(ETLCheckpoint.source == "csv_products").first()
    assert checkpoint is not None
    assert checkpoint.last_processed_at.year == 2023
    
    # 2. Add a new record
    new_data = {
        'id': [1, 2, 3],
        'title': ['P1', 'P2', 'P3'],
        'description': ['D1', 'D2', 'D3'],
        'price': [10.0, 20.0, 30.0],
        'created_at': ['2023-01-01T10:00:00Z', '2023-01-02T10:00:00Z', '2023-01-03T10:00:00Z']
    }
    pd.DataFrame(new_data).to_csv(csv_path, index=False)
    
    # 3. Second run - should only ingest the NEW record (id 3)
    extractor.run()
    
    # UnifiedData should now have 3 records (2 from first run, 1 from second)
    assert db.query(UnifiedData).count() == 3
    
    # ETLRun records should reflect the counts
    runs = db.query(ETLRun).filter(ETLRun.source == "csv_products").order_by(ETLRun.started_at.asc()).all()
    assert len(runs) == 2
    assert runs[0].records_processed == 2
    assert runs[1].records_processed == 1
    
    # Cleanup
    if os.path.exists(csv_path):
        os.remove(csv_path)

def test_extraction_failure_recovery(db):
    # Test that a failed run records failure and can be resumed
    csv_path = "fail_test.csv"
    try:
        pd.DataFrame({'id': [1], 'title': ['P1'], 'price': [10], 'created_at': ['2023-01-01T10:00:00Z']}).to_csv(csv_path, index=False)
        
        extractor = CSVExtractor(db, csv_path)
        
        # Mock extract to fail
        original_extract = extractor.extract
        def failing_extract(checkpoint):
            raise Exception("Simulated failure")
        extractor.extract = failing_extract
        
        with pytest.raises(Exception):
            extractor.run()
        
        # Check that the run was recorded as failure
        run = db.query(ETLRun).filter(ETLRun.source == "csv_products").first()
        assert run is not None, "ETLRun record should exist"
        assert run.status == "failure"
        assert run.error_message == "Simulated failure"
        
        # Restore extract and run again
        extractor.extract = original_extract
        extractor.run()
        
        # Should now succeed and have 1 record
        assert db.query(UnifiedData).count() == 1
        new_run = db.query(ETLRun).filter(ETLRun.source == "csv_products", ETLRun.status == "success").first()
        assert new_run is not None
    finally:
        if os.path.exists(csv_path):
            try:
                os.remove(csv_path)
            except PermissionError:
                pass # Ignore if still locked, though not ideal
