'use client';

import { useState, useEffect, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { db } from '@/lib/firebase';
import { doc, getDoc } from 'firebase/firestore';

import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { ArrowLeft, User, Camera, Plus } from 'lucide-react';
import Spinner from '@/app/components/Spinner';

export default function ManageStudentsPage() {
  const params = useParams();
  const router = useRouter();
  const { classId } = params;

  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const [students, setStudents] = useState([]);
  const [classData, setClassData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Photo capture states
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [capturedPhotos, setCapturedPhotos] = useState([]);
  const [isAddingPhotos, setIsAddingPhotos] = useState(false);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');

  useEffect(() => {
    const fetchStudents = async () => {
      if (!classId) return;

      const classDocRef = doc(db, 'classes', classId);
      const classDocSnap = await getDoc(classDocRef);

      if (classDocSnap.exists()) {
        const classInfo = classDocSnap.data();
        setClassData(classInfo);

        const studentUIDs = classInfo.studentIds || [];
        const studentPromises = studentUIDs.map((uid) =>
          getDoc(doc(db, 'users', uid))
        );
        const studentDocs = await Promise.all(studentPromises);

        const studentsData = studentDocs
          .filter((doc) => doc.exists())
          .map((doc) => ({ id: doc.id, ...doc.data() }));

        setStudents(studentsData);
      }
      setLoading(false);
    };
    fetchStudents();
  }, [classId]);

  useEffect(() => {
    let stream = null;
    const startCamera = async () => {
      if (!isCameraActive) return;
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error('Error accessing the camera: ', err);
        alert('Could not access camera. Please check permissions.');
      }
    };

    if (isCameraActive) {
      startCamera();
    }

    return () => {
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
      }
    };
  }, [isCameraActive]);

  const handleOpenCamera = (student) => {
    setSelectedStudent(student);
    setCapturedPhotos([]);
    setIsCameraActive(true);
  };

  const handleCloseCamera = () => {
    setSelectedStudent(null);
    setCapturedPhotos([]);
    setIsCameraActive(false);
    if (videoRef.current && videoRef.current.srcObject) {
      videoRef.current.srcObject.getTracks().forEach((track) => track.stop());
    }
  };

  const handleCapturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      canvas
        .getContext('2d')
        .drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
      const imageData = canvas.toDataURL('image/jpeg');
      setCapturedPhotos((prev) => [...prev, imageData]);
    }
  };

  const handleAddPhotos = async () => {
    if (!selectedStudent || capturedPhotos.length === 0) {
      alert('Please capture at least one photo');
      return;
    }

    setIsAddingPhotos(true);
    setUploadStatus('Uploading photos...');

    try {
      const response = await fetch('http://127.0.0.1:5000/add_student', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_name: selectedStudent.id,
          images: capturedPhotos,
          class_id: classId,
        }),
      });
      const data = await response.json();

      if (data.status === 'success') {
        setUploadStatus('Photos uploaded! Updating recognition system...');
        const embeddingResponse = await fetch(
          'http://127.0.0.1:5000/update_embeddings',
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
          }
        );

        const embeddingData = await embeddingResponse.json();

        if (embeddingData.status === 'ok') {
          setUploadStatus('Success! Recognition system updated.');
          setTimeout(() => {
            alert(`Photos for ${selectedStudent.fullName} added successfully!`);
            handleCloseCamera();
          }, 1000);
        } else {
          throw new Error('Failed to update embeddings');
        }
      } else {
        throw new Error(data.message || 'Failed to add photos');
      }
    } catch (error) {
      console.error('Error:', error);
      setUploadStatus('');
      alert(`Failed to add photos: ${error.message}`);
    } finally {
      setIsAddingPhotos(false);
    }
  };

  if (loading) return <Spinner />;

  return (
    <div className="p-8 bg-gradient-to-br from-slate-50 via-slate-100 to-slate-200 min-h-screen space-y-6">
      <div className="flex items-center gap-4 mb-6">
        <Button
          variant="outline"
          size="icon"
          onClick={() => router.back()}
          className="shadow-sm"
        >
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <h1 className="text-3xl font-bold text-slate-800 drop-shadow-sm">
          Manage Students for {classData?.className}
        </h1>
      </div>

      <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-md">
        <CardHeader>
          <CardTitle className="text-slate-800">
            Enrolled Students ({students.length})
          </CardTitle>
          <CardDescription>
            Click on &quot;Add Photos&quot; to capture student photos for facial
            recognition.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            {students.length > 0 ? (
              students.map((student) => (
                <div
                  key={student.id}
                  className="flex items-center justify-between p-4 bg-gradient-to-r from-slate-50 to-slate-100 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-slate-200 rounded-full">
                      <User className="h-5 w-5 text-slate-700" />
                    </div>
                    <div>
                      <p className="font-medium text-slate-800">
                        {student.fullName}
                      </p>
                      <p className="text-sm text-slate-500">{student.email}</p>
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleOpenCamera(student)}
                  >
                    <Camera className="h-4 w-4 mr-2" /> Add Photos
                  </Button>
                </div>
              ))
            ) : (
              <p className="text-slate-500">
                No students are enrolled in this class yet.
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      <Dialog
        open={isCameraActive}
        onOpenChange={(open) => !open && handleCloseCamera()}
      >
        <DialogContent className="max-w-4xl bg-white/90 backdrop-blur-md border-0 shadow-2xl">
          <DialogHeader>
            <DialogTitle className="text-slate-800">
              Add Photos for {selectedStudent?.fullName}
            </DialogTitle>
          </DialogHeader>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <div className="w-full bg-slate-900 rounded-xl overflow-hidden shadow-lg relative">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="w-full h-auto"
                />
                <canvas ref={canvasRef} style={{ display: 'none' }} />
              </div>
              <div className="mt-4 flex justify-center gap-4">
                <Button onClick={handleCapturePhoto} disabled={isAddingPhotos}>
                  <Camera className="h-4 w-4 mr-2" /> Capture Photo
                </Button>
                <Button
                  variant="outline"
                  onClick={handleCloseCamera}
                  disabled={isAddingPhotos}
                >
                  Cancel
                </Button>
              </div>
            </div>

            <div>
              <h3 className="font-semibold mb-2 text-slate-800">
                Captured Photos ({capturedPhotos.length})
              </h3>
              <div className="grid grid-cols-2 gap-2 max-h-96 overflow-y-auto mb-4">
                {capturedPhotos.map((photo, idx) => (
                  <img
                    key={idx}
                    src={photo}
                    alt={`Captured ${idx + 1}`}
                    className="w-full h-32 object-cover rounded-lg border border-slate-200"
                  />
                ))}
              </div>
              <p className="text-sm text-slate-600 mb-4">
                Capture 3-5 photos from different angles for better recognition.
              </p>

              {uploadStatus && (
                <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
                  <div className="text-sm text-blue-800 flex items-center gap-2">
                    <Spinner /> {uploadStatus}
                  </div>
                </div>
              )}

              <Button
                className="w-full"
                onClick={handleAddPhotos}
                disabled={isAddingPhotos || capturedPhotos.length === 0}
              >
                {isAddingPhotos ? (
                  <>
                    <Spinner /> Processing...
                  </>
                ) : (
                  <>
                    <Plus className="h-4 w-4 mr-2" /> Save{' '}
                    {capturedPhotos.length} Photo
                    {capturedPhotos.length !== 1 ? 's' : ''}
                  </>
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
