'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/app/context/AuthContext';
import { db } from '@/lib/firebase';
import {
  collection,
  query,
  where,
  onSnapshot,
  orderBy,
  doc,
  getDoc,
  addDoc,
  updateDoc,
} from 'firebase/firestore';
import { useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Upload, 
  FileAudio, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  FileText,
  BookOpen,
  ClipboardList
} from 'lucide-react';
import { motion } from 'framer-motion';
import Spinner from '@/app/components/Spinner';

export default function TeacherSessionsPage() {
  const { user } = useAuth();
  const params = useParams();
  const classId = params.classId;

  const [classData, setClassData] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploadingSessionId, setUploadingSessionId] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [newSessionName, setNewSessionName] = useState('');
  const [uploadProgress, setUploadProgress] = useState('');

  useEffect(() => {
    if (!user || !classId) return;

    const fetchClassData = async () => {
      try {
        const classDocRef = doc(db, 'classes', classId);
        const docSnap = await getDoc(classDocRef);
        if (docSnap.exists()) {
          setClassData({ id: docSnap.id, ...docSnap.data() });
        }
      } catch (error) {
        console.error('Error fetching class data:', error);
      }
    };

    fetchClassData();

    const q = query(
      collection(db, 'sessions'),
      where('classId', '==', classId)
    );

    const unsubscribe = onSnapshot(q, (querySnapshot) => {
      const sessionsData = querySnapshot.docs.map((doc) => ({
        id: doc.id,
        ...doc.data(),
      }))
      .sort((a, b) => new Date(b.startTime) - new Date(a.startTime)); // Client-side sorting
      
      setSessions(sessionsData);
      setLoading(false);
    });

    return () => unsubscribe();
  }, [user, classId]);

  const handleCreateSession = async (e) => {
    e.preventDefault();
    if (!newSessionName.trim()) return;

    try {
      const sessionId = `${classId}_session_${Date.now()}`;
      await addDoc(collection(db, 'sessions'), {
        sessionId,
        sessionName: newSessionName,
        classId,
        teacherId: user.uid,
        startTime: new Date().toISOString(),
        endTime: new Date().toISOString(),
        processingStatus: 'pending',
        audioProcessed: false,
        createdAt: new Date(),
      });

      setNewSessionName('');
      setIsDialogOpen(false);
    } catch (error) {
      console.error('Error creating session:', error);
      alert('Failed to create session');
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file && (file.type === 'audio/mpeg' || file.type === 'audio/wav' || file.type === 'audio/mp3')) {
      setSelectedFile(file);
    } else {
      alert('Please select a valid audio file (MP3 or WAV)');
    }
  };

  const handleUploadAudio = async (sessionId) => {
    if (!selectedFile) {
      alert('Please select an audio file first');
      return;
    }

    setUploadingSessionId(sessionId);
    setUploadProgress('Uploading audio file...');

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('sessionId', sessionId);
    formData.append('classId', classId);

    try {
      // Update Firestore to show processing status
      const sessionRef = doc(db, 'sessions', sessions.find(s => s.sessionId === sessionId)?.id);
      await updateDoc(sessionRef, {
        processingStatus: 'processing',
      });

      setUploadProgress('Processing audio (this may take a few minutes)...');

      const response = await fetch('http://localhost:5001/process-session-audio', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (data.success) {
        setUploadProgress('Processing complete! ✅');
        // Update session with processing results
        await updateDoc(sessionRef, {
          audioProcessed: true,
          processingStatus: 'completed',
          transcriptId: data.transcriptId,
          summaryId: data.summaryId,
          quizId: data.quizId,
        });

        setTimeout(() => {
          setUploadingSessionId(null);
          setSelectedFile(null);
          setUploadProgress('');
        }, 2000);
      } else {
        throw new Error(data.error || 'Processing failed');
      }
    } catch (error) {
      console.error('Error uploading audio:', error);
      setUploadProgress('');
      alert(`Failed to process audio: ${error.message}`);
      
      // Update status to failed
      const sessionRef = doc(db, 'sessions', sessions.find(s => s.sessionId === sessionId)?.id);
      await updateDoc(sessionRef, {
        processingStatus: 'failed',
      });
      
      setUploadingSessionId(null);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return <Badge className="bg-green-500"><CheckCircle className="mr-1 h-3 w-3" /> Completed</Badge>;
      case 'processing':
        return <Badge className="bg-blue-500"><Clock className="mr-1 h-3 w-3" /> Processing</Badge>;
      case 'failed':
        return <Badge className="bg-red-500"><AlertCircle className="mr-1 h-3 w-3" /> Failed</Badge>;
      default:
        return <Badge className="bg-gray-500"><Clock className="mr-1 h-3 w-3" /> Pending</Badge>;
    }
  };

  if (loading) return <Spinner />;

  return (
    <main className="min-h-screen bg-gradient-to-br from-indigo-100 via-white to-pink-100 p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-6xl mx-auto space-y-8"
      >
        <div className="flex justify-between items-center bg-white/80 backdrop-blur-lg shadow-md rounded-2xl p-6 border border-indigo-100">
          <div>
            <h1 className="text-3xl font-extrabold bg-gradient-to-r from-indigo-600 to-pink-600 bg-clip-text text-transparent">
              Session Management
            </h1>
            <p className="text-gray-600 mt-1">{classData?.className}</p>
          </div>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button className="rounded-xl bg-gradient-to-r from-indigo-500 to-pink-500 hover:from-indigo-600 hover:to-pink-600 text-white shadow-md">
                Create New Session
              </Button>
            </DialogTrigger>
            <DialogContent className="rounded-2xl">
              <DialogHeader>
                <DialogTitle className="text-xl font-semibold text-indigo-700">
                  Create New Session
                </DialogTitle>
              </DialogHeader>
              <form onSubmit={handleCreateSession} className="space-y-4">
                <div className="grid gap-2">
                  <Label htmlFor="sessionName">Session Name</Label>
                  <Input
                    id="sessionName"
                    value={newSessionName}
                    onChange={(e) => setNewSessionName(e.target.value)}
                    placeholder="e.g., Lecture 1: Introduction to React"
                  />
                </div>
                <Button
                  type="submit"
                  className="w-full bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl"
                >
                  Create Session
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        <div className="grid gap-6">
          {sessions.map((session) => (
            <Card key={session.id} className="border border-indigo-100 shadow-md">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-xl text-indigo-700">
                      {session.sessionName}
                    </CardTitle>
                    <CardDescription className="mt-1">
                      {new Date(session.startTime).toLocaleString()}
                    </CardDescription>
                  </div>
                  {getStatusBadge(session.processingStatus)}
                </div>
              </CardHeader>
              <CardContent>
                {!session.audioProcessed && session.processingStatus !== 'processing' && (
                  <div className="space-y-4">
                    <div className="flex items-center gap-4">
                      <Input
                        type="file"
                        accept="audio/mpeg,audio/wav,audio/mp3"
                        onChange={handleFileSelect}
                        disabled={uploadingSessionId === session.sessionId}
                        className="flex-1"
                      />
                      <Button
                        onClick={() => handleUploadAudio(session.sessionId)}
                        disabled={!selectedFile || uploadingSessionId === session.sessionId}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white"
                      >
                        <Upload className="mr-2 h-4 w-4" />
                        Upload Audio
                      </Button>
                    </div>
                    {uploadingSessionId === session.sessionId && (
                      <div className="text-sm text-indigo-600 flex items-center gap-2">
                        <Clock className="h-4 w-4 animate-spin" />
                        {uploadProgress}
                      </div>
                    )}
                  </div>
                )}

                {session.audioProcessed && session.processingStatus === 'completed' && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                    <div className="flex items-center gap-3 p-4 bg-green-50 rounded-lg border border-green-200">
                      <FileText className="h-8 w-8 text-green-600" />
                      <div>
                        <p className="font-semibold text-green-900">Transcript</p>
                        <p className="text-xs text-green-700">Available</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
                      <BookOpen className="h-8 w-8 text-blue-600" />
                      <div>
                        <p className="font-semibold text-blue-900">Summary</p>
                        <p className="text-xs text-blue-700">Available</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-4 bg-purple-50 rounded-lg border border-purple-200">
                      <ClipboardList className="h-8 w-8 text-purple-600" />
                      <div>
                        <p className="font-semibold text-purple-900">Quiz</p>
                        <p className="text-xs text-purple-700">Available</p>
                      </div>
                    </div>
                  </div>
                )}

                {session.processingStatus === 'processing' && (
                  <div className="flex items-center justify-center gap-3 p-6 bg-blue-50 rounded-lg">
                    <Clock className="h-6 w-6 text-blue-600 animate-spin" />
                    <p className="text-blue-900 font-medium">
                      Processing audio... This may take a few minutes.
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}

          {sessions.length === 0 && (
            <Card className="border border-dashed border-indigo-300">
              <CardContent className="flex flex-col items-center justify-center py-12">
                <FileAudio className="h-16 w-16 text-indigo-300 mb-4" />
                <p className="text-gray-600 text-center">
                  No sessions created yet. Create your first session to get started!
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </motion.div>
    </main>
  );
}
