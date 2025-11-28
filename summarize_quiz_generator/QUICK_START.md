# Quick Start Guide - ClassSphere Integration

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies

```bash
cd summarize_quiz_generator
pip install -r requirements.txt
```

### Step 2: Verify Firebase Setup

Ensure your Firebase service account key exists:
```
ai-backend-attendance/serviceAccountKey.json
```

### Step 3: Start the Server

```bash
python app.py
```

Server runs on `http://localhost:5000`

### Step 4: Test the Integration

#### Test 1: Process Session Audio
```bash
curl -X POST http://localhost:5000/process-session-audio \
  -F "file=@test_audio.mp3" \
  -F "sessionId=test_session_001" \
  -F "classId=test_class"
```

#### Test 2: Get Transcript
```bash
curl http://localhost:5000/get-session-transcript/test_session_001
```

#### Test 3: Get Summary
```bash
curl http://localhost:5000/get-session-summary/test_session_001
```

#### Test 4: Get Quiz
```bash
curl http://localhost:5000/get-session-quiz/test_session_001
```

#### Test 5: Submit Quiz
```bash
curl -X POST http://localhost:5000/submit-quiz \
  -H "Content-Type: application/json" \
  -d '{
    "quizId": "quiz_test_session_001_xxx",
    "sessionId": "test_session_001",
    "studentId": "student123",
    "classId": "test_class",
    "answers": {
      "q1": "B",
      "q2": "A",
      "q3": "C"
    }
  }'
```

---

## 📁 What Was Created

### New Files:
- `firebase_integration.py` - Extended Firebase manager
- `utils/quiz_utils.py` - Quiz parsing and scoring utilities
- `DATABASE_STRUCTURE.md` - Complete database schema
- `INTEGRATION_GUIDE.md` - Full integration documentation
- `QUICK_START.md` - This file

### Updated Files:
- `app.py` - Added integrated endpoints
- `ai-backend-attendance/firebase_config.py` - Added new session fields
- `ai-backend-attendance/main.py` - Passes classId to sessions

---

## 🔗 Integration Points

### How It Connects:

1. **Attendance System** creates sessions with:
   - `classId` (NEW)
   - `processingStatus: "pending"` (NEW)
   - `audioProcessed: false` (NEW)

2. **Audio Processing System** updates sessions with:
   - `transcriptId` → Links to `session_transcripts`
   - `summaryId` → Links to `session_summaries`
   - `quizId` → Links to `session_quizzes`
   - `processingStatus: "completed"`

3. **Students** can:
   - Read transcripts
   - Read summaries
   - Take quizzes
   - View their scores

---

## 📊 Database Collections Created

When you process your first audio:

1. **session_transcripts** - Stores transcribed text
2. **session_summaries** - Stores AI summaries
3. **session_quizzes** - Stores quiz questions
4. **quiz_attempts** - Stores student submissions

All linked via `sessionId` to the existing `sessions` collection.

---

## ✅ Verification Checklist

Run through this checklist to verify everything works:

- [ ] Server starts without errors
- [ ] Firebase connection successful (check console logs)
- [ ] Can process test audio file
- [ ] Transcript appears in Firestore `session_transcripts`
- [ ] Summary appears in Firestore `session_summaries`
- [ ] Quiz appears in Firestore `session_quizzes`
- [ ] Session document updated with IDs
- [ ] Can retrieve transcript via API
- [ ] Can retrieve summary via API
- [ ] Can retrieve quiz via API
- [ ] Can submit quiz answers
- [ ] Score calculated correctly
- [ ] Attempt saved to `quiz_attempts`

---

## 🐛 Common Issues

### Issue: "Firebase not initialized"
**Solution**: Check that `serviceAccountKey.json` exists in `../ai-backend-attendance/`

### Issue: "Session not found"
**Solution**: Make sure session was created in attendance system first

### Issue: "Transcription failed"
**Solution**: Check audio file format (MP3, WAV) and that Whisper model is loaded

---

## 📚 Next Steps

1. Read `INTEGRATION_GUIDE.md` for detailed documentation
2. Review `DATABASE_STRUCTURE.md` for schema details
3. Integrate with your frontend
4. Add authentication/authorization
5. Set up Firestore security rules

---

## 💡 Pro Tips

1. **Use structured quiz data**: The API returns both `quizText` (raw) and `quizData` (structured) - use `quizData` for easier frontend rendering

2. **Monitor processing status**: Check `processingStatus` field in sessions to show loading states in UI

3. **Handle errors gracefully**: All endpoints return proper error codes - handle them in your frontend

4. **Cache quiz data**: Once a quiz is generated, it doesn't change - cache it for better performance

5. **Track attempts**: Use `get-student-attempts` to show students their quiz history

---

## 🎉 You're Ready!

Your system is now fully integrated. Students can access transcripts, summaries, and take quizzes for their sessions!

For detailed API documentation, see `INTEGRATION_GUIDE.md`.

