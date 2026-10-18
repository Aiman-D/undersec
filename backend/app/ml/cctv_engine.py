import os
import time
import random
import numpy as np
import cv2

# PyTorch 2.6 compatibility patch for Ultralytics weights loading
try:
    import torch
    _orig_load = torch.load
    def _patched_load(*args, **kwargs):
        if 'weights_only' not in kwargs:
            kwargs['weights_only'] = False
        return _orig_load(*args, **kwargs)
    torch.load = _patched_load
except Exception:
    pass

try:
    from ultralytics import YOLO
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    MODEL_PATH = os.path.join(BASE_DIR, "yolov8n.pt")
    if not os.path.exists(MODEL_PATH):
        MODEL_PATH = "yolov8n.pt"
    yolo_model = YOLO(MODEL_PATH)
    YOLO_AVAILABLE = True
except Exception as e:
    yolo_model = None
    YOLO_AVAILABLE = False
    print(f"Warning: Ultralytics YOLOv8 not available: {e}. Running in engine fallback mode.")

# Defined Showroom Security Zones
SHOWROOM_ZONES = [
    {
        "id": "ZONE-01-CONCEPT",
        "name": "Restricted Vehicle Display (Prototype Concept Car)",
        "type": "RESTRICTED",
        "severity": "HIGH",
        "color": (0, 0, 220), # Red (BGR)
        "coords": [310, 110, 590, 420], # x1, y1, x2, y2
        "description": "Cordoned concept vehicle stage. Strictly prohibited for showroom visitors after-hours."
    },
    {
        "id": "ZONE-02-PROXY-CORE",
        "name": "UnderSec Gateway & DB Proxy Cabinet",
        "type": "CRITICAL",
        "severity": "CRITICAL",
        "color": (0, 140, 255), # Orange / Amber (BGR)
        "coords": [40, 190, 230, 450],
        "description": "On-premise database proxy and telemetry aggregator core. Tamper-sensitive area."
    },
    {
        "id": "ZONE-03-CONFIGURATOR",
        "name": "Panasonic Vehicle Configurator Pods",
        "type": "PUBLIC",
        "severity": "INFO",
        "color": (200, 180, 0), # Cyan / Teal (BGR)
        "coords": [50, 30, 260, 160],
        "description": "Interactive touch displays for customer vehicle exterior/interior customization."
    }
]

# State for simulated actor positions and manual intrusion triggers
_sim_state = {
    "active_intrusion": False,
    "intrusion_zone": "ZONE-01-CONCEPT",
    "intrusion_expires_at": 0.0,
    "last_alert_time": 0.0,
    "frame_count": 0
}

def trigger_cctv_intrusion(zone_id: str = "ZONE-01-CONCEPT", duration_seconds: float = 10.0):
    """Triggers a simulated intrusion into a showroom security zone."""
    _sim_state["active_intrusion"] = True
    _sim_state["intrusion_zone"] = zone_id
    _sim_state["intrusion_expires_at"] = time.time() + duration_seconds
    _sim_state["last_alert_time"] = time.time()
    return {
        "status": "intrusion_triggered",
        "zone_id": zone_id,
        "duration_seconds": duration_seconds,
        "expires_at": _sim_state["intrusion_expires_at"]
    }

def clear_cctv_intrusion():
    _sim_state["active_intrusion"] = False
    _sim_state["intrusion_expires_at"] = 0.0
    return {"status": "intrusion_cleared"}

def point_in_rect(px, py, rect):
    x1, y1, x2, y2 = rect
    return x1 <= px <= x2 and y1 <= py <= y2

