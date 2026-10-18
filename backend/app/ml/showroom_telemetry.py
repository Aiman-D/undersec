import time
import random
import numpy as np

SHOWROOM_DISPLAYS = [
    {
        "id": "PAN-CFG-01",
        "name": "Main Pavilion - 8K Ultra-Wall Configurator",
        "model": "Panasonic TH-98CQE2U Pro 4K/8K Display",
        "location": "Zone 1 - Main Showroom Pavilion",
        "vehicle_model": "Panasonic-Lexus Concept Sport EV",
        "resolution": "7680x4320 @ 60Hz",
        "gpu_model": "NVIDIA RTX 4090 Workstation",
        "baseline_fps": 60.0,
        "baseline_gpu_temp": 64.0,
        "baseline_panel_temp": 42.0,
        "baseline_touch_latency": 11.0,
        "backlight_hours": 3420,
    },
    {
        "id": "PAN-CFG-02",
        "name": "EV Studio - 4K Interactive Touch Pod",
        "model": "Panasonic TH-65SQE2W High-Brightness Touch",
        "location": "Zone 3 - EV Studio West",
        "vehicle_model": "Lexus RZ 450e All-Electric SUV",
        "resolution": "3840x2160 @ 60Hz",
        "gpu_model": "NVIDIA RTX 4080 Super",
        "baseline_fps": 60.0,
        "baseline_gpu_temp": 59.0,
        "baseline_panel_temp": 39.5,
        "baseline_touch_latency": 13.5,
        "backlight_hours": 1890,
    },
    {
        "id": "PAN-CFG-03",
        "name": "VIP Bespoke Lounge - Dual Curved OLED Kiosk",
        "model": "Panasonic TX-65MZ2000 Pro Master OLED",
        "location": "VIP Executive Suite",
        "vehicle_model": "Toyota Crown Signia Bespoke Edition",
        "resolution": "3840x2160 @ 120Hz",
        "gpu_model": "Dual NVIDIA RTX 4090 NVLink",
        "baseline_fps": 120.0,
        "baseline_gpu_temp": 67.5,
        "baseline_panel_temp": 44.0,
        "baseline_touch_latency": 8.2,
        "backlight_hours": 940,
    },
    {
        "id": "PAN-CFG-04",
        "name": "Materials & Trim Table - Multi-touch Surface",
        "model": "Panasonic Touch-Station Pro Interactive Surface",
        "location": "Design & Material Studio",
        "vehicle_model": "Interior Cockpit & Leather Finishes",
        "resolution": "3840x2160 @ 60Hz",
        "gpu_model": "NVIDIA RTX 3080 Ti",
        "baseline_fps": 60.0,
        "baseline_gpu_temp": 56.0,
        "baseline_panel_temp": 38.0,
        "baseline_touch_latency": 14.0,
        "backlight_hours": 4210,
    },
    {
        "id": "PAN-CFG-05",
        "name": "Entrance Foyer - Wayfinding & Portfolio Station",
        "model": "Panasonic TH-55SQ2H Commercial Signage",
        "location": "Showroom Welcome Lobby",
        "vehicle_model": "Full Panasonic Automotive Showroom Lineup",
        "resolution": "3840x2160 @ 60Hz",
        "gpu_model": "Intel Core i9 / Iris Xe Embedded Pro",
        "baseline_fps": 60.0,
        "baseline_gpu_temp": 51.0,
        "baseline_panel_temp": 36.5,
        "baseline_touch_latency": 17.5,
        "backlight_hours": 5120,
    }
]

# In-memory fault injections and historical buffers
_active_faults = {}
_history_buffers = {d["id"]: [] for d in SHOWROOM_DISPLAYS}
MAX_HISTORY_POINTS = 30

