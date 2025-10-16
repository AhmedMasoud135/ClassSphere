// Updated AttendancePage with seamless modern UI matching the dashboard and class pages
'use client';

import { useState, useEffect, useRef } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft, UserCheck, Play, Square } from 'lucide-react';
import Spinner from '@/app/components/Spinner';
import { db } from '@/lib/firebase';
import { doc, getDoc } from 'firebase/firestore';
import { motion } from 'framer-motion';

export default function AttendancePage() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const overlayCanvasRef = useRef(null);
  const intervalRef = useRef(null);

  const [isSessionActive, setIsSessionActive] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [finalResult, setFinalResult] = useState(null);
  const [enrolledStudents, setEnrolledStudents] = useState(new Map());
  const [recognizedUIDs, setRecognizedUIDs] = useState([]);

  const params = useParams();
  const classId = params.classId;

  useEffect(() => {
    const fetchEnrolledStudents = async () => {
      if (!classId) return;
      const classDocRef = doc(db, 'classes', classId);
      const classDoc = await getDoc(classDocRef);
      if (classDoc.exists()) {
        const studentUIDs = classDoc.data().studentIds || [];
        const studentMap = new Map();
        for (const uid of studentUIDs) {
          const userDoc = await getDoc(doc(db, 'users', uid));
          if (userDoc.exists()) {
            studentMap.set(uid, userDoc.data().fullName);
          }
        }
        setEnrolledStudents(studentMap);
      }
    };
    fetchEnrolledStudents();
  }, [classId]);

  useEffect(() => {
    let stream = null;
    const startCamera = async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) videoRef.current.srcObject = stream;
      } catch (err) {
        console.error('Error accessing the camera: ', err);
      }
    };
    startCamera();

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (stream) stream.getTracks().forEach((track) => track.stop());
    };
  }, []);

  const drawBoundingBoxes = (results) => {
    if (!overlayCanvasRef.current || !videoRef.current) return;
    const canvas = overlayCanvasRef.current;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (!results || results.length === 0) return;

    results.forEach((result) => {
      if (!result.name || result.name.toLowerCase() === 'unknown') return;
      const boundingBox = result.bounding_box || result.bbox;
      if (!boundingBox) return;
      const [x, y, w, h] = boundingBox;
      const confidence = result.confidence || 0;
      const studentName = enrolledStudents.get(result.name) || result.name;

      ctx.strokeStyle = '#4f46e5'; // Indigo color
      ctx.lineWidth = 3;
      ctx.strokeRect(x, y, w, h);

      const text = `${studentName}`;
      const confidenceText = `${(confidence * 100).toFixed(1)}%`;
      ctx.font = 'bold 16px Inter';
      const textWidth = Math.max(
        ctx.measureText(text).width,
        ctx.measureText(confidenceText).width
      );

      ctx.fillStyle = 'rgba(79, 70, 229, 0.85)';
      ctx.fillRect(x, y - 45, textWidth + 20, 40);
      ctx.fillStyle = '#ffffff';
      ctx.fillText(text, x + 10, y - 25);
      ctx.fillText(confidenceText, x + 10, y - 8);
    });
  };

  const handleStartSession = async () => {
    setFinalResult(null);
    setRecognizedUIDs([]);
    setLoadingMessage('Initializing camera and AI recognition...');
    setIsSessionActive(true);

    try {
      await fetch('http://127.0.0.1:5000/start_session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ classId }),
      });
    } catch (error) {
      console.error('Failed to start session:', error);
    }

    intervalRef.current = setInterval(async () => {
      if (videoRef.current && canvasRef.current) {
        const video = videoRef.current;
        const canvas = canvasRef.current;
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        if (overlayCanvasRef.current) {
          overlayCanvasRef.current.width = video.videoWidth;
          overlayCanvasRef.current.height = video.videoHeight;
        }
        canvas
          .getContext('2d')
          .drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
        const imageData = canvas.toDataURL('image/jpeg');

        try {
          const response = await fetch(
            'http://127.0.0.1:5000/recognize_image',
            {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ image: imageData, classId }),
            }
          );
          const data = await response.json();
          if (data.status === 'success' && data.results) {
            drawBoundingBoxes(data.results);
            const uids = data.results
              .filter((r) => r.name && r.name.toLowerCase() !== 'unknown')
              .map((r) => r.name);
            setRecognizedUIDs((prev) =>
              Array.from(new Set([...prev, ...uids]))
            );
          }
        } catch (error) {
          console.error('Recognition error:', error);
        }
      }
    }, 3000);
  };

  const handleStopSession = async () => {
    setLoadingMessage('Stopping session...');
    if (intervalRef.current) clearInterval(intervalRef.current);
    if (overlayCanvasRef.current)
      overlayCanvasRef.current
        .getContext('2d')
        .clearRect(
          0,
          0,
          overlayCanvasRef.current.width,
          overlayCanvasRef.current.height
        );

    try {
      const response = await fetch('http://127.0.0.1:5000/stop_session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ classId }),
      });
      const data = await response.json();
      setFinalResult(data);
    } catch (error) {
      console.error('Failed to stop session:', error);
    }

    setIsSessionActive(false);
    setLoadingMessage('');
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="min-h-screen p-8 bg-gradient-to-br from-indigo-50 via-white to-indigo-100"
    >
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-4xl font-semibold text-gray-800 tracking-tight">
          Live Attendance
        </h1>
        <Link href={`/teacher/class/${classId}`}>
          <Button variant="outline" className="flex items-center gap-2">
            <ArrowLeft className="h-4 w-4" /> Back to Class
          </Button>
        </Link>
      </div>

      <div className="grid md:grid-cols-3 gap-8">
        {/* Video Section */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="md:col-span-2 bg-white rounded-2xl shadow-md overflow-hidden border border-gray-200 relative"
        >
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-auto"
          />
          <canvas
            ref={overlayCanvasRef}
            className="absolute top-0 left-0 w-full h-full pointer-events-none"
          />
          <canvas ref={canvasRef} style={{ display: 'none' }} />
          {isSessionActive && (
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-2 bg-black/60 text-white px-4 py-2 rounded-full">
              <Spinner /> <span>{loadingMessage || 'Recognizing...'}</span>
            </div>
          )}
        </motion.div>

        {/* Recognized Students */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Card className="shadow-lg border border-gray-200 rounded-2xl">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-gray-800">
                Recognized Students ({recognizedUIDs.length} /{' '}
                {enrolledStudents.size})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isSessionActive && recognizedUIDs.length === 0 && (
                <p className="text-sm text-gray-500">
                  Scanning for students...
                </p>
              )}
              <ul className="space-y-2">
                {recognizedUIDs.map((uid) => (
                  <li
                    key={uid}
                    className="flex items-center text-indigo-600 font-medium"
                  >
                    <UserCheck className="h-4 w-4 mr-2" />{' '}
                    {enrolledStudents.get(uid) || uid}
                  </li>
                ))}
              </ul>

              {finalResult && (
                <div className="mt-6 p-4 bg-indigo-50 rounded-xl border border-indigo-200">
                  <h3 className="font-semibold text-indigo-700">
                    Session Complete
                  </h3>
                  <p className="text-sm text-gray-600">{finalResult.message}</p>
                  <p className="text-sm font-semibold text-gray-700">
                    Records saved: {finalResult.records_saved || 0}
                  </p>
                  <p className="text-sm font-semibold text-gray-700">
                    Total students: {finalResult.total_students || 0}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Control Buttons */}
      <div className="mt-8 flex justify-center gap-4">
        <Button
          size="lg"
          onClick={handleStartSession}
          disabled={isSessionActive}
          className="bg-indigo-600 hover:bg-indigo-700 text-white flex items-center gap-2"
        >
          <Play className="h-5 w-5" /> Start Session
        </Button>
        <Button
          size="lg"
          variant="destructive"
          onClick={handleStopSession}
          disabled={!isSessionActive}
          className="flex items-center gap-2"
        >
          <Square className="h-5 w-5" /> Stop Session
        </Button>
      </div>
    </motion.div>
  );
}