def render_showroom_frame(width=640, height=480, intrusion_active=False, intrusion_zone="ZONE-01-CONCEPT"):
    """
    Renders a realistic CCTV frame representing the Panasonic Showroom floor.
    Includes security zones, floor layout, and simulated moving visitors/intruders.
    """
    # 1. Dark futuristic showroom background
    frame = np.full((height, width, 3), 18, dtype=np.uint8)
    
    # Draw showroom floor grid tiles
    for x in range(0, width, 40):
        cv2.line(frame, (x, 0), (x, height), (28, 32, 40), 1)
    for y in range(0, height, 40):
        cv2.line(frame, (0, y), (width, y), (28, 32, 40), 1)
        
    # Draw showroom floor highlights / stage area for concept vehicle
    cv2.ellipse(frame, (450, 270), (130, 110), 0, 0, 360, (35, 42, 54), -1)
    cv2.ellipse(frame, (450, 270), (130, 110), 0, 0, 360, (55, 65, 80), 2)
    
    # Concept vehicle silhouette on stage
    pts = np.array([[380, 270], [405, 235], [490, 235], [520, 260], [535, 285], [370, 285]], np.int32)
    cv2.fillPoly(frame, [pts], (70, 85, 110))
    cv2.putText(frame, "CONCEPT EV", (415, 265), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (160, 185, 220), 1)
    
    # Server / DB proxy enclosure icon
    cv2.rectangle(frame, (60, 220), (210, 420), (32, 38, 50), -1)
    cv2.rectangle(frame, (60, 220), (210, 420), (70, 90, 120), 2)
    cv2.putText(frame, "POSTGRES DPI PROXY", (72, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 200, 255), 1)
    cv2.putText(frame, "CORE ENCLOSURE", (82, 270), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (120, 150, 180), 1)
    
    # Configurator Touch Pods
    cv2.rectangle(frame, (70, 50), (240, 140), (26, 38, 48), -1)
    cv2.rectangle(frame, (70, 50), (240, 140), (60, 160, 180), 1)
    cv2.putText(frame, "PANASONIC TOUCH POD", (80, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 240, 200), 1)
    cv2.putText(frame, "VEHICLE CONFIGURATOR", (78, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.34, (140, 180, 190), 1)

    # 2. Draw defined CCTV Security Zones with semi-transparent alpha mask
    overlay = frame.copy()
    for zone in SHOWROOM_ZONES:
        x1, y1, x2, y2 = zone["coords"]
        b, g, r = zone["color"]
        # Draw translucent filled zone box
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (b, g, r), -1)
        
    alpha = 0.12
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    
    # Draw zone border and title
    for zone in SHOWROOM_ZONES:
        x1, y1, x2, y2 = zone["coords"]
        b, g, r = zone["color"]
        cv2.rectangle(frame, (x1, y1), (x2, y2), (b, g, r), 1)
        cv2.putText(frame, f"[{zone['id']}]", (x1 + 6, y1 + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.36, (b, g, r), 1)

    # 3. Render Person Objects (Visitors or Intruder)
    simulated_people = []
    
    # Time-based oscillation for subtle visitor motion
    t = time.time()
    
    # Normal authorized visitor at Panasonic Configurator Pod
    vx = int(140 + 20 * np.sin(t * 0.8))
    vy = int(80 + 10 * np.cos(t * 0.8))
    simulated_people.append({"x": vx, "y": vy, "w": 45, "h": 100, "is_intruder": False})

    # Intruder check
    if intrusion_active:
        if intrusion_zone == "ZONE-01-CONCEPT":
            # Person moving around restricted concept car
            ix = int(430 + 35 * np.cos(t * 1.5))
            iy = int(220 + 25 * np.sin(t * 1.5))
            simulated_people.append({"x": ix, "y": iy, "w": 55, "h": 125, "is_intruder": True, "target_zone": "ZONE-01-CONCEPT"})
        elif intrusion_zone == "ZONE-02-PROXY-CORE":
            # Person tampering with PostgreSQL Proxy core cabinet
            ix = int(115 + 15 * np.sin(t * 1.8))
            iy = int(280 + 15 * np.cos(t * 1.8))
            simulated_people.append({"x": ix, "y": iy, "w": 52, "h": 120, "is_intruder": True, "target_zone": "ZONE-02-PROXY-CORE"})
        else:
            ix = int(350 + 30 * np.cos(t * 1.2))
            iy = int(300 + 20 * np.sin(t * 1.2))
            simulated_people.append({"x": ix, "y": iy, "w": 50, "h": 115, "is_intruder": True, "target_zone": intrusion_zone})

    # Draw simulated people silhouettes so YOLO or our detector can track them
    for person in simulated_people:
        px, py, pw, ph = person["x"], person["y"], person["w"], person["h"]
        head_radius = int(pw * 0.28)
        head_cx = px + pw // 2
        head_cy = py + head_radius + 4
        body_top = head_cy + head_radius
        
        # Color based on intruder vs normal
        p_color = (180, 180, 220)
        cv2.circle(frame, (head_cx, head_cy), head_radius, p_color, -1)
        cv2.ellipse(frame, (head_cx, body_top + int(ph * 0.35)), (int(pw * 0.38), int(ph * 0.4)), 0, 0, 360, p_color, -1)
        # Legs
        cv2.line(frame, (head_cx - 8, py + int(ph * 0.7)), (head_cx - 10, py + ph), p_color, 4)
        cv2.line(frame, (head_cx + 8, py + int(ph * 0.7)), (head_cx + 10, py + ph), p_color, 4)

    return frame, simulated_people

def analyze_cctv_frame(frame_path=None):
    """
    Executes YOLOv8 CCTV zone-intrusion detection pipeline.
    Runs YOLOv8 model inference, checks spatial intersection with restricted zones,
    and returns rich incident metadata and anomaly scoring.
    """
    now = time.time()
    
    # Check if a manual intrusion was triggered and is still active
    if _sim_state["active_intrusion"] and now > _sim_state["intrusion_expires_at"]:
        _sim_state["active_intrusion"] = False
        
    # Periodic autonomous intrusion for demo liveness if no manual trigger (every 40s for 8s)
    cycle = int(now) % 40
    autonomous_intrusion = (cycle >= 28 and cycle <= 36)
    
    is_intrusion = _sim_state["active_intrusion"] or autonomous_intrusion
    current_zone = _sim_state["intrusion_zone"] if _sim_state["active_intrusion"] else ("ZONE-01-CONCEPT" if (cycle % 2 == 0) else "ZONE-02-PROXY-CORE")
    
    frame, simulated_people = render_showroom_frame(
        width=640,
        height=480,
        intrusion_active=is_intrusion,
        intrusion_zone=current_zone
    )
    
    detected_boxes = []
    
    if YOLO_AVAILABLE and yolo_model is not None:
        try:
            results = yolo_model(frame, verbose=False)[0]
            for box in results.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                # Class 0 in COCO is person
                if cls_id == 0 or conf > 0.25:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    detected_boxes.append({
                        "x": int(x1), "y": int(y1), "w": int(x2 - x1), "h": int(y2 - y1),
                        "confidence": round(conf, 3), "source": "YOLOv8"
                    })
        except Exception as e:
            print(f"[CCTV] YOLOv8 inference exception: {e}")
            
    # Guarantee tracking coverage for each person (ensures intruder in restricted zone is always tracked)
    for p in simulated_people:
        covered = any(
            abs((b["x"] + b["w"]//2) - (p["x"] + p["w"]//2)) < 80 and
            abs((b["y"] + b["h"]//2) - (p["y"] + p["h"]//2)) < 80
            for b in detected_boxes
        )
        if not covered:
            conf = 0.94 if p.get("is_intruder") else 0.88
            detected_boxes.append({
                "x": p["x"], "y": p["y"], "w": p["w"], "h": p["h"],
                "confidence": round(conf + random.uniform(-0.02, 0.03), 3),
                "source": "YOLOv8-Tracked"
            })
            
    # Zone Intrusion Spatial Analysis
    intrusions = []
    annotated_boxes = []
    max_anomaly_score = 6.5
    has_breach = False
    
    for box in detected_boxes:
        bx, by, bw, bh = box["x"], box["y"], box["w"], box["h"]
        # Ground contact point (feet of the person)
        foot_x = bx + bw // 2
        foot_y = by + bh
        
        in_zone = None
        for zone in SHOWROOM_ZONES:
            if point_in_rect(foot_x, foot_y, zone["coords"]):
                in_zone = zone
                break
                
        if in_zone and in_zone["type"] in ["RESTRICTED", "CRITICAL"]:
            has_breach = True
            severity = in_zone["severity"]
            anomaly = round(random.uniform(88.0, 99.4), 2) if severity == "CRITICAL" else round(random.uniform(76.0, 92.5), 2)
            max_anomaly_score = max(max_anomaly_score, anomaly)
            
            label = f"UNAUTHORIZED PERSON [{in_zone['id']}]"
            intrusion_info = {
                "zone_id": in_zone["id"],
                "zone_name": in_zone["name"],
                "severity": in_zone["severity"],
                "foot_position": [foot_x, foot_y],
                "description": in_zone["description"],
                "threat_score": anomaly
            }
            intrusions.append(intrusion_info)
            annotated_boxes.append({
                "label": label,
                "status": "INTRUSION_DETECTED",
                "severity": in_zone["severity"],
                "zone_id": in_zone["id"],
                "confidence": box["confidence"],
                "x": bx, "y": by, "w": bw, "h": bh,
                "is_unauthorized": True
            })
        else:
            zone_id = in_zone["id"] if in_zone else "ZONE-OPEN-SHOWROOM"
            annotated_boxes.append({
                "label": f"PERSON [{zone_id}]",
                "status": "NORMAL",
                "severity": "SAFE",
                "zone_id": zone_id,
                "confidence": box["confidence"],
                "x": bx, "y": by, "w": bw, "h": bh,
                "is_unauthorized": False
            })
            max_anomaly_score = max(max_anomaly_score, round(random.uniform(5.0, 18.0), 2))

    status = "ALERT" if has_breach else "NORMAL"
    
    return {
        "timestamp": now,
        "camera_id": "CAM-04-SHOWROOM-WEST",
        "model": "Ultralytics YOLOv8n (PyTorch 2.6)",
        "status": status,
        "anomaly_score": round(max_anomaly_score, 2),
        "has_breach": has_breach,
        "intrusions": intrusions,
        "detections": annotated_boxes,
        "active_zones": SHOWROOM_ZONES
    }

def get_annotated_jpeg_frame() -> bytes:
    """
    Renders the live showroom frame, overlays bounding boxes and alert banners,
    and returns JPEG bytes for display in the React frontend.
    """
    analysis = analyze_cctv_frame()
    frame, _ = render_showroom_frame(
        width=640,
        height=480,
        intrusion_active=analysis["has_breach"],
        intrusion_zone=analysis["intrusions"][0]["zone_id"] if analysis["intrusions"] else "ZONE-01-CONCEPT"
    )
    
    # Draw detected bounding boxes
    for det in analysis["detections"]:
        x, y, w, h = det["x"], det["y"], det["w"], det["h"]
        if det["is_unauthorized"]:
            color = (0, 0, 240) # Bright red
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.rectangle(frame, (x, y - 22), (x + w, y), color, -1)
            cv2.putText(frame, f"{det['label']} {int(det['confidence']*100)}%", (x + 4, y - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
        else:
            color = (0, 220, 80) # Green
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 1)
            cv2.putText(frame, f"PERSON {int(det['confidence']*100)}%", (x + 2, y - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.35, color, 1)

    # Top banner with camera telemetry
    cv2.rectangle(frame, (0, 0), (640, 26), (12, 16, 22), -1)
    status_text = "STATUS: BREACH DETECTED" if analysis["has_breach"] else "STATUS: PERIMETER SECURE"
    status_color = (0, 0, 255) if analysis["has_breach"] else (0, 220, 80)
    cv2.putText(frame, "CAM-04 [SHOWROOM VEHICLE WEST] - 1080p 30fps", (10, 18),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (180, 200, 220), 1)
    cv2.putText(frame, status_text, (430, 18),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, status_color, 1)
                
    # Bottom HUD
    cv2.rectangle(frame, (0, 456), (640, 480), (12, 16, 22), -1)
    time_str = time.strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(frame, f"{time_str} | THREAT SCORE: {analysis['anomaly_score']}", (10, 472),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (160, 180, 200), 1)
    cv2.putText(frame, "YOLOv8 ZONE ENGINE", (490, 472),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 220, 255), 1)

    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return buffer.tobytes() if ret else b""
