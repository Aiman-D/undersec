from fastapi import APIRouter, Response
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel
from typing import Optional
from app.ml.cctv_engine import (
    analyze_cctv_frame,
    get_annotated_jpeg_frame,
    trigger_cctv_intrusion,
    clear_cctv_intrusion,
    SHOWROOM_ZONES
)

router = APIRouter()

class IntrusionTriggerRequest(BaseModel):
    zone_id: Optional[str] = "ZONE-01-CONCEPT"
    duration_seconds: Optional[float] = 10.0

@router.get("/feed")
async def get_cctv_feed():
    """Returns real-time YOLOv8 CCTV detections and zone intrusion analysis."""
    result = await run_in_threadpool(analyze_cctv_frame, None)
    return result

@router.get("/frame")
async def get_cctv_frame():
    """Returns the current annotated CCTV frame as a JPEG image."""
    jpeg_bytes = await run_in_threadpool(get_annotated_jpeg_frame)
    return Response(
        content=jpeg_bytes,
        media_type="image/jpeg",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )

@router.get("/zones")
async def get_zones():
    """Returns the defined showroom security zones."""
    return {"zones": SHOWROOM_ZONES}

@router.post("/trigger")
async def trigger_intrusion(req: IntrusionTriggerRequest):
    """Triggers an intrusion event in a specified security zone for live demo testing."""
    result = trigger_cctv_intrusion(req.zone_id, req.duration_seconds)
    return result

@router.post("/clear")
async def clear_intrusion():
    """Clears any active simulated zone intrusion."""
    return clear_cctv_intrusion()
