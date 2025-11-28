# ClassSphere Integration Guide
## Session Transcript, Summary & Quiz System

This guide explains how to use the fully integrated system that connects session audio processing with the attendance system.

---

## 📋 Overview

The integrated system allows:
1. **Teachers** to upload session audio after a class ends
2. **System** to automatically transcribe, summarize, and generate quizzes
3. **Students** to access transcripts, summaries, and take quizzes
4. **All data** stored in Firestore with proper relationships

---

## 🔧 Setup

### 1. Install Dependencies

Make sure you have all required packages:

```bash
cd summarize_quiz_generator
pip install -r requirements.txt

# Also install Firebase Admin SDK if not already installed
pip install firebase-admin
```

### 2. Firebase Configuration

The system automatically uses the Firebase configuration from `ai-backend-attendance`:
- Service account key: `../ai-backend-attendance/serviceAccountKey.json`
- Same Firestore database instance

Ensure the service account key has proper permissions for:
- Reading/writing to `sessions` collection
- Creating `session_transcripts`, `session_summaries`, `session_quizzes`, `quiz_attempts` collections

---

## 📊 Database Structure

See `DATABASE_STRUCTURE.md` for complete schema details.

### Key Collections:
- **sessions** - Links to transcripts, summaries, quizzes
- **session_transcripts** - Transcribed session audio
- **session_summaries** - AI-generated summaries
- **session_quizzes** - Generated quiz questions
- **quiz_attempts** - Student quiz submissions and scores

---

## 🚀 Usage Workflow

### Step 1: Session Ends (Automatic)

When a session ends in the attendance system:
- Session is saved to `sessions` collection
- `processingStatus` = `"pending"`
- `audioProcessed` = `false`

### Step 2: Teacher Uploads Audio

After the session ends, teacher uploads the audio file:

```bash
curl -X POST http://localhost:5000/process-session-audio \
  -F "file=@session_audio.mp3" \
  -F "sessionId=class101_session_20240115_143022" \
  -F "classId=class101"
```

**Response:**
```json
{
  "success": true,
  "message": "Session audio processed successfully",
  "sessionId": "class101_session_20240115_143022",
  "transcriptId": "transcript_class101_session_20240115_143022_20240115_150000",
  "summaryId": "summary_class101_session_20240115_143022_20240115_150005",
  "quizId": "quiz_class101_session_20240115_143022_20240115_150010",
  "processingStatus": "completed"
}
```

**What happens:**
1. Audio is transcribed using Whisper
2. Transcript saved to `session_transcripts`
3. Summary generated with Gemini
4. Summary saved to `session_summaries`
5. Quiz generated with Gemini
6. Quiz saved to `session_quizzes`
7. Session document updated with IDs and status

### Step 3: Students Access Data

#### Get Transcript
```bash
GET http://localhost:5000/get-session-transcript/class101_session_20240115_143022
```

**Response:**
```json
{
  "success": true,
  "transcript": "Full transcript text...",
  "language": "en",
  "createdAt": "2024-01-15T15:00:00Z"
}
```

#### Get Summary
```bash
GET http://localhost:5000/get-session-summary/class101_session_20240115_143022
```

**Response:**
```json
{
  "success": true,
  "summary": "6-10 sentence summary...",
  "createdAt": "2024-01-15T15:00:05Z"
}
```

#### Get Quiz
```bash
GET http://localhost:5000/get-session-quiz/class101_session_20240115_143022
```

**Response:**
```json
{
  "success": true,
  "quizId": "quiz_xxx",
  "quizText": "1. Question text?\nA) Option 1\n...",
  "numberOfQuestions": 5,
  "quizData": {
    "questions": [
      {
        "questionId": "q1",
        "questionText": "Question text?",
        "options": {
          "A": "Option 1",
          "B": "Option 2",
          "C": "Option 3",
          "D": "Option 4"
        },
        "correctAnswer": "B"
      }
    ]
  },
  "createdAt": "2024-01-15T15:00:10Z"
}
```

#### Get Complete Session Data
```bash
GET http://localhost:5000/get-session-data/class101_session_20240115_143022
```

Returns everything: session info, transcript, summary, and quiz in one response.

### Step 4: Student Takes Quiz

Student submits quiz answers:

```bash
POST http://localhost:5000/submit-quiz
Content-Type: application/json

{
  "quizId": "quiz_class101_session_20240115_143022_20240115_150010",
  "sessionId": "class101_session_20240115_143022",
  "studentId": "student123",
  "classId": "class101",
  "answers": {
    "q1": "B",
    "q2": "A",
    "q3": "C",
    "q4": "D",
    "q5": "A"
  },
  "timeSpent": 300
}
```

**Response:**
```json
{
  "success": true,
  "attemptId": "attempt_quiz_xxx_student123_20240115_151000",
  "score": 80.0,
  "correctAnswers": 4,
  "totalQuestions": 5,
  "answerDetails": [
    {
      "questionId": "q1",
      "questionText": "Question text?",
      "studentAnswer": "B",
      "correctAnswer": "B",
      "isCorrect": true
    },
    ...
  ]
}
```

