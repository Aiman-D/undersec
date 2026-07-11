from fastapi import APIRouter
import psutil
import time

router = APIRouter()

@router.get("/metrics")
def get_system_metrics():
    # Allow 100ms for psutil to gather CPU stats
    cpu = psutil.cpu_percent(interval=0.1)
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
