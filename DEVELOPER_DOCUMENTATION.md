# ClassSphere - Developer Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Architecture](#architecture)
4. [Getting Started](#getting-started)
5. [Frontend Structure](#frontend-structure)
6. [Backend Services](#backend-services)
7. [Key Features](#key-features)
8. [API Documentation](#api-documentation)
9. [Database Schema](#database-schema)
10. [Deployment](#deployment)
11. [Contributing](#contributing)

---

## Project Overview

**ClassSphere** is a comprehensive classroom management system that combines traditional educational tools with cutting-edge AI technology. The platform offers:

- **Automated Attendance Tracking** using facial recognition
- **Real-time Violence Detection** for classroom safety
- **Class Management** for teachers and students
- **Lesson Summaries** and educational content delivery

### Problem Statement
Traditional classroom management requires manual attendance tracking, lacks real-time safety monitoring, and provides limited analytics. ClassSphere automates these processes using AI.

### Solution
An integrated platform combining:
- Face recognition for attendance
- Deep learning for violence detection
- Real-time monitoring and alerts
- Seamless user experience

---

## Technology Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 15.5.2 | React framework with SSR/SSG capabilities |
| **React** | 19.1.0 | UI library for component-based architecture |
| **Tailwind CSS** | 4.x | Utility-first CSS framework |
| **Framer Motion** | Latest | Animation library for smooth transitions |
| **Radix UI** | Latest | Headless UI components (Dialog, Accordion, etc.) |
| **Lucide React** | 0.543.0 | Icon library |
| **Firebase SDK** | 12.3.0 | Client-side Firebase integration |

### Backend - Attendance System
| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.12+ | Primary backend language |
| **Flask** | 3.0.3 | Web framework for REST API |
| **OpenCV** | 4.11.0 | Computer vision and face detection |
| **face_recognition** | - | Face encoding and matching |
| **Firebase Admin** | - | Server-side Firebase operations |
| **NumPy** | 2.0.2 | Numerical computations |

### Backend - Violence Detection
| Technology | Version | Purpose |
|------------|---------|---------|
| **PyTorch** | 2.9.0 | Deep learning framework |
| **TorchVision** | 0.24.0 | Pre-trained models and transforms |
| **Albumentations** | 2.0.8 | Image augmentation library |
| **MobileNetV2** | - | Feature extraction CNN |
| **LSTM** | - | Sequence modeling for temporal analysis |
| **Flask-CORS** | 6.0.1 | Cross-Origin Resource Sharing |

### Database & Storage
| Technology | Purpose |
|------------|---------|
| **Firebase Firestore** | NoSQL document database |
| **Firebase Storage** | Image and file storage |
| **Firebase Authentication** | User authentication and authorization |

### AI/ML Models
| Model | Architecture | Purpose |
|-------|--------------|---------|
| **YuNet** | Face Detection | Detects faces in images |
| **Face Recognition** | ResNet-based | Generates 128-dimensional face encodings |
| **Violence Detection** | MobileNetV2 + Bi-LSTM | Classifies video sequences as violent/non-violent |

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Client Browser                          │
│                     (Next.js Frontend)                       │
│  - React Components                                          │
│  - Firebase Auth                                             │
│  - Real-time Camera Access                                   │
└──────────────┬──────────────────────────────┬────────────────┘
               │                              │
               │ HTTP/HTTPS                   │ WebSocket (Firebase)
               │                              │
       ┌───────▼────────┐            ┌────────▼──────────┐
       │  Flask Backend  │            │  Firebase Cloud   │
       │   (Port 5000)   │            │   - Firestore     │
       │  - Attendance   │◄───────────┤   - Storage       │
       │  - Face Recog   │            │   - Auth          │
       └────────────────┘            └───────────────────┘
               │
       ┌───────▼────────┐
       │  Flask Backend  │
       │   (Port 5001)   │
       │  - Violence     │
       │    Detection    │
       └────────────────┘
               │
       ┌───────▼────────┐
       │  ML Models      │
       │  - MobileNetV2  │
       │  - BiLSTM       │
       │  - YuNet        │
       └────────────────┘
```

### Data Flow

#### Attendance System Flow
```
1. Student enters classroom
2. Camera captures video feed
3. Frontend sends frames to Flask (port 5000)
4. YuNet detects faces in frame
5. Face recognition generates encodings
6. Match encodings against enrolled students
7. Draw bounding boxes with names
8. Send results back to frontend
9. Update attendance in Firestore
10. Real-time UI update via Firebase listeners
```

#### Violence Detection Flow
```
1. Teacher activates monitoring
2. Camera streams to frontend
3. Frontend sends frames every 1 second to Flask (port 5001)
4. Frames accumulate in buffer (16 frames required)
5. MobileNetV2 extracts features from each frame
6. BiLSTM analyzes temporal sequence
7. Sigmoid outputs violence probability
8. If threshold exceeded, alert triggered
9. Results displayed in real-time
10. Alert history maintained
```

---

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.12+
- Git
- Firebase Account
- Webcam/Camera

### Installation

#### 1. Clone Repository
```bash
git clone https://github.com/AhmedMasoud135/ClassSphere.git
cd ClassSphere
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
```

Create `.env.local`:
```env
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_domain
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_bucket
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
```

#### 3. Attendance Backend Setup
```bash
cd ../ai-backend-attendance
pip install -r requirements.txt
```

Add `firebase_config.py` with your service account credentials.

#### 4. Violence Detection Backend Setup
```bash
cd ../ai-backend-violence
pip install -r requirements.txt
```

Ensure `best_model.pth` is in the directory.

#### 5. Run All Services

**Terminal 1 - Frontend:**
```bash
cd frontend
npm run dev
# Runs on http://localhost:3000
```

**Terminal 2 - Attendance Backend:**
```bash
cd ai-backend-attendance
python app.py
# Runs on http://localhost:5000
```

**Terminal 3 - Violence Backend:**
```bash
cd ai-backend-violence
python app.py
# Runs on http://localhost:5001
```

---

## Frontend Structure

### Directory Organization
```
frontend/
├── app/                          # Next.js App Router
│   ├── globals.css              # Global styles
│   ├── layout.js                # Root layout
│   ├── page.js                  # Home page
│   ├── components/              # Shared components
│   │   ├── Header.js           # Navigation header
│   │   └── Spinner.js          # Loading spinner
│   ├── context/                 # React Context
│   │   └── AuthContext.js      # Authentication state
│   ├── login/                   # Login page
│   ├── student/                 # Student portal
│   │   ├── dashboard/          # Student dashboard
│   │   └── class/[classId]/    # Student class view
│   └── teacher/                 # Teacher portal
│       ├── dashboard/          # Teacher dashboard
│       └── class/[classId]/    # Teacher class management
│           ├── page.js         # Class overview
│           ├── students/       # Student management
│           ├── attendance/     # Attendance tracking
│           └── violence/       # Violence detection
├── components/                   # UI Components (shadcn/ui)
│   └── ui/
│       ├── button.jsx
│       ├── card.jsx
│       ├── dialog.jsx
│       └── ...
├── lib/                         # Utility libraries
│   ├── firebase.js             # Firebase configuration
│   └── utils.js                # Helper functions
└── public/                      # Static assets
```

### Key Frontend Concepts

#### 1. Server Components vs Client Components
```javascript
// Server Component (default in Next.js 13+)
export default function ServerPage() {
  // Runs on server, no interactivity
}

// Client Component (requires 'use client')
'use client';
export default function ClientPage() {
  // Runs in browser, can use hooks
}
```

#### 2. Firebase Integration
```javascript
// lib/firebase.js
import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';
import { getAuth } from 'firebase/auth';

const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);
export const auth = getAuth(app);
```

#### 3. Real-time Data Listeners
```javascript
// Real-time updates from Firestore
const unsubscribe = onSnapshot(query, (snapshot) => {
  const data = snapshot.docs.map(doc => ({
    id: doc.id,
    ...doc.data()
  }));
  setData(data);
});

// Cleanup on unmount
return () => unsubscribe();
```

#### 4. Dynamic Routes
```javascript
// app/teacher/class/[classId]/page.js
import { useParams } from 'next/navigation';

export default function ClassPage() {
  const params = useParams();
  const classId = params.classId; // Extract from URL
}
```

---

## Backend Services

### Attendance Service (Port 5000)

#### Core Components

**1. Face Detection**
```python
# face_detection_yunet_2023mar.onnx
detector = cv2.FaceDetectorYN.create(
    model='face_detection_yunet_2023mar.onnx',
    config='',
    input_size=(320, 320),
    score_threshold=0.6
)
```

**2. Face Encoding**
```python
import face_recognition

# Generate 128-dimensional encoding
encoding = face_recognition.face_encodings(
    face_image, 
    known_face_locations=[(top, right, bottom, left)]
)
```

**3. Face Matching**
```python
# Compare faces using Euclidean distance
matches = face_recognition.compare_faces(
    known_encodings,
    test_encoding,
    tolerance=0.6  # Lower = stricter
)
```

#### API Endpoints

**POST /start_session**
```json
Request:
{
  "classId": "abc123"
}

Response:
{
  "status": "success",
  "message": "Session started"
}
```

**POST /recognize_image**
```json
Request:
{
  "image": "data:image/jpeg;base64,...",
  "classId": "abc123"
}

Response:
{
  "status": "success",
  "results": [
    {
      "name": "student_uid",
      "confidence": 0.85,
      "bounding_box": [x, y, w, h]
    }
  ]
}
```

**POST /stop_session**
```json
Request:
{
  "classId": "abc123"
}

Response:
{
  "status": "success",
  "records_saved": 5,
  "total_students": 10,
  "timestamp": "2025-10-21T10:30:00Z"
}
```

### Violence Detection Service (Port 5001)

#### Model Architecture

```python
class ViolenceDetectionModel(nn.Module):
    def __init__(self):
        # Feature Extractor: MobileNetV2
        self.cnn = mobilenet_v2(pretrained=True)
        self.cnn.classifier = nn.Identity()  # Remove classifier
        
        # Temporal Analysis: Bidirectional LSTM
        self.lstm = nn.LSTM(
            input_size=1280,      # MobileNetV2 output
            hidden_size=256,
            num_layers=1,
            bidirectional=True
        )
        
        # Classification Head
        self.fc = nn.Linear(512, 1)  # 256*2 for bidirectional
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        # x shape: (batch, sequence, channels, height, width)
        b, s, c, h, w = x.size()
        
        # Extract features for each frame
        x = x.view(b * s, c, h, w)
        features = self.cnn(x)  # (b*s, 1280)
        features = features.view(b, s, -1)  # (b, s, 1280)
        
        # Temporal modeling
        lstm_out, _ = self.lstm(features)  # (b, s, 512)
        
        # Use last timestep
        out = self.fc(lstm_out[:, -1, :])  # (b, 1)
        return self.sigmoid(out)
```

#### Why This Architecture?

1. **MobileNetV2**: Lightweight CNN, efficient for real-time processing
2. **LSTM**: Captures temporal dependencies across frames
3. **Bidirectional**: Learns context from both past and future frames
4. **Sequence Length = 16**: Optimal balance between context and speed

#### Data Preprocessing

```python
import albumentations as A

transform = A.Compose([
    A.Resize(224, 224),                    # MobileNet input size
    A.Normalize(
        mean=(0.485, 0.456, 0.406),       # ImageNet statistics
        std=(0.229, 0.224, 0.225)
    ),
    ToTensorV2()
])
```

#### API Endpoints

**POST /detect_frame**
```json
Request:
{
  "image": "data:image/jpeg;base64,...",
  "classId": "abc123"
}

Response (Collecting):
{
  "status": "waiting",
  "message": "Collecting frames... (5/16)",
  "buffer_size": 5
}

Response (Ready):
{
  "status": "success",
  "prediction": "Violence",
  "probability": 0.8534
}
```

**POST /reset_buffer**
```json
Request:
{
  "classId": "abc123"
}

Response:
{
  "status": "success",
  "message": "Buffer reset successfully"
}
```

---

## Key Features

### 1. Automated Attendance System

**How It Works:**
1. Teacher starts an attendance session
2. System captures video feed at 3-second intervals
3. YuNet detects all faces in frame
4. Face recognition matches against enrolled students
5. Bounding boxes drawn with student names
6. Attendance recorded in Firestore with timestamp
7. Real-time updates shown to teacher

**Accuracy Factors:**
- Lighting conditions
- Face angle (frontal works best)
- Distance from camera (2-6 feet optimal)
- Image quality
- Enrolled face quality

**Threshold Tuning:**
```python
# Lower = stricter matching, fewer false positives
# Higher = looser matching, more false positives
RECOGNITION_TOLERANCE = 0.6  # Default: 0.6
```

### 2. Violence Detection System

**How It Works:**
1. System collects 16 consecutive frames (sequence)
2. Each frame processed by MobileNetV2 → 1280-dim features
3. LSTM analyzes temporal patterns across sequence
4. Output: probability of violence (0.0 - 1.0)
5. If probability > threshold (0.5), alert triggered
6. New frames continuously added to sliding window

**Model Training (for reference):**
- Dataset: Violence/Non-violence video clips
- Training: Cross-entropy loss, Adam optimizer
- Validation: Accuracy, Precision, Recall, F1-Score
- Best model saved based on validation loss

**Performance Metrics:**
- **Latency**: ~1-2 seconds per prediction
- **Throughput**: 1 FPS (frame per second)
- **Accuracy**: Depends on training data quality
- **Hardware**: GPU accelerated (if available)

### 3. Real-time Communication

**Firebase Firestore Listeners:**
```javascript
// Subscribe to real-time updates
const q = query(
  collection(db, 'attendance'),
  where('classId', '==', classId),
  orderBy('timestamp', 'desc')
);

const unsubscribe = onSnapshot(q, (snapshot) => {
  snapshot.docChanges().forEach((change) => {
    if (change.type === 'added') {
      // New attendance record
    }
    if (change.type === 'modified') {
      // Updated record
    }
  });
});
```

---

## Database Schema

### Firestore Collections

#### users
```javascript
{
  uid: "firebase_uid",
  fullName: "John Doe",
  email: "john@example.com",
  role: "teacher" | "student",
  createdAt: Timestamp
}
```

#### classes
```javascript
{
  classId: "auto_generated_id",
  className: "Math 101",
  teacherId: "teacher_uid",
  studentIds: ["student_uid1", "student_uid2", ...],
  createdAt: Timestamp
}
```

#### attendance
```javascript
{
  attendanceId: "auto_generated_id",
  classId: "class_id",
  studentId: "student_uid",
  timestamp: Timestamp,
  status: "present" | "absent",
  confidence: 0.85  // Face recognition confidence
}
```

#### summaries
```javascript
{
  summaryId: "auto_generated_id",
  classId: "class_id",
  teacherId: "teacher_uid",
  title: "Chapter 5: Algebra",
  content: "Lesson summary text...",
  createdAt: Timestamp
}
```

### Firebase Storage Structure
```
storage/
├── Images/
│   ├── {studentUid}/
│   │   ├── image1.jpg
│   │   ├── image2.jpg
│   │   └── image3.jpg
│   └── {studentUid2}/
│       └── ...
└── encodings/
    └── {classId}_encodings.pkl  # Cached encodings
```

---

## API Documentation

### Authentication

All protected routes require Firebase Authentication token:

```javascript
// Frontend
const token = await user.getIdToken();

fetch('http://localhost:5000/endpoint', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

```python
# Backend (if implementing auth)
from firebase_admin import auth

def verify_token(token):
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except:
        return None
```

### Error Handling

**Standard Error Response:**
```json
{
  "status": "error",
  "message": "Descriptive error message",
  "code": "ERROR_CODE"
}
```

**Common Status Codes:**
- `200`: Success
- `400`: Bad Request (missing parameters)
- `401`: Unauthorized (invalid token)
- `404`: Resource Not Found
- `500`: Internal Server Error

---

## Deployment

### Frontend (Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel
```

**Environment Variables:**
Set all `NEXT_PUBLIC_*` variables in Vercel dashboard.

### Backend (Render/Heroku/AWS)

**Requirements:**
- Python 3.12+ runtime
- Sufficient memory for ML models (2GB+ recommended)
- Persistent storage for model files

**Dockerfile Example:**
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

### Production Considerations

1. **Security:**
   - Enable HTTPS
   - Implement rate limiting
   - Validate all inputs
   - Sanitize file uploads
   - Use environment variables

2. **Performance:**
   - Use GPU for violence detection
   - Implement caching for face encodings
   - Optimize image compression
   - Use CDN for static assets

3. **Scalability:**
   - Load balancing for multiple backends
   - Database indexing
   - Horizontal scaling with containerization
   - Queue systems for async processing

4. **Monitoring:**
   - Error tracking (Sentry)
   - Performance monitoring
   - Usage analytics
   - Alert systems

---

## Contributing

### Development Workflow

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -m 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit Pull Request

### Code Standards

**Frontend:**
- Use ESLint configuration
- Follow React best practices
- Use TypeScript (if migrating)
- Component-driven architecture

**Backend:**
- Follow PEP 8 style guide
- Type hints for functions
- Docstrings for all classes/functions
- Unit tests for critical functions

### Testing

**Frontend:**
```bash
npm run test
npm run lint
```

**Backend:**
```bash
pytest tests/
python -m pylint app.py
```

---

## Troubleshooting

### Common Issues

**1. Camera Not Accessible**
- Check browser permissions
- Ensure HTTPS (required for getUserMedia)
- Try different browsers

**2. Face Recognition Not Working**
- Verify encoding files exist
- Check image quality
- Adjust tolerance threshold
- Ensure proper lighting

**3. Violence Detection Slow**
- Use GPU if available
- Reduce frame resolution
- Increase frame interval
- Optimize model (quantization)

**4. Firebase Connection Issues**
- Verify API keys
- Check Firestore rules
- Ensure network connectivity
- Validate service account

---

## Performance Optimization

### Frontend Optimizations

1. **Image Optimization:**
```javascript
import Image from 'next/image';

<Image 
  src={imageUrl} 
  width={500} 
  height={300}
  loading="lazy"
  quality={75}
/>
```

2. **Code Splitting:**
```javascript
const HeavyComponent = dynamic(
  () => import('./HeavyComponent'),
  { loading: () => <Spinner /> }
);
```

3. **Memoization:**
```javascript
const memoizedValue = useMemo(
  () => computeExpensiveValue(a, b),
  [a, b]
);
```

### Backend Optimizations

1. **Caching Face Encodings:**
```python
import pickle

# Save encodings
with open('encodings.pkl', 'wb') as f:
    pickle.dump(encodings, f)

# Load encodings
with open('encodings.pkl', 'rb') as f:
    encodings = pickle.load(f)
```

2. **Batch Processing:**
```python
# Process multiple frames at once
features = model.extract_features(frames)  # GPU accelerated
```

3. **Model Quantization:**
```python
# Reduce model size and increase speed
quantized_model = torch.quantization.quantize_dynamic(
    model, {nn.Linear}, dtype=torch.qint8
)
```

---

## Security Best Practices

1. **Never commit sensitive data:**
   - Use `.env` files
   - Add `.env` to `.gitignore`
   - Use secrets management services

2. **Input Validation:**
```python
def validate_image(image_data):
    if not image_data.startswith('data:image'):
        raise ValueError('Invalid image format')
    # Additional validation...
```

3. **Firestore Security Rules:**
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read: if request.auth != null;
      allow write: if request.auth.uid == userId;
    }
    match /classes/{classId} {
      allow read: if request.auth != null;
      allow write: if resource.data.teacherId == request.auth.uid;
    }
  }
}
```

---

## License

This project is licensed under the MIT License.

---

## Support

For questions or issues:
- GitHub Issues: [Create an issue](https://github.com/AhmedMasoud135/ClassSphere/issues)
- Email: support@classsphere.com
- Documentation: [Read the docs](https://docs.classsphere.com)

---

## Acknowledgments

- YuNet Face Detection Model
- MobileNetV2 (ImageNet pretrained)
- Firebase Platform
- Next.js Team
- PyTorch Community

---

**Last Updated:** October 21, 2025
**Version:** 1.0.0
**Maintained by:** ClassSphere Development Team
