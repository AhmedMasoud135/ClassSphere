# EncodeGenerator.py (Final Workaround Version)

import cv2
import pickle
import os
import firebase_admin
from firebase_admin import credentials, firestore
import dlib
import numpy as np

# --- 1. INITIALIZATION ---

# Initialize Firebase Admin
cred = credentials.Certificate("serviceAccountKey.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()
print("Connected to Firebase.")

# --- MANUAL MODEL LOADING (THE FIX) ---
try:
    print("Manually loading models...")
    # IMPORTANT: VERIFY THIS PATH IS CORRECT FOR YOUR SYSTEM
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
# ------------------------------------

# --- 2. SCRIPT LOGIC ---

folderPath = 'Images'
pathList = os.listdir(folderPath)
print("Processing student images...")

encodeListKnown = []
studentUIDs = []

def get_uid_for_name(name):
    """Queries the 'users' collection to find the UID for a given full name."""
    users_ref = db.collection('users')
    query = users_ref.where('fullName', '==', name).limit(1)
    results = query.stream()
    for doc in results:
        return doc.id
    return None

for path in pathList:
    studentName = os.path.splitext(path)[0]
    studentUID = get_uid_for_name(studentName)
    
    if studentUID:
        print(f"Processing image for {studentName}...")
        img = cv2.imread(os.path.join(folderPath, path))
        if img is None:
            print(f"Warning: Could not read image {path}. Skipping.")
            continue
            
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # --- Manual Face Encoding Logic ---
        # 1. Detect face(s)
        detections = detector(rgb_img, 1)
        
        # 2. If a face is found, get its encoding
        if len(detections) > 0:
            # Assuming one face per image for enrollment
            shape = sp(rgb_img, detections[0])
            encode = np.array(facerec.compute_face_descriptor(rgb_img, shape))
            
            encodeListKnown.append(encode)
            studentUIDs.append(studentUID)
        else:
            print(f"Warning: No face was found in the image for {studentName}. Skipping.")
        # ------------------------------------
    else:
        print(f"Error: Could not find a user with the name '{studentName}' in the database.")

encodeListKnownWithUIDs = [encodeListKnown, studentUIDs]

print("Encoding Complete.")

with open("embeddings.pkl", 'wb') as file:
    pickle.dump(encodeListKnownWithUIDs, file)

print("File 'embeddings.pkl' saved successfully.")