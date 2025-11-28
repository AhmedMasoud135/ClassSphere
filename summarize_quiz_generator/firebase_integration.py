"""
Firebase integration for Session Transcript, Summary, and Quiz management.
Extends the existing FirebaseManager from ai-backend-attendance.
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
import sys



class ExtendedFirebaseManager:
    """
    Extended Firebase Manager for session transcripts, summaries, and quizzes.
    Uses the same Firebase instance as the attendance system.
    """
    
    def __init__(self, service_account_path: str = None):
        """Initialize with existing Firebase instance or create new one."""
        try:
            # Try to use existing Firebase instance
            if firebase_admin._apps:
                self.db = firestore.client()
                print("✅ Using existing Firebase Admin SDK instance")
            else:
                # Initialize new instance
                if service_account_path is None:
                    # Try to find service account key in parent directory
                    parent_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
                    if os.path.exists(parent_path):
                        service_account_path = parent_path
                    else:
                        service_account_path = "serviceAccountKey.json"
                
                if os.path.exists(service_account_path):
                    cred = credentials.Certificate(service_account_path)
                    firebase_admin.initialize_app(cred)
                    self.db = firestore.client()
                    print(f"✅ Firebase Admin SDK initialized from {service_account_path}")
                else:
                    raise FileNotFoundError(f"Service account key not found: {service_account_path}")
        except Exception as e:
            print(f"❌ Error initializing Firebase: {e}")
            raise e
    
    # ============================================================
    # SESSION TRANSCRIPT METHODS
    # ============================================================
    
    def save_session_transcript(self, session_id: str, class_id: str, 
                               transcript_text: str, language: str = "en",
                               transcription_model: str = "whisper-base",
                               processing_time: float = None) -> Optional[str]:
        """
        Save session transcript to Firestore.
        
        Args:
            session_id: Session identifier
            class_id: Class identifier
            transcript_text: Transcribed text
            language: Language code (default: "en")
            transcription_model: Model used (default: "whisper-base")
            processing_time: Processing time in seconds
            
        Returns:
            transcript_id if successful, None otherwise
        """
        try:
            transcript_id = f"transcript_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            transcript_data = {
                'transcriptId': transcript_id,
                'sessionId': session_id,
                'classId': class_id,
                'transcriptText': transcript_text,
                'language': language,
                'transcriptionModel': transcription_model,
                'createdAt': firestore.SERVER_TIMESTAMP,
                'updatedAt': firestore.SERVER_TIMESTAMP
            }
            
            if processing_time is not None:
                transcript_data['processingTime'] = processing_time
            
            self.db.collection('session_transcripts').document(transcript_id).set(transcript_data)
            
            # Update session document with transcript ID
            self.db.collection('sessions').document(session_id).update({
                'transcriptId': transcript_id,
                'audioProcessed': True,
                'processingStatus': 'completed',
                'updatedAt': firestore.SERVER_TIMESTAMP
            })
            
            print(f"✅ Transcript saved: {transcript_id}")
            return transcript_id
            
        except Exception as e:
            print(f"❌ Error saving transcript: {e}")
            return None
    
    def get_session_transcript(self, session_id: str) -> Optional[Dict]:
        """Get transcript for a session."""
        try:
            query = self.db.collection('session_transcripts').where('sessionId', '==', session_id).limit(1)
            docs = list(query.stream())
            
            if docs:
                data = docs[0].to_dict()
                data['id'] = docs[0].id
                return data
            return None
            
        except Exception as e:
            print(f"❌ Error getting transcript: {e}")
            return None
    
    # ============================================================
    # SESSION SUMMARY METHODS
    # ============================================================
    
    def save_session_summary(self, session_id: str, transcript_id: str, 
                            class_id: str, summary_text: str,
                            model: str = "gemini-2.5-flash") -> Optional[str]:
        """
        Save session summary to Firestore.
        
        Args:
            session_id: Session identifier
            transcript_id: Related transcript identifier
            class_id: Class identifier
            summary_text: Summary text
            model: Model used (default: "gemini-2.5-flash")
            
        Returns:
            summary_id if successful, None otherwise
        """
        try:
            summary_id = f"summary_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            summary_data = {
                'summaryId': summary_id,
                'sessionId': session_id,
                'transcriptId': transcript_id,
                'classId': class_id,
                'summaryText': summary_text,
                'model': model,
                'createdAt': firestore.SERVER_TIMESTAMP,
                'updatedAt': firestore.SERVER_TIMESTAMP
            }
            
            self.db.collection('session_summaries').document(summary_id).set(summary_data)
            
            # Update session document with summary ID
            self.db.collection('sessions').document(session_id).update({
                'summaryId': summary_id,
                'updatedAt': firestore.SERVER_TIMESTAMP
            })
            
            print(f"✅ Summary saved: {summary_id}")
            return summary_id
            
        except Exception as e:
            print(f"❌ Error saving summary: {e}")
            return None
    
    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """Get summary for a session."""
        try:
            query = self.db.collection('session_summaries').where('sessionId', '==', session_id).limit(1)
            docs = list(query.stream())
            
            if docs:
                data = docs[0].to_dict()
                data['id'] = docs[0].id
                return data
            return None
            
        except Exception as e:
            print(f"❌ Error getting summary: {e}")
            return None
    
    # ============================================================
    # SESSION QUIZ METHODS
    # ============================================================
    
    def save_session_quiz(self, session_id: str, transcript_id: str,
                         class_id: str, quiz_text: str,
                         number_of_questions: int = 5,
                         quiz_data: Dict = None,
                         model: str = "gemini-2.5-flash") -> Optional[str]:
        """
        Save session quiz to Firestore.
        
        Args:
            session_id: Session identifier
            transcript_id: Related transcript identifier
            class_id: Class identifier
            quiz_text: Quiz text (raw format)
            number_of_questions: Number of questions
            quiz_data: Optional structured quiz data
            model: Model used (default: "gemini-2.5-flash")
            
        Returns:
            quiz_id if successful, None otherwise
        """
        try:
            quiz_id = f"quiz_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            quiz_document = {
                'quizId': quiz_id,
                'sessionId': session_id,
                'transcriptId': transcript_id,
                'classId': class_id,
                'quizText': quiz_text,
                'quizData': quiz_data,
                'numberOfQuestions': number_of_questions,
                'model': model,
                'createdAt': firestore.SERVER_TIMESTAMP,
                'updatedAt': firestore.SERVER_TIMESTAMP
            }
            
            self.db.collection('session_quizzes').document(quiz_id).set(quiz_document)
            
            # Update session document with quiz ID
            self.db.collection('sessions').document(session_id).update({
                'quizId': quiz_id,
                'updatedAt': firestore.SERVER_TIMESTAMP
            })
            
            print(f"✅ Quiz saved: {quiz_id}")
            return quiz_id
            
        except Exception as e:
            print(f"❌ Error saving quiz: {e}")
            return None
    
    def get_session_quiz(self, session_id: str) -> Optional[Dict]:
        """Get quiz for a session."""
        try:
            query = self.db.collection('session_quizzes').where('sessionId', '==', session_id).limit(1)
            docs = list(query.stream())
            
            if docs:
                data = docs[0].to_dict()
                data['id'] = docs[0].id
                return data
            return None
            
        except Exception as e:
            print(f"❌ Error getting quiz: {e}")
            return None
    
    # ============================================================
    # QUIZ ATTEMPTS METHODS
    # ============================================================
    
    def save_quiz_attempt(self, quiz_id: str, session_id: str, 
                         student_id: str, class_id: str,
                         answers: Dict[str, str],
                         score: float, correct_answers: int,
                         total_questions: int,
                         time_spent: int = None) -> Optional[str]:
        """
        Save student quiz attempt.
        
        Args:
            quiz_id: Quiz identifier
            session_id: Session identifier
            student_id: Student identifier
            class_id: Class identifier
            answers: Dictionary of question_id -> answer
            score: Score percentage
            correct_answers: Number of correct answers
            total_questions: Total number of questions
            time_spent: Time spent in seconds
            
        Returns:
            attempt_id if successful, None otherwise
        """
        try:
            attempt_id = f"attempt_{quiz_id}_{student_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            attempt_data = {
                'attemptId': attempt_id,
                'quizId': quiz_id,
                'sessionId': session_id,
                'studentId': student_id,
                'classId': class_id,
                'answers': answers,
                'score': score,
                'correctAnswers': correct_answers,
                'totalQuestions': total_questions,
                'submittedAt': firestore.SERVER_TIMESTAMP,
                'createdAt': firestore.SERVER_TIMESTAMP
            }
            
            if time_spent is not None:
                attempt_data['timeSpent'] = time_spent
            
            self.db.collection('quiz_attempts').document(attempt_id).set(attempt_data)
            
            print(f"✅ Quiz attempt saved: {attempt_id}")
            return attempt_id
            
        except Exception as e:
            print(f"❌ Error saving quiz attempt: {e}")
            return None
    
    def get_student_quiz_attempts(self, student_id: str, session_id: str = None) -> List[Dict]:
        """Get all quiz attempts for a student, optionally filtered by session."""
        try:
            if session_id:
                query = self.db.collection('quiz_attempts').where('studentId', '==', student_id).where('sessionId', '==', session_id)
            else:
                query = self.db.collection('quiz_attempts').where('studentId', '==', student_id)
            
            docs = query.stream()
            attempts = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                attempts.append(data)
            
            return attempts
            
        except Exception as e:
            print(f"❌ Error getting quiz attempts: {e}")
            return []
    
    def get_quiz_attempt(self, attempt_id: str) -> Optional[Dict]:
        """Get a specific quiz attempt by ID."""
        try:
            doc = self.db.collection('quiz_attempts').document(attempt_id).get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
            
        except Exception as e:
            print(f"❌ Error getting quiz attempt: {e}")
            return None
    
    # ============================================================
    # SESSION STATUS METHODS
    # ============================================================
    
    def update_session_processing_status(self, session_id: str, status: str):
        """
        Update session processing status.
        
        Args:
            session_id: Session identifier
            status: "pending" | "processing" | "completed" | "failed"
        """
        try:
            self.db.collection('sessions').document(session_id).update({
                'processingStatus': status,
                'updatedAt': firestore.SERVER_TIMESTAMP
            })
            print(f"✅ Session status updated: {session_id} -> {status}")
        except Exception as e:
            print(f"❌ Error updating session status: {e}")
    
    def get_session_with_related_data(self, session_id: str) -> Optional[Dict]:
        """Get session with all related data (transcript, summary, quiz)."""
        try:
            session_doc = self.db.collection('sessions').document(session_id).get()
            if not session_doc.exists:
                return None
            
            session_data = session_doc.to_dict()
            session_data['id'] = session_doc.id
            
            # Get transcript
            transcript = self.get_session_transcript(session_id)
            if transcript:
                session_data['transcript'] = transcript
            
            # Get summary
            summary = self.get_session_summary(session_id)
            if summary:
                session_data['summary'] = summary
            
            # Get quiz
            quiz = self.get_session_quiz(session_id)
            if quiz:
                session_data['quiz'] = quiz
            
            return session_data
            
        except Exception as e:
            print(f"❌ Error getting session with related data: {e}")
            return None


# Global instance
_firebase_manager = None

def get_firebase_manager() -> ExtendedFirebaseManager:
    """Get or create global Firebase manager instance."""
    global _firebase_manager
    if _firebase_manager is None:
        _firebase_manager = ExtendedFirebaseManager()
    return _firebase_manager

