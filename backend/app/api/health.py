from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from typing import Optional
import psutil
import time

from app.ml.showroom_telemetry import (
    get_showroom_fleet_telemetry,
    get_display_detail,
    inject_display_fault,
    clear_display_fault,
    clear_all_display_faults
)

router = APIRouter()

class ShowroomFaultRequest(BaseModel):
    display_id: str
    fault_type: str # 'gpu_thermal', 'touch_lag', 'chassis_tamper', 'frame_drop', 'signal_loss'
    duration_seconds: Optional[float] = 30.0

@router.get("/showroom/fleet")
async def get_showroom_fleet():
    """Returns real-time Panasonic showroom vehicle-configurator fleet health telemetry."""
    return await run_in_threadpool(get_showroom_fleet_telemetry)

@router.get("/showroom/display/{display_id}")
async def get_display(display_id: str):
    """Returns diagnostics and telemetry history for a specific Panasonic vehicle configurator display."""
    return await run_in_threadpool(get_display_detail, display_id)

@router.post("/showroom/fault")
async def inject_fault(req: ShowroomFaultRequest):
    """Injects a diagnostic anomaly into a vehicle configurator display for live testing."""
    return await run_in_threadpool(
        inject_display_fault,
        req.display_id,
        req.fault_type,
        req.duration_seconds or 30.0
    )

@router.post("/showroom/clear/{display_id}")
async def clear_fault(display_id: str):
    """Clears active fault for a display."""
    return await run_in_threadpool(clear_display_fault, display_id)

@router.post("/showroom/clear-all")
async def clear_all_faults():
    """Clears all active showroom faults."""
    return await run_in_threadpool(clear_all_display_faults)

@router.get("/metrics")
def get_system_metrics():
    """Host system compute resource metrics."""
    cpu = psutil.cpu_percent(interval=0.05)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    net = psutil.net_io_counters()

    anomaly_score = max(0.0, (cpu - 50) * 1.5) if cpu > 50 else (cpu * 0.5)
    
    return {
        "cpu_usage": cpu,
        "memory_usage": memory.percent,
        "disk_usage": disk.percent,
        "bytes_sent": net.bytes_sent,
        "bytes_recv": net.bytes_recv,
        "anomaly_score": round(anomaly_score, 2),
        "status": "WARNING" if cpu > 85 or memory.percent > 90 else "HEALTHY",
        "timestamp": time.time()
    }