def inject_display_fault(display_id: str, fault_type: str, duration_seconds: float = 30.0):
    """
    Injects a real-time hardware telemetry fault into a vehicle configurator display.
    fault_type: 'gpu_thermal', 'touch_lag', 'chassis_tamper', 'frame_drop', 'signal_loss'
    """
    _active_faults[display_id] = {
        "fault_type": fault_type,
        "expires_at": time.time() + duration_seconds,
        "started_at": time.time()
    }
    return {
        "status": "fault_injected",
        "display_id": display_id,
        "fault_type": fault_type,
        "duration_seconds": duration_seconds
    }

def clear_display_fault(display_id: str):
    if display_id in _active_faults:
        del _active_faults[display_id]
    return {"status": "fault_cleared", "display_id": display_id}

def clear_all_display_faults():
    _active_faults.clear()
    return {"status": "all_faults_cleared"}

def sample_display_telemetry(display_config: dict) -> dict:
    disp_id = display_config["id"]
    now = time.time()
    
    # Check if a fault is currently active on this display
    active_fault = _active_faults.get(disp_id)
    if active_fault and now > active_fault["expires_at"]:
        del _active_faults[disp_id]
        active_fault = None
        
    fault_type = active_fault["fault_type"] if active_fault else None

    # Base telemetry values with small natural physical sensor jitter
    target_fps = display_config["baseline_fps"]
    fps_jitter = random.uniform(-1.2, 0.8)
    fps = round(max(0.0, target_fps + fps_jitter), 1)
    
    gpu_temp = round(display_config["baseline_gpu_temp"] + random.uniform(-1.0, 1.5), 1)
    panel_temp = round(display_config["baseline_panel_temp"] + random.uniform(-0.5, 0.8), 1)
    touch_latency = round(display_config["baseline_touch_latency"] + random.uniform(-1.0, 1.5), 1)
    
    frame_time = round(1000.0 / max(1.0, fps), 2)
    vram_pct = round(62.0 + random.uniform(-3.0, 4.0), 1)
    ambient_lux = random.randint(480, 560)
    asset_sync_latency = round(4.2 + random.uniform(-0.6, 1.2), 1)
    touch_points = random.choice([0, 0, 1, 2, 3])
    chassis_tamper = "CLOSED"
    signal_lock = True
    unauthorized_usb = False
    
    # Apply Fault Injections if active
    fault_reasons = []
    if fault_type == "gpu_thermal":
        gpu_temp = round(89.5 + random.uniform(0.5, 4.5), 1)
        fps = round(14.2 + random.uniform(-2.0, 3.0), 1)
        frame_time = round(1000.0 / fps, 2)
        vram_pct = 98.4
        fault_reasons.append("CRITICAL: GPU thermal throttling detected (core temp exceeded 88°C)")
    elif fault_type == "touch_lag":
        touch_latency = round(84.0 + random.uniform(5.0, 22.0), 1)
        fault_reasons.append("WARNING: Capacitive touch digitizer input lag anomaly (>75ms)")
    elif fault_type == "chassis_tamper":
        chassis_tamper = "TRIPPED"
        unauthorized_usb = True
        fault_reasons.append("SECURITY CRITICAL: Enclosure chassis tamper switch tripped & unauthorized USB port activity")
    elif fault_type == "frame_drop":
        fps = round(11.0 + random.uniform(-3.0, 2.0), 1)
        frame_time = round(1000.0 / fps, 2)
        fault_reasons.append("WARNING: 3D Configurator rendering pipeline severe frame drop (<15 FPS)")
    elif fault_type == "signal_loss":
        signal_lock = False
        fps = 0.0
        frame_time = 0.0
        fault_reasons.append("CRITICAL: Panasonic display HDMI/DP 2.1 video link lock lost")

    # Determine Health Status and Anomaly Score
    anomaly_score = 0.0
    status = "HEALTHY"
    
    if chassis_tamper == "TRIPPED" or not signal_lock or gpu_temp > 88.0:
        status = "CRITICAL"
        anomaly_score = round(random.uniform(88.0, 99.5), 2)
    elif gpu_temp > 78.0 or touch_latency > 35.0 or fps < (target_fps * 0.6):
        status = "WARNING"
        anomaly_score = round(random.uniform(50.0, 75.0), 2)
    else:
        status = "HEALTHY"
        anomaly_score = round(random.uniform(2.0, 14.0), 2)

    telemetry_record = {
        "id": disp_id,
        "name": display_config["name"],
        "model": display_config["model"],
        "location": display_config["location"],
        "vehicle_model": display_config["vehicle_model"],
        "resolution": display_config["resolution"],
        "gpu_model": display_config["gpu_model"],
        "status": status,
        "anomaly_score": anomaly_score,
        "timestamp": now,
        "diagnostics": {
            "fps": fps,
            "target_fps": target_fps,
            "frame_time_ms": frame_time,
            "gpu_temp_c": gpu_temp,
            "panel_temp_c": panel_temp,
            "vram_usage_pct": vram_pct,
            "touch_latency_ms": touch_latency,
            "touch_points_active": touch_points,
            "touch_status": "CALIBRATING" if touch_latency > 50 else "OPERATIONAL",
            "ambient_lux": ambient_lux,
            "signal_lock": signal_lock,
            "chassis_tamper": chassis_tamper,
            "unauthorized_usb": unauthorized_usb,
            "asset_sync_latency_ms": asset_sync_latency,
            "backlight_hours": display_config["backlight_hours"],
            "power_rail_voltage": 12.02,
        },
        "fault_reasons": fault_reasons,
        "active_fault": fault_type
    }
    
    # Store in historical buffer for sparklines
    buf = _history_buffers[disp_id]
    buf.append({
        "time": time.strftime("%H:%M:%S", time.localtime(now)),
        "fps": fps,
        "gpu_temp": gpu_temp,
        "panel_temp": panel_temp,
        "touch_latency": touch_latency,
        "status": status
    })
    if len(buf) > MAX_HISTORY_POINTS:
        buf.pop(0)

    return telemetry_record

