from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from app.core.database import get_db
from app.core.models import UnifiedData, ETLRun, ETLCheckpoint
from app.schemas.data import UnifiedDataRead, HealthStatus, ETLStats
from app.core.rate_limiter import rate_limiter
from app.ingestion.csv_source import CSVExtractor
import shutil
import os
import uuid

router = APIRouter()

@router.get("/data", response_model=List[UnifiedDataRead], dependencies=[Depends(rate_limiter)])
def get_data(
    skip: int = 0,
    limit: int = 100,
    source: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(UnifiedData)
    
    if source:
        query = query.filter(UnifiedData.source == source)
    
    if search:
        query = query.filter(UnifiedData.title.ilike(f"%{search}%") | UnifiedData.description.ilike(f"%{search}%"))
    
    return query.order_by(UnifiedData.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/health", response_model=HealthStatus)
def health_check(db: Session = Depends(get_db)):
    try:
        # Check DB connectivity
        db.execute(func.now())
        db_connected = True
    except Exception:
        db_connected = False
    
    # Get last ETL run
    last_run = db.query(ETLRun).order_by(ETLRun.started_at.desc()).first()
    
    # Get total runs count (unique batch runs)
    total_runs = db.query(ETLRun.run_id).distinct().count()
    # success_runs is more complex: a batch is successful if ALL its sources succeeded?
    # Or just count how many unique run_ids have at least one success?
    # Let's count how many unique run_ids exist where ALL sources succeeded.
    
    # Subquery to find run_ids that have any failure
    failed_runs = db.query(ETLRun.run_id).filter(ETLRun.status == "failure").distinct().subquery()
    
    # Count run_ids that are not in the failed_runs list
    success_runs = db.query(ETLRun.run_id).filter(
        ~ETLRun.run_id.in_(failed_runs)
    ).distinct().count()
    
    return HealthStatus(
        db_connected=db_connected,
        last_etl_run=last_run.ended_at if last_run else None,
        total_runs=total_runs,
        success_runs=success_runs,
        status="healthy" if db_connected else "degraded"
    )

@router.post("/trigger")
def trigger_etl():
    import subprocess
    import os
    try:
        # Run the runner.py script in a separate process
        import sys
        script_path = os.path.join(os.getcwd(), "app", "ingestion", "runner.py")
        subprocess.Popen([sys.executable, script_path])
        return {"status": "triggered"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    # Create temp directory if not exists
    temp_dir = "temp_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    
    file_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{file.filename}")
    
    try:
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Run extraction immediately
        batch_run_id = f"manual_{uuid.uuid4().hex[:8]}"
        extractor = CSVExtractor(db, file_path, run_id=batch_run_id)
        results = extractor.run()
        
        # Cleanup
        os.remove(file_path)
        
        return {
            "status": "success",
            "records_processed": results["records_processed"],
            "run_id": batch_run_id
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=List[ETLStats])
def get_stats(db: Session = Depends(get_db)):
    # Get the latest run for each source
    latest_runs = db.query(
        ETLRun.source,
        func.max(ETLRun.started_at).label("max_started_at")
    ).group_by(ETLRun.source).subquery()
    
    stats_query = db.query(ETLRun).join(
        latest_runs,
        (ETLRun.source == latest_runs.c.source) & (ETLRun.started_at == latest_runs.c.max_started_at)
    )
    
    results = []
    for run in stats_query.all():
        results.append(ETLStats(
            source=run.source,
            records_processed=run.records_processed,
            status=run.status,
            duration_ms=run.duration_ms or 0,
            last_run_at=run.ended_at,
            error_message=run.error_message
        ))
    
    return results
