from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool
from app.ml.cctv_engine import analyze_frame_yolo

router = APIRouter()

@router.get("/feed")
async def get_cctv_feed():
    # In a real app, this would pass the current frame from a live RTSP stream buffer
    result = await run_in_threadpool(analyze_frame_yolo, None)
    return result