def get_showroom_fleet_telemetry() -> dict:
    """Returns real-time telemetry for all Panasonic showroom configurator displays."""
    devices = [sample_display_telemetry(cfg) for cfg in SHOWROOM_DISPLAYS]
    
    total = len(devices)
    healthy = sum(1 for d in devices if d["status"] == "HEALTHY")
    warning = sum(1 for d in devices if d["status"] == "WARNING")
    critical = sum(1 for d in devices if d["status"] == "CRITICAL")
    
    avg_fps = round(np.mean([d["diagnostics"]["fps"] for d in devices]), 1)
    avg_gpu_temp = round(np.mean([d["diagnostics"]["gpu_temp_c"] for d in devices]), 1)
    avg_touch_latency = round(np.mean([d["diagnostics"]["touch_latency_ms"] for d in devices]), 1)
    
    fleet_health_score = round(100.0 - (warning * 15.0 + critical * 35.0), 1)
    fleet_health_score = max(0.0, min(100.0, fleet_health_score))
    
    return {
        "timestamp": time.time(),
        "total_displays": total,
        "fleet_health_score": fleet_health_score,
        "counts": {
            "healthy": healthy,
            "warning": warning,
            "critical": critical
        },
        "averages": {
            "avg_fps": avg_fps,
            "avg_gpu_temp_c": avg_gpu_temp,
            "avg_touch_latency_ms": avg_touch_latency
        },
        "displays": devices
    }

def get_display_detail(display_id: str) -> dict:
    cfg = next((d for d in SHOWROOM_DISPLAYS if d["id"] == display_id), None)
    if not cfg:
        return {"error": f"Display {display_id} not found"}
        
    latest = sample_display_telemetry(cfg)
    history = _history_buffers.get(display_id, [])
    
    return {
        "telemetry": latest,
        "history": history
    }
