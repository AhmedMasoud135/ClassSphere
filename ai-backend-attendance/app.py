# app_firebase.py
"""
Main Flask application with Firebase integration for Smart Attendance System.
This version replaces global variables with Firebase database storage.
"""

import os
import io
import json
import base64
import tempfile
import traceback
import subprocess
import sys
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

# Import Firebase configuration
from firebase_config import get_firebase_manager, initialize_firebase

import main  
import Run as scheduler_module  
import Student_Manage as student_manage  

# We need to safely import manage_embeddings from EncodeGenerator 
import ast

def safe_load_manage_embeddings(module_path="EncodeGenerator.py"):
    """
    Read the source of module_path, parse it, extract the manage_embeddings
    function object without executing top-level calls (like manage_embeddings()).
    Returns the function object or raises.
    """
    if not os.path.exists(module_path):
        raise FileNotFoundError(f"{module_path} not found")

    source = open(module_path, "r", encoding="utf-8").read()
    parsed = ast.parse(source, filename=module_path)

    # Build a new AST that contains only the function def for manage_embeddings
    new_body = []
    for node in parsed.body:
        # Keep function def named 'manage_embeddings' and necessary imports
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            new_body.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name == "manage_embeddings":
            new_body.append(node)

    new_module = ast.Module(body=new_body, type_ignores=[])
    ast.fix_missing_locations(new_module)

    # Compile and exec in a fresh namespace
    namespace = {}
    compiled = compile(new_module, module_path, "exec")
    exec(compiled, namespace)
    if "manage_embeddings" not in namespace:
        raise RuntimeError("manage_embeddings function not found in module")
    return namespace["manage_embeddings"]

# Try to load manage_embeddings safely
try:
    manage_embeddings = safe_load_manage_embeddings("EncodeGenerator.py")
except Exception as e:
    manage_embeddings = None
    print("⚠️ Warning: could not load manage_embeddings safely:", str(e))
    print(traceback.format_exc())

# Flask app setup
app = Flask(__name__)
CORS(app)

# Initialize Firebase
try:
    firebase_manager = initialize_firebase()
    print("✅ Firebase initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Firebase: {e}")
    firebase_manager = None

# Configuration (paths used across modules)
BASE_DIR = "Smart Attendance System"
STUDENTS_DIR = os.path.join(BASE_DIR, "Images")
EMBEDDINGS_PATH = getattr(main, "EMBEDDINGS_PATH", "embeddings.pkl")
ATTENDANCE_PREFIX = "attendance_"  # main.save_attendance produces attendance_{session}.csv

# Ensure directories exist
os.makedirs(STUDENTS_DIR, exist_ok=True)
os.makedirs(BASE_DIR, exist_ok=True)

# ------------------------------
# Helpers
# ------------------------------
def decode_base64_image(data_b64):
    """Return bytes for base64 image string (may include data:image/... prefix)."""
    if "," in data_b64:
        data_b64 = data_b64.split(",")[1]
    return base64.b64decode(data_b64)

