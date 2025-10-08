import cv2
import pickle
import numpy as np
from deepface import DeepFace
from sklearn.metrics.pairwise import cosine_similarity
import os
import csv
from datetime import datetime
from flask import jsonify

# Configuration
EMBEDDINGS_PATH = "embeddings.pkl"
SIMILARITY_THRESHOLD = 0.6
MODEL_NAME = "ArcFace"
ATTENDANCE_THRESHOLD = 0.25  # 25%
MODEL_PATH_YUNET = 'face_detection_yunet_2023mar.onnx'  

# Load face detector
DETECTOR = cv2.FaceDetectorYN.create(MODEL_PATH_YUNET, "", (320, 320))

# ---------------------------
# Utility Functions
# ---------------------------

def load_embeddings():
    """Load stored face embeddings from file."""
    with open(EMBEDDINGS_PATH, "rb") as f:
        return pickle.load(f)

def find_match(face_embedding, embeddings_db):
    """Find the best match for a given face embedding."""
    best_match = "Unknown"
    best_score = 0
    
    for person, person_embeddings in embeddings_db.items():
        for stored_embedding in person_embeddings:
            similarity = cosine_similarity([face_embedding], [stored_embedding])[0][0]
            if similarity > best_score:
                best_score = similarity
                best_match = person
    
    return (best_match, best_score) if best_score >= SIMILARITY_THRESHOLD else ("Unknown", best_score)

def save_attendance(attendance, session_name, session_start, session_end, session_length):
    """Save attendance data to CSV."""
    filename = f"attendance_{session_name}.csv"
    file_exists = os.path.isfile(filename)

    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Name", "Presence (s)", "Session Duration (s)", "Attendance (%)", "Status", "Start", "End"])
        
        for person, presence_time in attendance.items():
            percentage = presence_time / session_length
            status = "Present" if percentage >= ATTENDANCE_THRESHOLD else "Absent"
            writer.writerow([
                person, round(presence_time, 2), session_length,
                f"{percentage*100:.1f}%", status,
                session_start.strftime("%Y-%m-%d %H:%M:%S"),
                session_end.strftime("%Y-%m-%d %H:%M:%S")
            ])

# ---------------------------
# API-Ready Core Logic
# ---------------------------

def recognize_faces_from_image(image_path):
    """
    Detect and recognize faces from an uploaded image.
    Returns JSON with recognized faces and confidence scores.
    """
    embeddings_db = load_embeddings()
    
    frame = cv2.imread(image_path)
    if frame is None:
        return jsonify({"status": "error", "message": "Invalid image file"}), 400

    DETECTOR.setInputSize((frame.shape[1], frame.shape[0]))
    _, faces = DETECTOR.detect(frame)

    results = []
    
    if faces is not None:
        for face in faces:
            x, y, w, h = map(int, face[:4])
            face_img = frame[y:y+h, x:x+w]

            try:
                embedding = DeepFace.represent(face_img, model_name=MODEL_NAME, enforce_detection=False)[0]["embedding"]
                name, confidence = find_match(embedding, embeddings_db)
                results.append({
                    "name": name,
                    "confidence": round(float(confidence), 3),
                    "bounding_box": [x, y, w, h]
                })
            except Exception as e:
                results.append({"error": str(e)})

    return jsonify({
        "status": "success",
        "faces_detected": len(results),
        "results": results
    })

def mark_attendance(session_name, attendance_data, session_duration):
    """
    Mark attendance based on provided presence durations.
    This assumes `attendance_data` = {"Ahmed": 35.5, "Usama": 10.3, ...}
    """
    session_start = datetime.now()
    session_end = datetime.now()

    save_attendance(attendance_data, session_name, session_start, session_end, session_duration)

    return jsonify({
        "status": "attendance_saved",
        "session": session_name,
        "duration": session_duration,
        "total_records": len(attendance_data)
    })