### Step 5: View Student Attempts

Get all quiz attempts for a student:

```bash
GET http://localhost:5000/get-student-attempts/student123
```

Or filter by session:

```bash
GET http://localhost:5000/get-student-attempts/student123?sessionId=class101_session_20240115_143022
```

---

## 🔌 API Endpoints Reference

### Integrated Endpoints (with Firebase)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/process-session-audio` | Process audio, save transcript/summary/quiz |
| GET | `/get-session-transcript/<session_id>` | Get session transcript |
| GET | `/get-session-summary/<session_id>` | Get session summary |
| GET | `/get-session-quiz/<session_id>` | Get session quiz |
| GET | `/get-session-data/<session_id>` | Get complete session data |
| POST | `/submit-quiz` | Submit quiz answers and get score |
| GET | `/get-student-attempts/<student_id>` | Get student's quiz attempts |

### Standalone Endpoints (testing only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/transcribe` | Transcribe audio (no DB) |
| POST | `/summarize` | Summarize audio (no DB) |
| POST | `/quiz` | Generate quiz (no DB) |
| POST | `/full-process` | Full process (no DB) |

---

## 🔍 Frontend Integration Examples

### React/JavaScript Example

```javascript
// 1. Upload audio after session ends
async function uploadSessionAudio(sessionId, classId, audioFile) {
  const formData = new FormData();
  formData.append('file', audioFile);
  formData.append('sessionId', sessionId);
  formData.append('classId', classId);
  
  const response = await fetch('/process-session-audio', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}

// 2. Get session transcript for student
async function getTranscript(sessionId) {
  const response = await fetch(`/get-session-transcript/${sessionId}`);
  const data = await response.json();
  return data.transcript;
}

// 3. Get session summary
async function getSummary(sessionId) {
  const response = await fetch(`/get-session-summary/${sessionId}`);
  const data = await response.json();
  return data.summary;
}

// 4. Get quiz and display to student
async function getQuiz(sessionId) {
  const response = await fetch(`/get-session-quiz/${sessionId}`);
  const data = await response.json();
  return data.quizData; // Structured format
}

// 5. Submit quiz answers
async function submitQuiz(quizId, sessionId, studentId, classId, answers, timeSpent) {
  const response = await fetch('/submit-quiz', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      quizId,
      sessionId,
      studentId,
      classId,
      answers,
      timeSpent
    })
  });
  
  return await response.json();
}
```

---

## 🔐 Security Considerations

1. **Authentication**: Add authentication middleware to endpoints
2. **Authorization**: Verify students can only access their class sessions
3. **File Upload**: Validate audio file type and size
4. **Rate Limiting**: Prevent abuse of API endpoints
5. **Firestore Rules**: Set up proper security rules (see `DATABASE_STRUCTURE.md`)

---

## 🐛 Troubleshooting

### Firebase Not Initialized
- Check that `serviceAccountKey.json` exists in `ai-backend-attendance/`
- Verify Firebase Admin SDK is installed
- Check service account permissions

### Transcription Fails
- Verify audio file format (MP3, WAV supported)
- Check Whisper model is loaded
- Ensure sufficient disk space for temp files

### Quiz Parsing Issues
- Check `quiz_utils.py` parsing logic
- Verify Gemini response format matches expected structure

### Session Not Found
- Ensure session was created in attendance system first
- Check session_id format matches

---

## 📝 Next Steps

1. **Add Authentication**: Integrate with your auth system
2. **Add Notifications**: Notify students when quiz is available
3. **Add Analytics**: Track quiz performance per student/class
4. **Add UI**: Build frontend components for transcript/summary/quiz display
5. **Add Retry Logic**: Handle failed transcriptions gracefully

---

## 🎯 Complete Workflow Diagram

```
Session Ends (Attendance System)
    ↓
Session saved with status="pending"
    ↓
Teacher uploads audio → /process-session-audio
    ↓
Status → "processing"
    ↓
Transcribe Audio → Save to session_transcripts
    ↓
Generate Summary → Save to session_summaries
    ↓
Generate Quiz → Save to session_quizzes
    ↓
Status → "completed"
    ↓
Students can now access:
  - Transcript → /get-session-transcript
  - Summary → /get-session-summary
  - Quiz → /get-session-quiz
    ↓
Student takes quiz → /submit-quiz
    ↓
Score calculated and saved to quiz_attempts
```

---

## ✅ Testing Checklist

- [ ] Session created with proper fields in Firestore
- [ ] Audio processing saves transcript correctly
- [ ] Summary generated and saved
- [ ] Quiz generated and parsed correctly
- [ ] Student can retrieve transcript/summary/quiz
- [ ] Quiz submission calculates score correctly
- [ ] Attempt saved to database
- [ ] Student attempts query works

---

## 📞 Support

For issues or questions:
1. Check `DATABASE_STRUCTURE.md` for schema details
2. Review Firebase console for data
3. Check API logs for errors
4. Verify all dependencies are installed