def save_temp_image_bytes(bytes_data, suffix=".jpg"):
    """Save bytes to a temp file path and return the path (caller should remove)."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(bytes_data)
    tmp.flush()
    tmp.close()
    return tmp.name

def parse_recognize_response(flask_response):
    """
    Given a Flask Response returned by main.recognize_faces_from_image (which uses jsonify),
    parse and return the JSON object.
    """
    try:
        data = flask_response.get_data(as_text=True)
        return json.loads(data)
    except Exception:
        return {"status": "error", "message": "Failed to parse recognition response"}

# ------------------------------
# Routes - Health
# ------------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "running",
        "message": "Smart Attendance System API with Firebase",
        "firebase_status": "connected" if firebase_manager else "disconnected",
        "endpoints": {
            "POST /recognize_image": "Upload image (base64 or file) for recognition",
            "POST /add_student": "Add student with list of base64 images",
            "DELETE /remove_student/<name>": "Remove student",
            "POST /update_embeddings": "Rebuild/update embeddings (calls manage_embeddings)",
            "GET /session_status": "Get current session status",
            "GET /list_students": "List registered students",
            "GET /attendance_files": "List attendance CSV files",
            "POST /start_session": "Start attendance session",
            "POST /stop_session": "Stop attendance session and save to Firebase",
            "GET /attendance/<class_id>": "Get attendance records for a class"
        }
    })

# ------------------------------
# New Firebase-based Routes
# ------------------------------

@app.route("/start_session", methods=["POST"])
def start_session():
    """Start a new attendance session."""
    try:
        data = request.get_json()
        class_id = data.get('classId')
        
        if not class_id:
            return jsonify({"error": "classId is required"}), 400
        
        if not firebase_manager:
            return jsonify({"error": "Firebase not initialized"}), 500
        
        # Clear any existing session data for this class then start a new one
        scheduler_module.clear_session_data(class_id)
        start_resp = scheduler_module.start_session(class_id)
        # Return the scheduler's response JSON
        return start_resp
        
    except Exception as e:
        return jsonify({"error": f"Failed to start session: {str(e)}"}), 500

@app.route("/stop_session", methods=["POST"])
def stop_session():
    """Stop the current session and save attendance to Firebase."""
    try:
        data = request.get_json()
        class_id = data.get('classId')
        
        if not class_id:
            return jsonify({"error": "classId is required"}), 400
        
        if not firebase_manager:
            return jsonify({"error": "Firebase not initialized"}), 500
        
        # Stop the session and get summary (includes duration)
        stop_resp = scheduler_module.stop_session(class_id)
        session_data = parse_recognize_response(stop_resp)
        if not session_data or session_data.get("status") == "inactive":
            return jsonify({"error": "No active session found"}), 400
        
        # Save attendance records to Firebase
        attendance_records = session_data.get('attendance_records', {})
        success_count = 0
        
        for student_name, presence_time in attendance_records.items():
            # Calculate attendance percentage
            session_duration = session_data.get('duration_seconds', 60)
            attendance_percentage = (presence_time / session_duration) * 100 if session_duration > 0 else 0
            
            # Save to Firebase
            success = firebase_manager.save_attendance_record(
                class_id=class_id,
                student_id=student_name,
                status="present" if attendance_percentage >= 25 else "absent",
                additional_data={
                    'presence_time': presence_time,
                    'attendance_percentage': attendance_percentage,
                    'session_duration': session_duration
                }
            )
            
            if success:
                success_count += 1
        
        # Save session data
        session_id = f"{class_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        firebase_manager.save_session_data(
            session_id=session_id,
            session_name=session_data.get('session_name', 'Unknown'),
            start_time=datetime.fromisoformat(session_data.get('start_time')) if session_data.get('start_time') else datetime.now(),
            end_time=datetime.fromisoformat(session_data.get('end_time')) if session_data.get('end_time') else datetime.now(),
            duration_minutes=session_data.get('duration_seconds', 60) // 60,
            recognized_students=list(attendance_records.keys())
        )
        
        return jsonify({
            "message": "Session stopped and attendance saved to Firebase",
            "classId": class_id,
            "records_saved": success_count,
            "total_students": len(attendance_records),
            "session_id": session_id
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to stop session: {str(e)}"}), 500

@app.route("/attendance/<class_id>", methods=["GET"])
def get_attendance_for_class(class_id):
    """Get attendance records for a specific class."""
    try:
        if not firebase_manager:
            return jsonify({"error": "Firebase not initialized"}), 500
        
        date = request.args.get('date')  # Optional date parameter
        records = firebase_manager.get_attendance_for_class(class_id, date)
        
        return jsonify({
            "classId": class_id,
            "date": date or datetime.now().strftime("%Y-%m-%d"),
            "records": records,
            "total_records": len(records)
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to get attendance: {str(e)}"}), 500

# ------------------------------
# Route - Recognize image (frame)
# ------------------------------
@app.route("/recognize_image", methods=["POST"])
def recognize_image_route():
    """
    Accept either:
    - JSON with {"image": "data:image/jpeg;base64,...."} OR
    - multipart/form-data with file input named 'image'
    Process using main.recognize_faces_from_image (which expects an image path).
    If a session is active, record recognized names into scheduler attendance.
    """
    try:
        # Get image bytes either from JSON base64 or file upload
        if request.is_json:
            data = request.get_json()
            image_b64 = data.get("image")
            if not image_b64:
                return jsonify({"status": "error", "message": "No image field in JSON"}), 400
            img_bytes = decode_base64_image(image_b64)
            tmp_path = save_temp_image_bytes(img_bytes, suffix=".jpg")
        else:
            # multipart/form-data
            if "image" not in request.files:
                return jsonify({"status": "error", "message": "No image file provided"}), 400
            file = request.files["image"]
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            file.save(tmp.name)
            tmp_path = tmp.name

        # Call the recognition function from main.py
        resp = main.recognize_faces_from_image(tmp_path)
        result_json = parse_recognize_response(resp)

        # Determine classId for routing recognition to the correct session
        class_id = None
        if request.is_json:
            try:
                class_id = data.get("classId")
            except Exception:
                class_id = None
        if not class_id:
            class_id = request.args.get("classId")

        # If session active, parse recognized names and record them
        try:
            if result_json.get("status") == "success" and result_json.get("faces_detected", 0) > 0:
                names = []
                for r in result_json.get("results", []):
                    # result entries are {"name": name, ...} or {"error": ...
                    if "name" in r:
                        names.append(r["name"])
                if names:
                    if not class_id:
                        return jsonify({"status": "error", "message": "classId is required while a session is active"}), 400
                    # Route counts to the specific class session
                    scheduler_module.record_recognition_results_for_class(names, class_id)
        except Exception as e:
            # Do not fail recognition if recording fails; log and continue
            app.logger.error("Failed to record recognition results: %s", str(e))

        return jsonify(result_json)

    except Exception as e:
        app.logger.error("Error in /recognize_image: %s\n%s", str(e), traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        # cleanup temp file if exists
        try:
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass

# ------------------------------
# Student management endpoints
# ------------------------------
@app.route("/add_student", methods=["POST"])
def add_student_route():
    """
    Expects JSON:
    {
      "student_name": "Ahmed",
      "images": ["data:image/jpeg;base64,...", ...],
      "class_id": "CS101"  # Optional class ID
    }
    """
    try:
        images_b64 = []
        student_name = None
        class_id = "default"

        # Accept multipart/form-data (file upload) OR JSON with base64
        if request.files:
            # From form-data
            student_name = request.form.get("student_name")
            class_id = request.form.get("class_id", "default")
            # Support either multiple files under key 'images' or single 'image'
            files = request.files.getlist("images")
            if not files and "image" in request.files:
                files = [request.files["image"]]
            for file in files:
                content = file.read()
                if not content:
                    continue
                mime = file.mimetype or "image/jpeg"
                images_b64.append("data:" + mime + ";base64," + base64.b64encode(content).decode("utf-8"))
        else:
            # JSON
            data = request.get_json()
            student_name = (data or {}).get("student_name")
            images_b64 = (data or {}).get("images", [])
            class_id = (data or {}).get("class_id", "default")
            # Also allow single image field
            if not images_b64 and (data or {}).get("image"):
                images_b64 = [data.get("image")]

        if not student_name or not images_b64:
            return jsonify({"status": "error", "message": "Missing student_name or images"}), 400

        # Add student using existing function
        result = student_manage.add_student_from_api(student_name, images_b64)

        # Normalize result to dict for Firebase check
        result_json = {}
        if isinstance(result, tuple) and len(result) >= 1:
            resp_obj = result[0]
            if hasattr(resp_obj, "get_json"):
                result_json = resp_obj.get_json(silent=True) or {}
        elif hasattr(result, "get_json"):
            result_json = result.get_json(silent=True) or {}
        elif isinstance(result, dict):
            result_json = result

        # Also save to Firebase if available
        if firebase_manager and result_json.get("status") == "success":
            firebase_manager.save_student_data(
                student_id=student_name,
                student_name=student_name,
                class_id=class_id,
                additional_data={
                    'images_count': len(images_b64),
                    'added_at': datetime.now().isoformat()
                }
            )

        # Return original result to preserve response shape
        return result
        
    except Exception as e:
        app.logger.error("add_student error: %s", traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/remove_student/<student_name>", methods=["DELETE"])
def remove_student_route(student_name):
    try:
        result = student_manage.remove_student(student_name)
        
        # Also remove from Firebase if available
        if firebase_manager and result.get("status") == "success":
            # Note: Firebase doesn't have a direct delete method in our current setup
            # You might want to add a delete method to firebase_config.py
            pass
        
        return result
        
    except Exception as e:
        app.logger.error("remove_student error: %s", traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/list_students", methods=["GET"])
def list_students_route():
    try:
        students = [d for d in os.listdir(STUDENTS_DIR) if os.path.isdir(os.path.join(STUDENTS_DIR, d))]
        return jsonify({"count": len(students), "students": students})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ------------------------------
# Embeddings management
# ------------------------------
@app.route("/update_embeddings", methods=["POST"])
def update_embeddings_route():
    """
    Trigger recreation/update of embeddings.
    JSON optional body: {"n_aug": 3, "db_path": "...", "emb_path": "..."}
    """
    if manage_embeddings is None:
        return jsonify({"status": "error", "message": "manage_embeddings is unavailable"}), 500

    try:
        data = request.get_json(silent=True) or {}
        n_aug = int(data.get("n_aug", 1))
        db_path = data.get("db_path", STUDENTS_DIR)
        emb_path = data.get("emb_path", EMBEDDINGS_PATH)

        # Call the function (this may take time)
        manage_embeddings(db_path=db_path, N_AUG=n_aug, emb_path=emb_path)
        return jsonify({"status": "ok", "message": "Embeddings updated"})
    except Exception as e:
        app.logger.error("update_embeddings error: %s", traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

# (Scheduling endpoints removed)

@app.route("/session_status", methods=["GET"])
def session_status_route():
    try:
        class_id = request.args.get("classId")
        if not class_id:
            return jsonify({"status": "error", "message": "classId is required"}), 400
        return scheduler_module.get_session_status(class_id)
    except Exception as e:
        app.logger.error("get_session_status error: %s", traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

# ------------------------------
# Attendance files listing
# ------------------------------
@app.route("/attendance_files", methods=["GET"])
def attendance_files_route():
    try:
        files = [f for f in os.listdir(".") if f.startswith(ATTENDANCE_PREFIX) and f.endswith(".csv")]
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ------------------------------
# Endpoint to manually record recognition results (optional)
# ------------------------------
@app.route("/record_recognition", methods=["POST"])
def record_recognition_route():
    """
    Accepts JSON: {"recognized_names": ["Ahmed", "Usama", ...]}
    Useful if frontend does recognition and only wants to send names.
    """
    try:
        data = request.get_json()
        names = data.get("recognized_names", [])
        if not names:
            return jsonify({"status": "error", "message": "No recognized_names provided"}), 400
        return scheduler_module.record_recognition_results(names)
    except Exception as e:
        app.logger.error("record_recognition error: %s", traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500

# ------------------------------
# Serve embeddings file (download) - optional
# ------------------------------
@app.route("/download_embeddings", methods=["GET"])
def download_embeddings():
    try:
        if not os.path.exists(EMBEDDINGS_PATH):
            return jsonify({"status": "error", "message": "Embeddings file not found"}), 404
        return send_file(EMBEDDINGS_PATH, as_attachment=True)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ------------------------------
# Run server
# ------------------------------
if __name__ == "__main__":
    # Run the Flask app
    print("Starting Smart Attendance System API with Firebase...")
    app.run(host="0.0.0.0", port=5000, debug=True)
