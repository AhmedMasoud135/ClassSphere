# app.py
"""
Main Flask application that integrates:
- main.py: recognition + attendance saving
- smart_attendance_scheduler.py: scheduling + session state
- Student_Manage.py: add/remove student images (from frontend)
- EncodeGenerator.py: manage_embeddings (safely imported)
"""

import os
import io
import json
import base64
import tempfile
import traceback
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

import main  
import Run as scheduler_module  
import Student_Manage as student_manage  

# We need to safely import manage_embeddings from EncodeGenerator 
# because the file may call manage_embeddings(...) at module top-level.
# To avoid that side-effect, we parse & execute only the function definition.
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
        # Also keep helper defs if any (not expected), but skip other top-level calls

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
        "message": "Smart Attendance System API",
        "endpoints": {
            "POST /recognize_image": "Upload image (base64 or file) for recognition",
            "POST /add_student": "Add student with list of base64 images",
            "DELETE /remove_student/<name>": "Remove student",
            "POST /update_embeddings": "Rebuild/update embeddings (calls manage_embeddings)",
            "POST /schedule": "Schedule a session",
            "GET /sessions": "List scheduled sessions",
            "DELETE /cancel/<session_id>": "Cancel scheduled session",
            "GET /session_status": "Get current session status",
            "GET /list_students": "List registered students",
            "GET /attendance_files": "List attendance CSV files"
        }
    })


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

        # If session active, parse recognized names and record them
        try:
            if result_json.get("status") == "success" and result_json.get("faces_detected", 0) > 0:
                names = []
                for r in result_json.get("results", []):
                    # result entries are {"name": name, ...} or {"error": ...
                    if "name" in r:
                        names.append(r["name"])
                if names:
                    # record_recognition_results returns a Flask JSON response; ignore return
                    scheduler_module.record_recognition_results(names)
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
      "images": ["data:image/jpeg;base64,...", ...]
    }
    """
    try:
        data = request.get_json()
        student_name = data.get("student_name")
        images = data.get("images", [])
        if not student_name or not images:
            return jsonify({"status": "error", "message": "Missing student_name or images"}), 400

        return student_manage.add_student_from_api(student_name, images)
    except Exception as e:
        app.logger.error("add_student error: %s", traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/remove_student/<student_name>", methods=["DELETE"])
def remove_student_route(student_name):
    try:
        return student_manage.remove_student(student_name)
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


# ------------------------------
# Scheduler endpoints
# ------------------------------
@app.route("/schedule", methods=["POST"])
def schedule_route():
    """
    JSON: { "session_name": "CS101", "start_time": "YYYY-MM-DD HH:MM:SS", "duration_minutes": 2 }
    """
    try:
        data = request.get_json()
        session_name = data.get("session_name")
        start_time = data.get("start_time")
        duration_minutes = int(data.get("duration_minutes", 1))
        if not session_name or not start_time:
            return jsonify({"status": "error", "message": "Missing session_name or start_time"}), 400
        return scheduler_module.schedule_session(session_name, start_time, duration_minutes)
    except Exception as e:
        app.logger.error("schedule error: %s", traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/sessions", methods=["GET"])
def list_sessions_route():
    try:
        return scheduler_module.list_scheduled_sessions()
    except Exception as e:
        app.logger.error("list_sessions error: %s", traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/cancel/<session_id>", methods=["DELETE"])
def cancel_session_route(session_id):
    try:
        return scheduler_module.cancel_session(session_id)
    except Exception as e:
        app.logger.error("cancel_session error: %s", traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/session_status", methods=["GET"])
def session_status_route():
    try:
        return scheduler_module.get_session_status()
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
    print("Starting Smart Attendance System API...")
    app.run(host="0.0.0.0", port=5000, debug=True)
