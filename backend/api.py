# api.py (Corrected and Complete)

import base64
import cv2
import numpy as np
import pickle
from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import dlib

# --- 1. INITIALIZATION ---

app = Flask(__name__)
CORS(app)

try:
    cred = credentials.Certificate("serviceAccountKey.json")
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Firebase Admin SDK initialized successfully.")
except Exception as e:
    print(f"Error initializing Firebase Admin SDK: {e}")
    exit()

try:
    print("Manually loading models...")
    MODELS_PATH = "D:/PROGRAMMING/Class Sphere/back-end/attendance-api/venv/Lib/site-packages/face_recognition_models/models"
    
    shape_predictor_path = f"{MODELS_PATH}/shape_predictor_68_face_landmarks.dat"
    face_rec_model_path = f"{MODELS_PATH}/dlib_face_recognition_resnet_model_v1.dat"
    
    detector = dlib.get_frontal_face_detector()
    sp = dlib.shape_predictor(shape_predictor_path)
    facerec = dlib.face_recognition_model_v1(face_rec_model_path)
    print("Models loaded manually.")
except Exception as e:
    print(f"CRITICAL ERROR: Could not load dlib models. Check MODELS_PATH. Error: {e}")
    exit()

try:
    print("Loading face encodings...")
    with open("embeddings.pkl", "rb") as f:
        all_data_from_file = pickle.load(f)
    known_face_encodings, known_face_uids = all_data_from_file
    print(f"Encodings for {len(known_face_uids)} students loaded successfully.")
except Exception as e:
    print(f"CRITICAL ERROR: Could not load embeddings file. Error: {e}")
    exit()

recognized_student_uids = set()


# --- 2. API ENDPOINTS ---

@app.route('/start', methods=['POST'])
def start_session():
    recognized_student_uids.clear()
    print("Attendance session started.")
    return jsonify({"message": "Session started successfully."})


@app.route('/recognize', methods=['POST'])
def recognize_frame():
    try:
        data = request.get_json()
        # This line has been corrected
        image_data = base64.b64decode(data['image'].split(',')[1])
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        detections = detector(rgb_frame, 1)

        for det in detections:
            shape = sp(rgb_frame, det)
            face_encoding = np.array(facerec.compute_face_descriptor(rgb_frame, shape))
            
            distances = np.linalg.norm(known_face_encodings - face_encoding, axis=1)
            best_match_index = np.argmin(distances)
            
            if distances[best_match_index] < 0.6:
                uid = known_face_uids[best_match_index]
                recognized_student_uids.add(uid)

        print("Processed frame. Recognized UIDs so far:", recognized_student_uids)
        return jsonify({
            "message": "Frame processed.",
            "recognized_uids": list(recognized_student_uids)
        })
    except Exception as e:
        print(f"Error processing frame: {e}")
        return jsonify({"error": "Failed to process frame"}), 500


@app.route('/stop', methods=['POST'])
def stop_session():
    try:
        data = request.get_json()
        class_id = data.get('classId')
        
        if not class_id:
            return jsonify({"error": "classId is required."}), 400

        print(f"Stopping session for class {class_id}. Saving records...")
        today_str = datetime.now().strftime("%Y-%m-%d")
        attendance_ref = db.collection('attendance')
        for uid in recognized_student_uids:
            record_id = f"{class_id}_{uid}_{today_str}"
            attendance_ref.document(record_id).set({
                'classId': class_id, 'studentId': uid, 'date': today_str,
                'status': 'present', 'timestamp': firestore.SERVER_TIMESTAMP
            }, merge=True)
        
        final_list = list(recognized_student_uids)
        recognized_student_uids.clear()
        
        return jsonify({ "message": "Session stopped and attendance recorded.", "present_students_uids": final_list })
    except Exception as e:
        print(f"Error stopping session: {e}")
        return jsonify({"error": "Failed to stop session"}), 500
    
# api.py

# ... (keep all your existing imports)
import subprocess # Add this import
import sys # Add this import

# ... (keep the rest of your initialization code: Flask, Firebase, Model Loading, etc.)
# ...

# --- THIS IS THE NEW ENDPOINT ---
@app.route('/update-embeddings', methods=['POST'])
def update_embeddings():
    """
    Runs the EncodeGenerator.py script to re-create the embeddings.pkl file.
    """
    try:
        print("Starting embeddings generation process...")
        # This command runs your other python script
        subprocess.run([sys.executable, 'EncodeGenerator.py'], check=True)
        print("Embeddings generation finished successfully.")
        return jsonify({
            "message": "Model update complete. Please restart this server to apply the changes."
        })
    except Exception as e:
        print(f"Error during embeddings generation: {e}")
        return jsonify({"error": "Failed to update the model."}), 500
# --------------------------------

# ... (keep your /start, /recognize, and /stop routes)
# ...

if __name__ == '__main__':
    app.run(debug=True, port=5001)

