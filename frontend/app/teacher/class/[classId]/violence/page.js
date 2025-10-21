// Violence Detection Page with seamless modern UI matching the attendance page
'use client';

import { useState, useEffect, useRef } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft, AlertTriangle, Play, Square, Shield } from 'lucide-react';
import Spinner from '@/app/components/Spinner';
import { motion } from 'framer-motion';

export default function ViolenceDetectionPage() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const intervalRef = useRef(null);

  const [isSessionActive, setIsSessionActive] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [detectionResults, setDetectionResults] = useState([]);
  const [currentPrediction, setCurrentPrediction] = useState(null);
  const [frameCount, setFrameCount] = useState(0);

  const params = useParams();
  const classId = params.classId;

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

  const handleStartSession = async () => {
    setDetectionResults([]);
    setCurrentPrediction(null);
    setFrameCount(0);
    setLoadingMessage('Initializing camera and AI detection...');
    setIsSessionActive(true);

    intervalRef.current = setInterval(async () => {
      if (videoRef.current && canvasRef.current) {
        const video = videoRef.current;
        const canvas = canvasRef.current;
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas
          .getContext('2d')
          .drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
        const imageData = canvas.toDataURL('image/jpeg');

        try {
          const response = await fetch(
            'http://127.0.0.1:5001/detect_frame',
            {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ image: imageData, classId }),
            }
          );
          const data = await response.json();
          
          setFrameCount(prev => prev + 1);
          
          if (data.status === 'success') {
            setCurrentPrediction({
              prediction: data.prediction,
              probability: data.probability,
              timestamp: new Date().toLocaleTimeString()
            });
            
            // Add to results if violence detected
            if (data.prediction === 'Violence') {
              setDetectionResults((prev) => [
                {
                  timestamp: new Date().toLocaleTimeString(),
                  probability: data.probability,
                  prediction: data.prediction
                },
                ...prev
              ].slice(0, 10)); // Keep last 10 detections
            }
          } else if (data.status === 'waiting') {
            setLoadingMessage(data.message || 'Collecting frames...');
          }
        } catch (error) {
          console.error('Detection error:', error);
        }
      }
    }, 1000); // Send frame every second
  };

  const handleStopSession = async () => {
    setLoadingMessage('Stopping session...');
    if (intervalRef.current) clearInterval(intervalRef.current);

    try {
      const response = await fetch('http://127.0.0.1:5001/reset_buffer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ classId }),
      });
      await response.json();
    } catch (error) {
      console.error('Failed to reset buffer:', error);
    }

    setIsSessionActive(false);
    setLoadingMessage('');
  };

  const getStatusColor = () => {
    if (!currentPrediction) return 'bg-gray-100 border-gray-300';
    return currentPrediction.prediction === 'Violence' 
      ? 'bg-red-100 border-red-300' 
      : 'bg-green-100 border-green-300';
  };

  const getStatusIcon = () => {
    if (!currentPrediction) return <Shield className="h-5 w-5 text-gray-500" />;
    return currentPrediction.prediction === 'Violence'
      ? <AlertTriangle className="h-5 w-5 text-red-600" />
      : <Shield className="h-5 w-5 text-green-600" />;
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
          Violence Detection
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
          <canvas ref={canvasRef} style={{ display: 'none' }} />
          
          {/* Current Status Overlay */}
          {isSessionActive && currentPrediction && (
            <div className={`absolute top-4 right-4 ${getStatusColor()} px-4 py-3 rounded-xl border-2 shadow-lg`}>
              <div className="flex items-center gap-2">
                {getStatusIcon()}
                <div>
                  <div className="font-semibold text-sm">
                    {currentPrediction.prediction}
                  </div>
                  <div className="text-xs">
                    {(currentPrediction.probability * 100).toFixed(1)}% confidence
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {isSessionActive && (
            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-2 bg-black/60 text-white px-4 py-2 rounded-full">
              <Spinner /> 
              <span>{loadingMessage || `Analyzing... (${frameCount} frames processed)`}</span>
            </div>
          )}
        </motion.div>

        {/* Detection Results */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Card className="shadow-lg border border-gray-200 rounded-2xl">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-gray-800">
                Violence Alerts ({detectionResults.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isSessionActive && detectionResults.length === 0 && (
                <p className="text-sm text-gray-500">
                  Monitoring for violence...
                </p>
              )}
              
              {!isSessionActive && detectionResults.length === 0 && (
                <p className="text-sm text-gray-500">
                  Start a session to begin monitoring
                </p>
              )}
              
              <ul className="space-y-2 max-h-96 overflow-y-auto">
                {detectionResults.map((result, index) => (
                  <li
                    key={index}
                    className="flex items-start p-3 bg-red-50 rounded-lg border border-red-200"
                  >
                    <AlertTriangle className="h-5 w-5 mr-2 text-red-600 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <div className="font-medium text-red-700">
                        {result.prediction}
                      </div>
                      <div className="text-xs text-gray-600">
                        {result.timestamp}
                      </div>
                      <div className="text-xs text-gray-600">
                        Confidence: {(result.probability * 100).toFixed(1)}%
                      </div>
                    </div>
                  </li>
                ))}
              </ul>

              {detectionResults.length > 0 && (
                <div className="mt-6 p-4 bg-indigo-50 rounded-xl border border-indigo-200">
                  <h3 className="font-semibold text-indigo-700">
                    Session Summary
                  </h3>
                  <p className="text-sm text-gray-600">
                    Total alerts: {detectionResults.length}
                  </p>
                  <p className="text-sm text-gray-600">
                    Frames processed: {frameCount}
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
          <Play className="h-5 w-5" /> Start Monitoring
        </Button>
        <Button
          size="lg"
          variant="destructive"
          onClick={handleStopSession}
          disabled={!isSessionActive}
          className="flex items-center gap-2"
        >
          <Square className="h-5 w-5" /> Stop Monitoring
        </Button>
      </div>
    </motion.div>
  );
}
