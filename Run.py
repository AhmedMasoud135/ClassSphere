from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from main import mark_attendance
from flask import jsonify
import time

# ---------------------------------------------------------
# Global scheduler instance
# ---------------------------------------------------------
scheduler = BackgroundScheduler()
scheduler.start()

# ---------------------------------------------------------
# Global session state (shared with API endpoints)
# ---------------------------------------------------------
is_session_active = False
current_session_name = None
attendance_records = {}  # { "Ahmed": frame_count, "Usama": frame_count }


# ---------------------------------------------------------
# Core Logic: session job (controls active window)
# ---------------------------------------------------------
def run_session_job(session_name, duration):
    """
    Opens attendance for a set duration.
    During this time, API endpoints can record recognized faces.
    """
    global is_session_active, current_session_name, attendance_records

    is_session_active = True
    current_session_name = session_name
    attendance_records = {}

    print(f"[{datetime.now()}] Session '{session_name}' started for {duration} seconds...")

    time.sleep(duration)  # Keep session open

    # End session
    is_session_active = False
    print(f"[{datetime.now()}] Session '{session_name}' ended. Finalizing attendance...")

    # Save final attendance
    mark_attendance(session_name, attendance_records, duration)
    current_session_name = None
    print(f"[{datetime.now()}] Attendance for '{session_name}' saved successfully.")


# ---------------------------------------------------------
# Schedule a session at a given start time
# ---------------------------------------------------------
def schedule_session(session_name, start_time_str, duration_minutes):
    """
    Schedule a new attendance session to run automatically at the given datetime.
    """
    try:
        start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
        duration_seconds = duration_minutes * 60
        session_name_with_date = f"{session_name}_{start_time.strftime('%Y-%m-%d')}"

        scheduler.add_job(
            run_session_job,
            trigger="date",
            run_date=start_time,
            args=[session_name_with_date, duration_seconds],
            id=session_name_with_date,
            replace_existing=True
        )

        return jsonify({
            "status": "scheduled",
            "session_name": session_name_with_date,
            "start_time": start_time_str,
            "duration_seconds": duration_seconds
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# ---------------------------------------------------------
# List all scheduled sessions
# ---------------------------------------------------------
def list_scheduled_sessions():
    """Return all scheduled jobs."""
    jobs = scheduler.get_jobs()
    job_list = [
        {
            "id": job.id,
            "next_run_time": job.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
            if job.next_run_time else None
        }
        for job in jobs
    ]
    return jsonify({"scheduled_jobs": job_list})


# ---------------------------------------------------------
# Cancel a scheduled session
# ---------------------------------------------------------
def cancel_session(session_id):
    """Cancel a scheduled session."""
    try:
        scheduler.remove_job(session_id)
        return jsonify({"status": "cancelled", "session_id": session_id})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


# ---------------------------------------------------------
# API helper: get current session status
# ---------------------------------------------------------
def get_session_status():
    """Return whether a session is currently active."""
    return jsonify({
        "session_active": is_session_active,
        "session_name": current_session_name
    })


# ---------------------------------------------------------
# API helper: record recognition result (called by Flask route)
# ---------------------------------------------------------
def record_recognition_results(recognized_names):
    """
    Called by /api/recognize_image endpoint.
    Updates attendance during active session.
    """
    global attendance_records

    if not is_session_active:
        return jsonify({"status": "inactive", "message": "No active session."}), 403

    for name in recognized_names:
        if name != "Unknown":
            attendance_records[name] = attendance_records.get(name, 0) + 1

    return jsonify({"status": "recorded", "updated": attendance_records})

