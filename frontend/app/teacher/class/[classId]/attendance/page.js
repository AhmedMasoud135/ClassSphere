'use client';

import { useState, useEffect, useRef } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft, UserCheck } from 'lucide-react';
import Spinner from '@/app/components/Spinner';
import { db } from '@/lib/firebase';
import { doc, getDoc } from 'firebase/firestore';

export default function AttendancePage() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const intervalRef = useRef(null);

  const [isSessionActive, setIsSessionActive] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [finalResult, setFinalResult] = useState(null);
  const [enrolledStudents, setEnrolledStudents] = useState(new Map());
  const [recognizedUIDs, setRecognizedUIDs] = useState([]);

  const params = useParams();
  const classId = params.classId;

  // Fetch enrolled students
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

  // --- THIS IS THE CORRECTED CAMERA LOGIC ---
  useEffect(() => {
    let stream = null; // Use a local variable to hold the stream

    const startCamera = async () => {
      try {
        // Get the stream and assign it to our local variable
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error('Error accessing the camera: ', err);
      }
    };

    startCamera();

    // The cleanup function now uses the local 'stream' variable, which is more reliable
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }
    };
  }, []); // Empty dependency array is correct

  const handleStartSession = async () => {
    setFinalResult(null);
    setRecognizedUIDs([]);
    setLoadingMessage('Starting session...');
    setIsSessionActive(true);
    await fetch('http://127.0.0.1:5001/start', { method: 'POST' });
    intervalRef.current = setInterval(async () => {
      if (videoRef.current && canvasRef.current) {
        setLoadingMessage('Recognizing...');
        const video = videoRef.current;
        const canvas = canvasRef.current;
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas
          .getContext('2d')
          .drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
        const imageData = canvas.toDataURL('image/jpeg');
        const response = await fetch('http://127.0.0.1:5001/recognize', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image: imageData }),
        });
        const data = await response.json();
        setRecognizedUIDs(data.recognized_uids || []);
      }
    }, 3000);
  };

  const handleStopSession = async () => {
    setLoadingMessage('Stopping session...');
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    intervalRef.current = null;
    const response = await fetch('http://127.0.0.1:5001/stop', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ classId: classId }),
    });
    const data = await response.json();
    setFinalResult(data);
    setIsSessionActive(false);
    setLoadingMessage('');
  };

  // The JSX part of your component remains the same
  return (
    <div className="grid md:grid-cols-3 gap-6">
      <div className="md:col-span-2">
        <div className="flex items-center gap-4 mb-4">
          <Link href={`/teacher/class/${classId}`}>
            <Button variant="outline" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <h1 className="text-3xl font-bold">Live Attendance</h1>
        </div>
        <div className="w-full bg-slate-900 rounded-lg overflow-hidden shadow-lg relative">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-auto"
          />
          <canvas ref={canvasRef} style={{ display: 'none' }} />
          {isSessionActive && (
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-2 bg-black/50 text-white px-3 py-1 rounded-full">
              <Spinner /> <span>{loadingMessage}</span>
            </div>
          )}
        </div>
        <div className="mt-6 flex justify-center gap-4">
          <Button
            size="lg"
            onClick={handleStartSession}
            disabled={isSessionActive}
          >
            Start Session
          </Button>
          <Button
            size="lg"
            variant="destructive"
            onClick={handleStopSession}
            disabled={!isSessionActive}
          >
            Stop Session
          </Button>
        </div>
      </div>
      <div className="md:col-span-1">
        <Card>
          <CardHeader>
            <CardTitle>
              Recognized Students ({recognizedUIDs.length} /{' '}
              {enrolledStudents.size})
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isSessionActive && recognizedUIDs.length === 0 && (
              <p className="text-sm text-muted-foreground">
                Scanning for students...
              </p>
            )}
            <ul className="space-y-2">
              {recognizedUIDs.map((uid) => (
                <li
                  key={uid}
                  className="flex items-center text-green-600 font-medium"
                >
                  <UserCheck className="h-4 w-4 mr-2" />
                  {enrolledStudents.get(uid) || 'Unknown Student'}
                </li>
              ))}
            </ul>
            {finalResult && (
              <div className="mt-4 pt-4 border-t">
                <h3 className="font-bold">Session Complete</h3>
                <p className="text-sm text-muted-foreground">
                  {finalResult.message}
                </p>
                <p className="text-sm font-semibold">
                  Total Present:{' '}
                  {finalResult.present_students_uids?.length || 0}
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
