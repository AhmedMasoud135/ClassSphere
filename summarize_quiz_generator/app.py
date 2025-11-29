from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
from transcription.transcription import transcribe_audio
from utils.gemini_utils import summarize_with_gemini, quiz_with_gemini
from utils.quiz_utils import parse_quiz_text, calculate_quiz_score
from firebase_integration import get_firebase_manager


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# In-memory cache for sessions (works without Firebase)
session_cache = {}

# Initialize Firebase manager
try:
    firebase_manager = get_firebase_manager()
    print("✅ Firebase integration ready")
except Exception as e:
    print(f"⚠️ Firebase initialization warning: {e}")
    firebase_manager = None


@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the ClassSphere Audio Summarizer & Quiz API!",
        "endpoints": {
            "integrated": [
                "POST /process-session-audio - Process session audio and save to database",
                "GET /get-session-transcript/<session_id> - Get session transcript",
                "GET /get-session-summary/<session_id> - Get session summary",
                "GET /get-session-quiz/<session_id> - Get session quiz",
                "POST /submit-quiz - Submit quiz answers",
                "GET /get-student-attempts/<student_id> - Get student quiz attempts",
                "GET /get-session-data/<session_id> - Get complete session data"
            ],
        }
    })


@app.route('/process-session-audio', methods=['POST'])
def process_session_audio():
    """
    Process session audio: transcribe, summarize, generate quiz, and save to Firestore.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    session_id = request.form.get('sessionId')
    class_id = request.form.get('classId')
    
    if not session_id or not class_id:
        return jsonify({"error": "sessionId and classId are required"}), 400
    
    file_path = None
    
    # Update session status to processing (ignore errors)
    if firebase_manager:
        try:
            firebase_manager.update_session_processing_status(session_id, "processing")
        except Exception as e:
            print(f"⚠️ Firebase error (ignored): {e}")
    
    try:
        # Save audio file temporarily
        audio = request.files['file']
        file_path = os.path.join(os.getcwd(), f"temp_audio_{session_id}.mp3")
        audio.save(file_path)
        
        print(f"[INFO] Audio file saved to: {file_path}")
        
        # Transcribe
        start_time = time.time()
        transcript = transcribe_audio(file_path)
        transcription_time = time.time() - start_time
        
        if not transcript:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            return jsonify({"error": "Transcription failed"}), 500
        
        # Save transcript (ignore Firebase errors)
        transcript_id = None
        if firebase_manager:
            try:
                transcript_id = firebase_manager.save_session_transcript(
                    session_id=session_id,
                    class_id=class_id,
                    transcript_text=transcript,
                    processing_time=transcription_time
                )
            except Exception as e:
                print(f"⚠️ Failed to save transcript to Firebase (ignored): {e}")
                transcript_id = f"local_{session_id}_transcript"
        else:
            transcript_id = f"local_{session_id}_transcript"
        
        # Generate summary
        summary_text = summarize_with_gemini(transcript)
        summary_id = None
        
        if summary_text and not summary_text.startswith("[ERROR]"):
            if firebase_manager:
                try:
                    summary_id = firebase_manager.save_session_summary(
                        session_id=session_id,
                        transcript_id=transcript_id,
                        class_id=class_id,
                        summary_text=summary_text
                    )
                except Exception as e:
                    print(f"⚠️ Failed to save summary to Firebase (ignored): {e}")
                    summary_id = f"local_{session_id}_summary"
            else:
                summary_id = f"local_{session_id}_summary"
        
        # Generate quiz
        quiz_text = quiz_with_gemini(transcript)
        quiz_id = None
        parsed_quiz = None
        
        if quiz_text:
            # Parse quiz to structured format
            parsed_quiz = parse_quiz_text(quiz_text)
            
            if firebase_manager:
                try:
                    quiz_id = firebase_manager.save_session_quiz(
                        session_id=session_id,
                        transcript_id=transcript_id,
                        class_id=class_id,
                        quiz_text=quiz_text,
                        quiz_data=parsed_quiz,
                        number_of_questions=parsed_quiz.get('numberOfQuestions', 5)
                    )
                except Exception as e:
                    print(f"⚠️ Failed to save quiz to Firebase (ignored): {e}")
                    quiz_id = f"local_{session_id}_quiz"
            else:
                quiz_id = f"local_{session_id}_quiz"
        
        # Store in cache for later retrieval
        session_cache[session_id] = {
            'transcript': transcript,
            'summary': summary_text,
            'quiz': parsed_quiz,
            'transcriptId': transcript_id,
            'summaryId': summary_id,
            'quizId': quiz_id,
            'timestamp': time.time()
        }
        
        # Clean up
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        
        # Update status to completed (ignore errors)
        if firebase_manager:
            try:
                firebase_manager.update_session_processing_status(session_id, "completed")
            except Exception as e:
                print(f"⚠️ Failed to update status (ignored): {e}")
        
        print(f"✅ Session {session_id} processed successfully and cached")
        
        return jsonify({
            "success": True,
            "message": "Session audio processed successfully",
            "sessionId": session_id,
            "transcript": transcript,
            "summary": summary_text,
            "quiz": parsed_quiz,
            "transcriptId": transcript_id,
            "summaryId": summary_id,
            "quizId": quiz_id,
            "processingStatus": "completed",
            "firebaseStatus": "disabled" if not firebase_manager else "partial"
        })
        
    except Exception as e:
        print(f"[ERROR] Exception in process_session_audio: {e}")
        import traceback
        traceback.print_exc()
        
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({"error": str(e)}), 500


@app.route('/get-session-transcript/<session_id>', methods=['GET'])
def get_session_transcript(session_id):
    """Get transcript for a session."""
    # Try cache first
    if session_id in session_cache:
        print(f"✅ Returning transcript from cache for session: {session_id}")
        return jsonify({
            "success": True,
            "transcript": session_cache[session_id]['transcript'],
            "source": "cache"
        })
    
    # Fall back to Firebase
    if not firebase_manager:
        return jsonify({"error": "Data not available - Firebase not initialized and not in cache"}), 404
    
    try:
        transcript = firebase_manager.get_session_transcript(session_id)
        if transcript:
            return jsonify({
                "success": True,
                "transcript": transcript.get('transcriptText'),
                "language": transcript.get('language'),
                "createdAt": transcript.get('createdAt'),
                "source": "firebase"
            })
    except Exception as e:
        print(f"❌ Error getting transcript from Firebase: {e}")
    
    return jsonify({"error": "Transcript not found"}), 404


@app.route('/get-session-summary/<session_id>', methods=['GET'])
def get_session_summary(session_id):
    """Get summary for a session."""
    # Try cache first
    if session_id in session_cache:
        print(f"✅ Returning summary from cache for session: {session_id}")
        return jsonify({
            "success": True,
            "summary": session_cache[session_id]['summary'],
            "source": "cache"
        })
    
    # Fall back to Firebase
    if not firebase_manager:
        return jsonify({"error": "Data not available - Firebase not initialized and not in cache"}), 404
    
    try:
        summary = firebase_manager.get_session_summary(session_id)
        if summary:
            return jsonify({
                "success": True,
                "summary": summary.get('summaryText'),
                "createdAt": summary.get('createdAt'),
                "source": "firebase"
            })
    except Exception as e:
        print(f"❌ Error getting summary from Firebase: {e}")
    
    return jsonify({"error": "Summary not found"}), 404


@app.route('/get-session-quiz/<session_id>', methods=['GET'])
def get_session_quiz(session_id):
    """Get quiz for a session."""
    # Try cache first
    if session_id in session_cache:
        print(f"✅ Returning quiz from cache for session: {session_id}")
        cached_data = session_cache[session_id]
        quiz_data = cached_data['quiz']
        return jsonify({
            "success": True,
            "quizId": cached_data['quizId'],
            "quizData": quiz_data,
            "numberOfQuestions": quiz_data.get('numberOfQuestions', 0) if quiz_data else 0,
            "source": "cache"
        })
    
    # Fall back to Firebase
    if not firebase_manager:
        return jsonify({"error": "Data not available - Firebase not initialized and not in cache"}), 404
    
    try:
        quiz = firebase_manager.get_session_quiz(session_id)
        if quiz:
            return jsonify({
                "success": True,
                "quizId": quiz.get('quizId'),
                "quizData": quiz.get('quizData'),
                "numberOfQuestions": quiz.get('numberOfQuestions'),
                "createdAt": quiz.get('createdAt'),
                "source": "firebase"
            })
    except Exception as e:
        print(f"❌ Error getting quiz from Firebase: {e}")
    
    return jsonify({"error": "Quiz not found"}), 404


@app.route('/get-session-data/<session_id>', methods=['GET'])
def get_session_data(session_id):
    """Get complete session data including transcript, summary, and quiz."""
    # Try cache first
    if session_id in session_cache:
        print(f"✅ Returning complete session data from cache for: {session_id}")
        cached = session_cache[session_id]
        return jsonify({
            "success": True,
            "session": {
                "sessionId": session_id,
                "processingStatus": "completed"
            },
            "transcript": cached['transcript'],
            "summary": cached['summary'],
            "quiz": cached['quiz'],
            "source": "cache"
        })
    
    # Fall back to Firebase
    if not firebase_manager:
        return jsonify({"error": "Data not available - Firebase not initialized and not in cache"}), 404
    
    try:
        session_data = firebase_manager.get_session_with_related_data(session_id)
        if session_data:
            return jsonify({
                "success": True,
                "session": {
                    "sessionId": session_data.get('sessionId'),
                    "sessionName": session_data.get('sessionName'),
                    "classId": session_data.get('classId'),
                    "startTime": session_data.get('startTime'),
                    "endTime": session_data.get('endTime'),
                    "processingStatus": session_data.get('processingStatus')
                },
                "transcript": session_data.get('transcript'),
                "summary": session_data.get('summary'),
                "quiz": session_data.get('quiz'),
                "source": "firebase"
            })
    except Exception as e:
        print(f"❌ Error getting session data from Firebase: {e}")
    
    return jsonify({"error": "Session not found"}), 404


@app.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    """Submit quiz answers and calculate score."""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    required_fields = ['quizId', 'sessionId', 'studentId', 'classId', 'answers']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    session_id = data['sessionId']
    
    # Try to get quiz from cache first
    quiz_data = None
    if session_id in session_cache:
        quiz_data = session_cache[session_id].get('quiz')
    
    # If not in cache, try Firebase
    if not quiz_data and firebase_manager:
        try:
            quiz = firebase_manager.get_session_quiz(session_id)
            if quiz:
                quiz_data = quiz.get('quizData')
                if not quiz_data:
                    quiz_data = parse_quiz_text(quiz.get('quizText', ''))
        except Exception as e:
            print(f"⚠️ Error getting quiz from Firebase: {e}")
    
    if not quiz_data or not quiz_data.get('questions'):
        return jsonify({"error": "Quiz not found or invalid"}), 404
    
    try:
        # Calculate score
        score_result = calculate_quiz_score(quiz_data, data['answers'])
        
        # Try to save attempt to Firebase (ignore errors)
        attempt_id = None
        if firebase_manager:
            try:
                attempt_id = firebase_manager.save_quiz_attempt(
                    quiz_id=data['quizId'],
                    session_id=session_id,
                    student_id=data['studentId'],
                    class_id=data['classId'],
                    answers=data['answers'],
                    score=score_result['score'],
                    correct_answers=score_result['correctAnswers'],
                    total_questions=score_result['totalQuestions'],
                    time_spent=data.get('timeSpent')
                )
            except Exception as e:
                print(f"⚠️ Failed to save quiz attempt to Firebase (ignored): {e}")
                attempt_id = f"local_attempt_{int(time.time())}"
        else:
            attempt_id = f"local_attempt_{int(time.time())}"
        
        return jsonify({
            "success": True,
            "attemptId": attempt_id,
            "score": score_result['score'],
            "correctAnswers": score_result['correctAnswers'],
            "totalQuestions": score_result['totalQuestions'],
            "answerDetails": score_result['answerDetails']
        })
        
    except Exception as e:
        print(f"[ERROR] Error in submit_quiz: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/get-student-attempts/<student_id>', methods=['GET'])
def get_student_attempts(student_id):
    """Get all quiz attempts for a student, optionally filtered by session."""
    if not firebase_manager:
        return jsonify({
            "success": True,
            "studentId": student_id,
            "attempts": [],
            "totalAttempts": 0,
            "message": "Firebase not available - no attempt history"
        })
    
    try:
        session_id = request.args.get('sessionId')
        attempts = firebase_manager.get_student_quiz_attempts(student_id, session_id)
        
        return jsonify({
            "success": True,
            "studentId": student_id,
            "attempts": attempts,
            "totalAttempts": len(attempts)
        })
    except Exception as e:
        print(f"⚠️ Error getting student attempts: {e}")
        return jsonify({
            "success": True,
            "studentId": student_id,
            "attempts": [],
            "totalAttempts": 0,
            "error": str(e)
        })


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
