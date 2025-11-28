from flask import Flask, request, jsonify
import os
import time
from transcription.transcription import transcribe_audio
from utils.gemini_utils import summarize_with_gemini, quiz_with_gemini
from utils.quiz_utils import parse_quiz_text, calculate_quiz_score
from firebase_integration import get_firebase_manager

app = Flask(__name__)

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
    
    Expected JSON:
    {
        "sessionId": "class101_session_20240115_143022",
        "classId": "class101",
        "file": <audio_file>
    }
    """
    if not firebase_manager:
        return jsonify({"error": "Firebase not initialized"}), 500
    
    if 'file' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    session_id = request.form.get('sessionId')
    class_id = request.form.get('classId')
    
    if not session_id or not class_id:
        return jsonify({"error": "sessionId and classId are required"}), 400
    
    # Update session status to processing
    firebase_manager.update_session_processing_status(session_id, "processing")
    
    try:
        # Save audio file temporarily
        audio = request.files['file']
        file_path = os.path.join(os.getcwd(), f"temp_audio_{session_id}.mp3")
        audio.save(file_path)
        
        # Transcribe
        start_time = time.time()
        transcript = transcribe_audio(file_path)
        transcription_time = time.time() - start_time
        
        if not transcript:
            firebase_manager.update_session_processing_status(session_id, "failed")
            os.remove(file_path)
            return jsonify({"error": "Transcription failed"}), 500
        
        # Save transcript
        transcript_id = firebase_manager.save_session_transcript(
            session_id=session_id,
            class_id=class_id,
            transcript_text=transcript,
            processing_time=transcription_time
        )
        
        if not transcript_id:
            firebase_manager.update_session_processing_status(session_id, "failed")
            os.remove(file_path)
            return jsonify({"error": "Failed to save transcript"}), 500
        
        # Generate summary
        summary_text = summarize_with_gemini(transcript)
        if summary_text and not summary_text.startswith("[ERROR]"):
            summary_id = firebase_manager.save_session_summary(
                session_id=session_id,
                transcript_id=transcript_id,
                class_id=class_id,
                summary_text=summary_text
            )
        else:
            summary_id = None
        
        # Generate quiz
        quiz_text = quiz_with_gemini(transcript)
        if quiz_text:
            # Parse quiz to structured format
            parsed_quiz = parse_quiz_text(quiz_text)
            
            quiz_id = firebase_manager.save_session_quiz(
                session_id=session_id,
                transcript_id=transcript_id,
                class_id=class_id,
                quiz_text=quiz_text,
                quiz_data=parsed_quiz,
                number_of_questions=parsed_quiz.get('numberOfQuestions', 5)
                
            )
        else:
            quiz_id = None
        
        # Clean up
        os.remove(file_path)
        
        return jsonify({
            "success": True,
            "message": "Session audio processed successfully",
            "sessionId": session_id,
            "transcriptId": transcript_id,
            "summaryId": summary_id,
            "quizId": quiz_id,
            "processingStatus": "completed"
        })
        
    except Exception as e:
        firebase_manager.update_session_processing_status(session_id, "failed")
        if os.path.exists(file_path):
            os.remove(file_path)
        return jsonify({"error": str(e)}), 500

@app.route('/get-session-transcript/<session_id>', methods=['GET'])
def get_session_transcript(session_id):
    """Get transcript for a session."""
    if not firebase_manager:
        return jsonify({"error": "Firebase not initialized"}), 500
    
    transcript = firebase_manager.get_session_transcript(session_id)
    
    if not transcript:
        return jsonify({"error": "Transcript not found for this session"}), 404
    
    return jsonify({
        "success": True,
        "transcript": transcript.get('transcriptText'),
        "language": transcript.get('language'),
        "createdAt": transcript.get('createdAt')
    })

@app.route('/get-session-summary/<session_id>', methods=['GET'])
def get_session_summary(session_id):
    """Get summary for a session."""
    if not firebase_manager:
        return jsonify({"error": "Firebase not initialized"}), 500
    
    summary = firebase_manager.get_session_summary(session_id)
    
    if not summary:
        return jsonify({"error": "Summary not found for this session"}), 404
    
    return jsonify({
        "success": True,
        "summary": summary.get('summaryText'),
        "createdAt": summary.get('createdAt')
    })

@app.route('/get-session-quiz/<session_id>', methods=['GET'])
def get_session_quiz(session_id):
    """Get quiz for a session."""
    if not firebase_manager:
        return jsonify({"error": "Firebase not initialized"}), 500
    
    quiz = firebase_manager.get_session_quiz(session_id)
    
    if not quiz:
        return jsonify({"error": "Quiz not found for this session"}), 404
    
    # Return both raw text and structured data if available
    response = {
        "success": True,
        "quizId": quiz.get('quizId'),
        "quizData": quiz.get('quizData'),
        "numberOfQuestions": quiz.get('numberOfQuestions'),
        "createdAt": quiz.get('createdAt')
    }
    
    if quiz.get('quizData'):
        response['quizData'] = quiz.get('quizData')
    
    return jsonify(response)

@app.route('/get-session-data/<session_id>', methods=['GET'])
def get_session_data(session_id):
    """Get complete session data including transcript, summary, and quiz."""
    if not firebase_manager:
        return jsonify({"error": "Firebase not initialized"}), 500
    
    session_data = firebase_manager.get_session_with_related_data(session_id)
    
    if not session_data:
        return jsonify({"error": "Session not found"}), 404
    
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
        "quiz": session_data.get('quiz')
    })

@app.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    """
    Submit quiz answers and calculate score.
    
    Expected JSON:
    {
        "quizId": "quiz_xxx",
        "sessionId": "session_xxx",
        "studentId": "student_xxx",
        "classId": "class_xxx",
        "answers": {
            "q1": "B",
            "q2": "A",
            ...
        },
        "timeSpent": 300  // optional, in seconds
    }
    """
    if not firebase_manager:
        return jsonify({"error": "Firebase not initialized"}), 500
    
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    required_fields = ['quizId', 'sessionId', 'studentId', 'classId', 'answers']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    try:
        # Get quiz data
        quiz = firebase_manager.get_session_quiz(data['sessionId'])
        if not quiz:
            return jsonify({"error": "Quiz not found"}), 404
        
        # Get structured quiz data
        quiz_data = quiz.get('quizData')
        if not quiz_data:
            # Try to parse from quiz text
            quiz_data = parse_quiz_text(quiz.get('quizText', ''))
        
        if not quiz_data or not quiz_data.get('questions'):
            return jsonify({"error": "Invalid quiz data"}), 400
        
        # Calculate score
        score_result = calculate_quiz_score(quiz_data, data['answers'])
        
        # Save attempt
        attempt_id = firebase_manager.save_quiz_attempt(
            quiz_id=data['quizId'],
            session_id=data['sessionId'],
            student_id=data['studentId'],
            class_id=data['classId'],
            answers=data['answers'],
            score=score_result['score'],
            correct_answers=score_result['correctAnswers'],
            total_questions=score_result['totalQuestions'],
            time_spent=data.get('timeSpent')
        )
        
        if not attempt_id:
            return jsonify({"error": "Failed to save quiz attempt"}), 500
        
        return jsonify({
            "success": True,
            "attemptId": attempt_id,
            "score": score_result['score'],
            "correctAnswers": score_result['correctAnswers'],
            "totalQuestions": score_result['totalQuestions'],
            "answerDetails": score_result['answerDetails']
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-student-attempts/<student_id>', methods=['GET'])
def get_student_attempts(student_id):
    """Get all quiz attempts for a student, optionally filtered by session."""
    if not firebase_manager:
        return jsonify({"error": "Firebase not initialized"}), 500
    
    session_id = request.args.get('sessionId')
    attempts = firebase_manager.get_student_quiz_attempts(student_id, session_id)
    
    return jsonify({
        "success": True,
        "studentId": student_id,
        "attempts": attempts,
        "totalAttempts": len(attempts)
    })


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
