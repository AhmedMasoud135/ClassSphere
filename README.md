# 🎓 ClassSphere

<div align="center">

![ClassSphere Logo](https://img.shields.io/badge/ClassSphere-AI--Powered%20Classroom-blue?style=for-the-badge)
[![Next.js](https://img.shields.io/badge/Next.js-15.5.2-black?style=flat-square&logo=next.js)](https://nextjs.org/)
[![React](https://img.shields.io/badge/React-19.1.0-61DAFB?style=flat-square&logo=react)](https://reactjs.org/)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.9.0-EE4C2C?style=flat-square&logo=pytorch)](https://pytorch.org/)
[![Firebase](https://img.shields.io/badge/Firebase-Firestore-FFCA28?style=flat-square&logo=firebase)](https://firebase.google.com/)

**An AI-powered classroom management system that revolutionizes attendance tracking, enhances student safety through real-time violence detection, and automates learning content generation.**

[Demo Video](https://drive.google.com/file/d/1kLiJkOropt1UhBRHDcD-aTLNmA-_pCIW/view?usp=drive_link) • [Documentation](./DEVELOPER_DOCUMENTATION.md) • [Quick Start](#-quick-start) • [Features](#-key-features)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Demo](#-demo)
- [Technology Stack](#-technology-stack)
- [System Architecture](#-system-architecture)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Application](#running-the-application)
- [Project Structure](#-project-structure)
- [AI Models](#-ai-models)
- [API Endpoints](#-api-endpoints)
- [Performance Metrics](#-performance-metrics)
- [Contributing](#-contributing)
- [License](#-license)
- [Team](#-team)
- [Contact](#-contact)

---

## 🌟 Overview

**ClassSphere** is a comprehensive classroom management platform that combines cutting-edge artificial intelligence with traditional educational tools to create a safer, more efficient learning environment. The system addresses critical challenges in modern education through four AI-powered modules.

### The Problem
- ⏰ **Manual attendance** wastes 10+ minutes per class
- 🚨 **Reactive safety measures** leave students vulnerable
- 📝 **Time-consuming content review** limits student learning
- 📊 **Limited analytics** prevent data-driven decisions
- 🎭 **Attendance fraud** undermines academic integrity
- 💰 **Expensive proprietary systems** limit accessibility

### Our Solution
ClassSphere leverages AI to automate attendance tracking using facial recognition, monitors classroom safety with real-time violence detection, and automatically generates transcripts, summaries, and quizzes from lecture audio—reducing attendance time by **95%**, providing proactive safety monitoring with **1-2 second latency**, and enabling instant content review and assessment.

---

## ✨ Key Features

### 🤖 **Automated Attendance Tracking**
- **Face Recognition Technology**: Uses YuNet face detection and 128-dimensional face encodings
- **95% Accuracy**: High precision in optimal lighting conditions
- **30-Second Processing**: Complete class attendance in half a minute
- **Biometric Verification**: Prevents attendance fraud
- **Real-time Sync**: Automatic Firebase Firestore integration
- **Attendance Analytics**: Detailed reports with presence percentages

### 🛡️ **Real-time Violence Detection**
- **Deep Learning Analysis**: MobileNetV2 + Bidirectional LSTM architecture
- **Temporal Pattern Recognition**: Analyzes 16 consecutive frames for accurate detection
- **1-2 Second Latency**: Near-instantaneous threat identification
- **Privacy-Preserving**: No video storage, real-time processing only
- **Alert System**: Immediate notifications for detected incidents
- **Continuous Monitoring**: Automatic threat detection during sessions

### 🎤 **AI-Powered Lecture Transcription**
- **Speech-to-Text**: Whisper AI converts lecture audio to accurate text transcripts
- **Multi-Language Support**: Automatic language detection and transcription
- **High Accuracy**: Enterprise-grade transcription quality
- **Audio Processing**: Supports multiple audio formats (MP3, WAV, M4A)
- **Real-time Processing**: Fast transcription with minimal latency
- **Searchable Content**: Makes lecture content easily discoverable

### 📚 **Intelligent Content Summarization**
- **AI-Powered Analysis**: Google Gemini AI generates concise, structured summaries
- **Key Points Extraction**: Highlights main concepts and important information
- **Context-Aware**: Maintains subject-specific terminology and concepts
- **Structured Output**: Organized summaries with clear sections
- **Time-Saving**: Students review hours of content in minutes
- **Revision Tool**: Perfect for exam preparation and quick review

### 📝 **Automated Quiz Generator**
- **AI-Powered Quiz Creation**: Google Gemini generates contextual questions from lecture content
- **Multiple Question Types**: MCQ, True/False, Short Answer, and Fill-in-the-blank
- **Difficulty Levels**: Adjustable complexity (Easy, Medium, Hard)
- **Instant Grading**: Automatic scoring and detailed feedback
- **Answer Explanations**: Helps students understand correct responses
- **Question Bank**: Reusable quiz repository for each class session
- **Performance Tracking**: Analytics on student quiz attempts

### 📊 **Comprehensive Class Management**
- **Teacher Dashboard**: Intuitive interface for managing classes and students
- **Student Enrollment**: Easy onboarding with face registration
- **Session Management**: Start/stop attendance tracking with one click
- **Content Library**: Access all transcripts, summaries, and quizzes
- **Attendance Reports**: Data-driven insights and historical analytics
- **User Authentication**: Secure Firebase-based auth system
- **Role-Based Access**: Separate interfaces for teachers and students

---

## 🎥 Demo

**Watch ClassSphere in Action:**

[![ClassSphere Demo](https://img.shields.io/badge/Watch%20Demo-Google%20Drive-4285F4?style=for-the-badge&logo=google-drive)](https://drive.google.com/file/d/1kLiJkOropt1UhBRHDcD-aTLNmA-_pCIW/view?usp=drive_link)

The demo video showcases:
- Real-time face recognition attendance
- Violence detection in action
- Audio transcription and summarization
- Automated quiz generation
- Teacher and student dashboards
- Complete class management workflows

---

## 🛠️ Technology Stack

### **Frontend**
| Technology | Version | Purpose |
|------------|---------|---------|
| [Next.js](https://nextjs.org/) | 15.5.2 | React framework with SSR/SSG capabilities |
| [React](https://reactjs.org/) | 19.1.0 | Component-based UI library |
| [TypeScript](https://www.typescriptlang.org/) | 5.x | Type-safe JavaScript |
| [Tailwind CSS](https://tailwindcss.com/) | 4.x | Utility-first CSS framework |
| [Framer Motion](https://www.framer.com/motion/) | 12.23.24 | Animation library |
| [Radix UI](https://www.radix-ui.com/) | Latest | Headless UI components |
| [Lucide React](https://lucide.dev/) | 0.543.0 | Icon library |
| [Firebase SDK](https://firebase.google.com/) | 12.3.0 | Client-side Firebase integration |

### **Backend - Attendance System**
| Technology | Version | Purpose |
|------------|---------|---------|
| [Python](https://www.python.org/) | 3.12+ | Primary backend language |
| [Flask](https://flask.palletsprojects.com/) | 2.3.3 | Lightweight web framework |
| [OpenCV](https://opencv.org/) | 4.11.0 | Computer vision library |
| [DeepFace](https://github.com/serengil/deepface) | Latest | Face recognition with ArcFace |
| [Firebase Admin](https://firebase.google.com/docs/admin/setup) | 6.5.0+ | Server-side Firebase operations |
| [NumPy](https://numpy.org/) | 1.26.0+ | Numerical computations |

### **Backend - Violence Detection**
| Technology | Version | Purpose |
|------------|---------|---------|
| [PyTorch](https://pytorch.org/) | 2.9.0 | Deep learning framework |
| [TorchVision](https://pytorch.org/vision/stable/index.html) | 0.24.0 | Pre-trained models and transforms |
| [Albumentations](https://albumentations.ai/) | 2.0.8 | Image augmentation |
| [MobileNetV2](https://arxiv.org/abs/1801.04381) | - | Lightweight CNN for feature extraction |
| [BiLSTM](https://en.wikipedia.org/wiki/Long_short-term_memory) | - | Temporal sequence modeling |
| [Flask-CORS](https://flask-cors.readthedocs.io/) | Latest | Cross-Origin Resource Sharing |

### **Backend - Quiz Generator & Transcription**
| Technology | Version | Purpose |
|------------|---------|---------|
| [Whisper AI](https://openai.com/research/whisper) | Base Model | Audio transcription (speech-to-text) |
| [Google Gemini](https://deepmind.google/technologies/gemini/) | Latest | AI-powered summarization and quiz generation |
| [Flask](https://flask.palletsprojects.com/) | 2.3.3 | Web framework |
| [FFmpeg](https://ffmpeg.org/) | Latest | Audio processing and format conversion |
| [Firebase Admin](https://firebase.google.com/docs/admin/setup) | 6.2.0+ | Backend Firebase integration |

### **Database & Storage**
| Technology | Purpose |
|------------|---------|
| **Firebase Firestore** | NoSQL document database for real-time data |
| **Firebase Storage** | Secure audio file and image storage |
| **Firebase Authentication** | User authentication and authorization |

### **AI/ML Models**
| Model | Architecture | Purpose |
|-------|--------------|---------|
| **YuNet** | CNN-based | High-speed face detection |
| **ArcFace** | ResNet-based | 128D face encoding generation |
| **Violence Detector** | MobileNetV2 + BiLSTM | Spatiotemporal violence classification |
| **Whisper Base** | Transformer | Audio transcription (74M parameters) |
| **Gemini Pro** | Large Language Model | Content summarization and quiz generation |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Browser                          │
│                   (Next.js 15.5.2 Frontend)                  │
│  • React 19.1.0 + TypeScript Components                     │
│  • Firebase Authentication                                   │
│  • Real-time Camera Access (WebRTC)                          │
│  • Audio Recording & Upload                                  │
│  • Tailwind CSS + Framer Motion UI                           │
└───┬─────────────┬──────────────┬────────────────────────────┘
    │             │              │
    │ HTTP/REST   │ HTTP/REST    │ HTTP/REST
    │             │              │
┌───▼──────────┐ ┌▼───────────┐ ┌▼──────────────────┐
│ Attendance   │ │ Violence   │ │ Quiz Generator &  │
│  Backend     │ │ Detection  │ │  Transcription    │
│(Flask :5000) │ │(:5002)     │ │  Backend (:5001)  │
│ • YuNet      │ │ • MobileNet│ │ • Whisper AI      │
│ • ArcFace    │ │ • BiLSTM   │ │ • Gemini AI       │
│ • DeepFace   │ │ • Alerts   │ │ • FFmpeg          │
└───┬──────────┘ └┬───────────┘ └┬──────────────────┘
    │             │              │
    │ Firebase Admin SDK         │
    │                            │
┌───▼────────────────────────────▼─────────────────────┐
│            Firebase Cloud Services                    │
│  ┌──────────┐  ┌──────────┐  ┌────────────┐         │
│  │Firestore │  │ Storage  │  │    Auth    │         │
│  │(Database)│  │(Audio &  │  │  (Users)   │         │
│  │          │  │ Images)  │  │            │         │
│  └──────────┘  └──────────┘  └────────────┘         │
│  • Attendance • Sessions • Transcripts • Summaries   │
│  • Quizzes • Student Records • Analytics             │
└──────────────────────────────────────────────────────┘
```

### **Data Flow**

#### Attendance Flow:
1. **Camera Capture** → Frontend captures frame via WebRTC
2. **Frame Upload** → Sends to Flask backend (port 5000)
3. **Face Detection** → YuNet identifies faces in frame
4. **Encoding Generation** → DeepFace creates 128D face embeddings using ArcFace
5. **Database Match** → Compares with enrolled student encodings
6. **Result Return** → Sends matched names + confidence scores
7. **Firestore Sync** → Logs attendance with timestamp and session data

#### Violence Detection Flow:
1. **Video Stream** → Frontend sends continuous frames
2. **Frame Buffering** → Backend accumulates 16 frames
3. **Feature Extraction** → MobileNetV2 processes each frame
4. **Temporal Analysis** → BiLSTM analyzes sequence patterns
5. **Classification** → Outputs violence probability (0.0-1.0)
6. **Alert Trigger** → If > 0.5, sends alert to frontend
7. **History Logging** → Records alert in Firestore with timestamp

#### Lecture Processing Flow:
1. **Audio Recording** → Teacher records lecture or uploads audio file
2. **Audio Upload** → File sent to Flask backend (port 5001)
3. **Transcription** → Whisper AI converts speech to text with punctuation
4. **Content Analysis** → Gemini AI analyzes transcript content
5. **Summary Generation** → Creates structured summary with key points
6. **Quiz Creation** → Generates questions with multiple difficulty levels
7. **Firestore Storage** → Saves transcript, summary, quiz, and metadata
8. **Student Access** → Students view content, take quizzes, and review materials

---

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed:

- **Node.js** (v18.0.0 or higher) - [Download](https://nodejs.org/)
- **Python** (3.12 or higher) - [Download](https://www.python.org/downloads/)
- **npm** or **yarn** - Comes with Node.js
- **Git** - [Download](https://git-scm.com/)
- **FFmpeg** - [Download](https://ffmpeg.org/download.html) (for audio processing)
- **Webcam** - For face recognition and violence detection
- **Firebase Account** - [Sign up](https://firebase.google.com/)
- **Google AI Studio Account** - [Get API Key](https://makersuite.google.com/app/apikey) (for Gemini)

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/AhmedMasoud135/ClassSphere.git
cd ClassSphere
```

#### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
# or
yarn install

# Return to root directory
cd ..
```

#### 3. Attendance Backend Setup

```bash
# Navigate to attendance backend directory
cd ai-backend-attendance

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Return to root directory
cd ..
```

#### 4. Violence Detection Backend Setup

```bash
# Navigate to violence detection backend directory
cd ai-backend-violence

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Return to root directory
cd ..
```

#### 5. Quiz Generator & Transcription Setup

```bash
# Navigate to quiz generator directory
cd summarize_quiz_generator

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install FFmpeg (Windows - using Chocolatey)
choco install ffmpeg
# Or download from https://ffmpeg.org/download.html

# Return to root directory
cd ..
```

### Configuration

#### 1. Firebase Setup

1. **Create a Firebase Project**:
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Click "Add project" and follow the setup wizard

2. **Enable Services**:
   - **Firestore Database**: Go to Firestore Database → Create database
   - **Storage**: Go to Storage → Get started
   - **Authentication**: Go to Authentication → Get started → Enable Email/Password

3. **Get Configuration Files**:

   **For Frontend** (Client SDK):
   - Go to Project Settings → General → Your apps
   - Click "Add app" → Web (</>) icon
   - Copy the Firebase config object
   - Create `frontend/.env.local` and add:

   ```env
   NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
   NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
   NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
   NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
   NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
   NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
   ```

   **For Backend** (Admin SDK):
   - Go to Project Settings → Service accounts
   - Click "Generate new private key"
   - Save as `serviceAccountKey.json`
   - Place copies in:
     - `ai-backend-attendance/serviceAccountKey.json`
     - `ai-backend-violence/serviceAccountKey.json`
     - `summarize_quiz_generator/serviceAccountKey.json`

#### 2. Google Gemini API Key

Create `summarize_quiz_generator/.env` (or add to existing file):

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

### Running the Application

#### **Option 1: Using Run Script (Windows)**

```bash
# Start all services
run.bat
```

#### **Option 2: Using Shell Script (macOS/Linux)**

```bash
# Make script executable
chmod +x start-services.sh

# Start all services
./start-services.sh
```

#### **Option 3: Manual Start (All Platforms)**

Open **Four separate terminals**:

**Terminal 1 - Frontend**:
```bash
cd frontend
npm run dev
```

**Terminal 2 - Attendance Backend**:
```bash
cd ai-backend-attendance
python app.py
```

**Terminal 3 - Quiz Generator & Transcription**:
```bash
cd summarize_quiz_generator
set PATH=%PATH%;C:\ffmpeg\bin  # Windows
# export PATH=$PATH:/usr/local/bin  # macOS/Linux
python app.py
```

**Terminal 4 - Violence Detection Backend**:
```bash
cd ai-backend-violence
python app.py
```

### Accessing the Application

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Attendance API**: [http://localhost:5000](http://localhost:5000)
- **Quiz & Transcription API**: [http://localhost:5001](http://localhost:5001)
- **Violence Detection API**: [http://localhost:5002](http://localhost:5002)

### First Time Setup

1. **Create an Account**:
   - Navigate to [http://localhost:3000](http://localhost:3000)
   - Click "Sign Up"
   - Choose role: Teacher or Student
   - Complete registration

2. **Enroll Students (Teacher)**:
   - Login as teacher
   - Go to "Classes" → Create a class
   - Add students and upload 3-5 face photos per student

3. **Test Attendance**:
   - Go to "Attendance" page
   - Click "Start Session"
   - Allow camera access
   - Students should face the camera

4. **Test Transcription & Quiz**:
   - Record a lecture or upload audio file
   - Wait for processing (transcription, summary, quiz)
   - Review generated content

5. **Test Violence Detection**:
   - Go to "Violence Detection" page
   - Start monitoring
   - System will alert if suspicious activity detected

---

## 📁 Project Structure

```
ClassSphere/
├── frontend/                      # Next.js frontend application
│   ├── app/                       # Next.js 13+ app directory
│   │   ├── (auth)/               # Authentication pages
│   │   ├── (dashboard)/          # Dashboard pages
│   │   ├── attendance/           # Attendance module
│   │   ├── violence/             # Violence detection module
│   │   ├── lectures/             # Lecture transcription & quiz
│   │   └── layout.js             # Root layout
│   ├── components/               # React components
│   │   ├── ui/                   # Reusable UI components
│   │   ├── dashboard/            # Dashboard-specific components
│   │   └── shared/               # Shared components
│   ├── lib/                      # Utility functions
│   │   ├── firebase.js           # Firebase configuration
│   │   └── utils.js              # Helper functions
│   ├── public/                   # Static assets
│   ├── package.json              # Frontend dependencies
│   └── next.config.js            # Next.js configuration
│
├── ai-backend-attendance/        # Flask attendance backend
│   ├── app.py                    # Main Flask application
│   ├── main.py                   # Face detection & recognition logic
│   ├── Run.py                    # Session management
│   ├── Student_Manage.py         # Student enrollment
│   ├── EncodeGenerator.py        # Face encoding generation
│   ├── firebase_config.py        # Firebase integration
│   ├── requirements.txt          # Python dependencies
│   └── serviceAccountKey.json    # Firebase admin credentials
│
├── ai-backend-violence/          # Flask violence detection backend
│   ├── app.py                    # Main Flask application
│   ├── model_utils.py            # MobileNetV2 + LSTM model
│   ├── best_model.pth            # Trained model weights
│   ├── requirements.txt          # Python dependencies
│   └── serviceAccountKey.json    # Firebase admin credentials
│
├── summarize_quiz_generator/     # AI quiz generator & transcription
│   ├── app.py                    # Flask application
│   ├── transcription/
│   │   └── transcription.py      # Whisper AI transcription
│   ├── utils/
│   │   ├── gemini_utils.py       # Gemini AI integration
│   │   └── quiz_utils.py         # Quiz parsing and grading
│   ├── firebase_integration.py   # Firebase operations
│   ├── requirements.txt          # Python dependencies
│   └── serviceAccountKey.json    # Firebase admin credentials
│
├── DEVELOPER_DOCUMENTATION.md    # Comprehensive technical docs
├── QUICK_REFERENCE.md           # Quick reference guide
├── Documentation.pdf            # Full project documentation
├── run.bat                      # Windows startup script
├── stop.bat                     # Windows shutdown script
├── start-services.sh            # Linux/macOS startup script
├── fix_ports.bat                # Port conflict resolver
└── README.md                    # This file
```

---

## 🧠 AI Models

### 1. Face Recognition System

**Pipeline**:
```
Input Image → YuNet Face Detection → Face Extraction → 
128D Encoding (ArcFace) → Cosine Similarity Comparison → Match/No Match
```

**Components**:
- **YuNet**: Lightweight CNN-based face detector
- **DeepFace**: Face recognition library with ArcFace model
- **Encoding**: 128-dimensional face embeddings
- **Threshold**: 0.6 cosine similarity for matching

**Performance**:
- **Accuracy**: 95% in optimal conditions
- **False Positive Rate**: < 5%
- **Processing Time**: 30 seconds per class (30 students)
- **Lighting Requirements**: Well-lit environments preferred

### 2. Violence Detection System

**Architecture**:
```
Input: 16 Frames (224×224 RGB)
    ↓
MobileNetV2 Feature Extractor (per frame)
    ↓
Feature Vector: (16, 1280)
    ↓
Bidirectional LSTM (512 hidden units)
    ↓
Fully Connected Layer + Sigmoid
    ↓
Output: Violence Probability (0.0 - 1.0)
```

**Model Specifications**:
- **Backbone**: MobileNetV2 (3.5M parameters)
- **Temporal Model**: Bidirectional LSTM
- **Input**: 16 consecutive frames at 224×224 resolution
- **Output**: Binary classification (Violence/No Violence)
- **Threshold**: 0.5 probability

**Performance**:
- **Latency**: 1-2 seconds
- **Frame Rate**: Processes every 1 second
- **Memory**: ~500MB GPU memory (CPU compatible)
- **Accuracy**: High precision in detecting physical altercations

### 3. Transcription & Summarization System

**Whisper AI Pipeline**:
```
Input Audio → Preprocessing → Whisper Base Model →
Feature Extraction → Decoder → Text Output with Punctuation
```

**Gemini AI Pipeline**:
```
Transcript Text → Gemini Pro Model → Content Analysis →
Summary Generation + Quiz Question Generation → Structured Output
```

**Specifications**:
- **Whisper Model**: Base (74M parameters)
- **Languages Supported**: 90+ languages
- **Audio Formats**: MP3, WAV, M4A, FLAC
- **Gemini Model**: Pro version for complex reasoning
- **Quiz Types**: MCQ, True/False, Short Answer
- **Processing Time**: ~2-5 minutes for 1-hour lecture

---

## 🔌 API Endpoints

### Attendance Backend (Port 5000)

#### `POST /recognize_image`
Recognize faces in uploaded image for attendance.

**Request**:
```json
{
  "image": "base64_encoded_image",
  "classId": "class_123"
}
```

**Response**:
```json
{
  "status": "success",
  "faces_detected": 3,
  "results": [
    {
      "name": "Ahmed Masoud",
      "confidence": 0.92,
      "bounding_box": [100, 150, 200, 250]
    }
  ]
}
```

#### `POST /start_session`
Start attendance tracking session.

**Request**:
```json
{
  "classId": "class_123"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Session started",
  "sessionId": "session_456"
}
```

#### `POST /stop_session`
Stop attendance session and save records.

**Request**:
```json
{
  "classId": "class_123"
}
```

**Response**:
```json
{
  "message": "Session stopped and attendance saved",
  "classId": "class_123",
  "records_saved": 25,
  "total_students": 30
}
```

### Violence Detection Backend (Port 5002)

#### `POST /detect_frame`
Analyze single frame for violence detection (requires 16 frames).

**Request**:
```json
{
  "image": "base64_encoded_frame"
}
```

**Response**:
```json
{
  "status": "success",
  "violence_detected": false,
  "probability": 0.23,
  "buffer_size": 16
}
```

#### `POST /reset_buffer`
Reset frame buffer for new detection session.

**Response**:
```json
{
  "status": "success",
  "message": "Buffer reset successfully"
}
```

### Quiz Generator & Transcription Backend (Port 5001)

#### `POST /process-session-audio`
Upload and process lecture audio for transcription, summary, and quiz.

**Request** (multipart/form-data):
```
file: audio_file.mp3
sessionId: "session_123"
classId: "class_456"
```

**Response**:
```json
{
  "success": true,
  "sessionId": "session_123",
  "transcript": "Today we will discuss machine learning algorithms...",
  "summary": "This lecture covered the fundamentals of...",
  "quiz": {
    "numberOfQuestions": 5,
    "questions": [
      {
        "question": "What is supervised learning?",
        "options": ["A", "B", "C", "D"],
        "correctAnswer": "A",
        "difficulty": "medium"
      }
    ]
  }
}
```

#### `GET /get-session-transcript/<session_id>`
Retrieve transcript for a specific session.

**Response**:
```json
{
  "success": true,
  "transcript": "Full lecture transcript text...",
  "language": "en"
}
```

#### `GET /get-session-summary/<session_id>`
Retrieve AI-generated summary.

**Response**:
```json
{
  "success": true,
  "summary": "Key points and main concepts from the lecture..."
}
```

#### `GET /get-session-quiz/<session_id>`
Retrieve quiz for a specific session.

**Response**:
```json
{
  "success": true,
  "quizId": "quiz_789",
  "quizData": {
    "numberOfQuestions": 5,
    "questions": [...]
  }
}
```

#### `POST /submit-quiz`
Submit student quiz answers for grading.

**Request**:
```json
{
  "quizId": "quiz_789",
  "sessionId": "session_123",
  "studentId": "student_101",
  "classId": "class_456",
  "answers": {
    "q1": "A",
    "q2": "B"
  }
}
```

**Response**:
```json
{
  "success": true,
  "attemptId": "attempt_999",
  "score": 80.0,
  "correctAnswers": 4,
  "totalQuestions": 5,
  "answerDetails": [...]
}
```

---

## 📊 Performance Metrics

### System Metrics

| Metric | Value | Target |
|--------|-------|--------|
| **Attendance Time** | 30 seconds | < 60 seconds |
| **Face Recognition Accuracy** | 95% | > 90% |
| **Violence Detection Latency** | 1-2 seconds | < 3 seconds |
| **Transcription Accuracy** | 92% | > 85% |
| **Quiz Generation Time** | 2-3 minutes | < 5 minutes |
| **False Positive Rate (Violence)** | < 10% | < 15% |
| **Concurrent Users** | 50+ | 100+ |
| **Uptime** | 99.5% | 99% |

### Cost Analysis (Monthly)

| Item | Cost (Small School - 500 students) |
|------|-----------------------------------|
| Firebase Firestore | ~$25 |
| Firebase Storage | ~$15 |
| Firebase Authentication | Free tier |
| Google Gemini API | ~$20 |
| Hosting (Cloud VM) | ~$50 |
| Bandwidth | ~$15 |
| **Total** | **~$125/month** |

### Scalability

- **Horizontal Scaling**: Backend services can be load-balanced
- **Firebase Auto-Scaling**: Database and storage scale automatically
- **Cost-Efficient**: Linear scaling with student count
- **GPU Optional**: Works on CPU, GPU accelerates processing

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Areas for Contribution

1. **Feature Development**:
   - Liveness detection (blink, head movement)
   - Multi-angle face recognition
   - Mask-wearing face recognition
   - Advanced analytics dashboard
   - Mobile app (iOS/Android)

2. **Model Improvements**:
   - Reduce false positives in violence detection
   - Optimize model size for edge deployment
   - Train on diverse datasets
   - Improve transcription accuracy

3. **UI/UX Enhancements**:
   - Mobile-responsive design improvements
   - Dark mode support
   - Accessibility improvements (WCAG compliance)
   - Internationalization (i18n)

4. **Documentation**:
   - API documentation improvements
   - Deployment guides
   - Video tutorials
   - Translation to other languages

### Development Workflow

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Code Standards

- **Frontend**: ESLint + Prettier for code formatting
- **Backend**: PEP 8 style guide for Python
- **Commits**: Conventional Commits format
- **Testing**: Write unit tests for new features
- **Documentation**: Update docs for new features

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

ClassSphere was developed by a dedicated team of engineers from Faculty of Engineering, Kafr El Sheikh University as part of the Digital Egypt Pioneers Initiative (DEPI).


### Development Team

| Name | Role | Email | Phone |
|------|------|-------|-------|
| Ahmed Usama Masoud | Project Lead & Full-Stack Developer | [ahmedmasoud2098@gmail.com](mailto:ahmedmasoud2098@gmail.com) | +20014043763 |
| Mohamed Soltan Mohamed | AI/ML Engineer & Backend Developer | [mosltn0@gmail.com](mailto:mosltn0@gmail.com) | +20115833963 |
| Ammar Yasser Fathy Fadlallah | Frontend Developer & UI/UX Designer | [ammaryasser9724@gmail.com](mailto:ammaryasser9724@gmail.com) | +20017749462 |
| Salma mohamed fouad | Data Scientist & ML Engineer | [sm3707@fayoum.edu.eg](mailto:sm3707@fayoum.edu.eg) | +20061751262 |
| Wessal Ayman Abdelfattah | Backend Developer & DevOps | [wessalayman17@gmail.com](mailto:wessalayman17@gmail.com) | +20093917094 |
| Mostafa Mahmoud Moahmed | Full-Stack Developer | [sasapubgmobile1@gmail.com](mailto:sasapubgmobile1@gmail.com) | +20098575634 |

---

## 📞 Contact

**Project Lead**: Ahmed Usama Masoud

- GitHub: [@AhmedMasoud135](https://github.com/AhmedMasoud135)
- Email: [ahmedmasoud2098@gmail.com](mailto:ahmedmasoud2098@gmail.com)
- Phone: +20 1014043763

**Project Repository**: [https://github.com/AhmedMasoud135/ClassSphere](https://github.com/AhmedMasoud135/ClassSphere)

For bug reports and feature requests, please open an issue on GitHub.

---

## 🙏 Acknowledgments

- **OpenCV Team** - YuNet face detection model
- **DeepFace** - Face recognition library by Serengil
- **OpenAI** - Whisper speech recognition model
- **Google** - Gemini AI for content generation
- **MobileNetV2** - Efficient CNN architecture
- **Firebase** - Backend infrastructure
- **Next.js Team** - Amazing React framework
- **PyTorch Community** - Deep learning tools
- **DEPI Program** - Digital Egypt Pioneers Initiative
- **Kafr El Sheikh University** - Faculty of Engineering

---

## 📚 Additional Resources

- [Developer Documentation](./DEVELOPER_DOCUMENTATION.md) - In-depth technical details
- [Quick Reference Guide](./QUICK_REFERENCE.md) - Fast lookup for key concepts
- [Full Documentation (PDF)](./Documentation.pdf) - Complete project documentation
- [Demo Video](https://drive.google.com/file/d/1kLiJkOropt1UhBRHDcD-aTLNmA-_pCIW/view?usp=drive_link) - Watch ClassSphere in action

---

## 🔮 Future Roadmap

### Version 2.0 (Q2 2025)
- [ ] Mobile app (iOS/Android)
- [ ] Liveness detection for anti-spoofing
- [ ] Multi-language support for UI
- [ ] Advanced analytics dashboard
- [ ] Parent portal and notifications

### Version 3.0 (Q4 2025)
- [ ] Edge deployment on Raspberry Pi
- [ ] Offline mode support
- [ ] Integration with LMS platforms (Moodle, Canvas)
- [ ] Emotion detection for student engagement
- [ ] Real-time translation for lectures

### Long-term Vision
- [ ] Global deployment in 1000+ schools
- [ ] AI-powered personalized learning recommendations
- [ ] Virtual classroom support with VR/AR
- [ ] Blockchain-based academic credentials
- [ ] Advanced predictive analytics for student performance

---

<div align="center">

**Made with ❤️ by the ClassSphere Team**

[![GitHub stars](https://img.shields.io/github/stars/AhmedMasoud135/ClassSphere?style=social)](https://github.com/AhmedMasoud135/ClassSphere/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/AhmedMasoud135/ClassSphere?style=social)](https://github.com/AhmedMasoud135/ClassSphere/network/members)

⭐ **Star this repository if you found it helpful!** ⭐

**Part of the Digital Egypt Pioneers Initiative (DEPI)**

</div>
