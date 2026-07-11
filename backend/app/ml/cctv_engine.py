import cv2
import random
import time
import os

try:
    from ultralytics import YOLO
    model = YOLO("yolov8n.pt") 
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("Warning: Ultralytics not installed. Falling back to mocked engine.")

def analyze_frame_yolo(frame_path=None):
    """
    Simulates a CCTV pipeline. If an image path is provided and YOLO is available, 
    it runs inference. Otherwise, it generates realistic mock data.
    """
    if not YOLO_AVAILABLE or frame_path is None or not os.path.exists(frame_path):
        return _generate_mock_detections()
        
    try:
        results = model(frame_path, verbose=False)[0]
        boxes = []
        for box in results.boxes:
            # Class 0 is 'person' in COCO dataset
            if int(box.cls[0]) == 0:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                # Mock a rule: person detected on right side of screen is "unauthorized"
                label = "person (unauthorized)" if x1 > 300 else "person"
                
                boxes.append({
                    "label": label,
                    "confidence": round(conf, 2),
                    "x": int(x1),
                    "y": int(y1),
                    "w": int(x2 - x1),
                    "h": int(y2 - y1)
                })
        
        has_anomaly = any("unauthorized" in b["label"] for b in boxes)
        status = "ALERT" if has_anomaly else "NORMAL"
        score = random.uniform(80.0, 99.9) if has_anomaly else random.uniform(5.0, 25.0)
        
        return {
            "timestamp": time.time(),
            "anomaly_score": round(score, 2),
            "status": status,
            "detections": boxes
        }
    except Exception as e:
        print(f"YOLO Inference Error: {e}")
        return _generate_mock_detections()

def _generate_mock_detections():
    anomaly = random.random() > 0.90 
    if anomaly:
        score = random.uniform(80.0, 99.9)
        boxes = [{"label": "person (unauthorized)", "confidence": round(random.uniform(0.8, 0.99), 2), "x": 120, "y": 45, "w": 100, "h": 200}]
        status = "ALERT"
    else:
        score = random.uniform(5.0, 25.0)
        num_people = random.randint(0, 3)
        boxes = []
        for i in range(num_people):
            boxes.append({"label": "person", "confidence": round(random.uniform(0.6, 0.9), 2), "x": random.randint(10, 400), "y": random.randint(10, 300), "w": 80, "h": 150})
        status = "NORMAL"

    return {
        "timestamp": time.time(),
        "anomaly_score": round(score, 2),
        "status": status,
        "detections": boxes
    }
