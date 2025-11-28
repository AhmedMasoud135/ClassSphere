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
} from 'firebase/firestore';
import { useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { 
  FileText, 
  BookOpen, 
  ClipboardList,
  CheckCircle,
  XCircle,
  Trophy,
  Clock
} from 'lucide-react';
import { motion } from 'framer-motion';
import Spinner from '@/app/components/Spinner';

export default function StudentSessionsPage() {
  const { user } = useAuth();
  const params = useParams();
  const classId = params.classId;

  const [classData, setClassData] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSession, setSelectedSession] = useState(null);
  const [transcript, setTranscript] = useState('');
  const [summary, setSummary] = useState('');
  const [quiz, setQuiz] = useState(null);
  const [currentAnswers, setCurrentAnswers] = useState({});
  const [quizResult, setQuizResult] = useState(null);
  const [dialogContent, setDialogContent] = useState(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [quizStartTime, setQuizStartTime] = useState(null);
  const [studentAttempts, setStudentAttempts] = useState({});

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
      where('classId', '==', classId),
      where('audioProcessed', '==', true)
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

  // Fetch student attempts
  useEffect(() => {
    const fetchAttempts = async () => {
      if (!user) return;
      try {
        const response = await fetch(`http://localhost:5001/get-student-attempts/${user.uid}`);
        const data = await response.json();
        if (data.success) {
          const attemptsMap = {};
          data.attempts.forEach(attempt => {
            attemptsMap[attempt.sessionId] = attempt;
          });
          setStudentAttempts(attemptsMap);
        }
      } catch (error) {
        console.error('Error fetching attempts:', error);
      }
    };
    fetchAttempts();
  }, [user, quizResult]);

  const viewTranscript = async (session) => {
    try {
      const response = await fetch(`http://localhost:5001/get-session-transcript/${session.sessionId}`);
      const data = await response.json();
      if (data.success) {
        setTranscript(data.transcript);
        setDialogContent('transcript');
        setSelectedSession(session);
        setIsDialogOpen(true);
      }
    } catch (error) {
      console.error('Error fetching transcript:', error);
      alert('Failed to load transcript');
    }
  };

  const viewSummary = async (session) => {
    try {
      const response = await fetch(`http://localhost:5001/get-session-summary/${session.sessionId}`);
      const data = await response.json();
      if (data.success) {
        setSummary(data.summary);
        setDialogContent('summary');
        setSelectedSession(session);
        setIsDialogOpen(true);
      }
    } catch (error) {
      console.error('Error fetching summary:', error);
      alert('Failed to load summary');
    }
  };

  const startQuiz = async (session) => {
    try {
      const response = await fetch(`http://localhost:5001/get-session-quiz/${session.sessionId}`);
      const data = await response.json();
      if (data.success && data.quizData) {
        setQuiz(data.quizData);
        setCurrentAnswers({});
        setQuizResult(null);
        setDialogContent('quiz');
        setSelectedSession(session);
        setQuizStartTime(Date.now());
        setIsDialogOpen(true);
      }
    } catch (error) {
      console.error('Error fetching quiz:', error);
      alert('Failed to load quiz');
    }
  };

  const handleAnswerSelect = (questionId, answer) => {
    setCurrentAnswers({
      ...currentAnswers,
      [questionId]: answer,
    });
  };

  const submitQuiz = async () => {
    if (!quiz || !selectedSession) return;

    const timeSpent = Math.floor((Date.now() - quizStartTime) / 1000);

    try {
      const response = await fetch('http://localhost:5001/submit-quiz', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          quizId: selectedSession.quizId,
          sessionId: selectedSession.sessionId,
          studentId: user.uid,
          classId: classId,
          answers: currentAnswers,
          timeSpent: timeSpent,
        }),
      });

      const data = await response.json();
      if (data.success) {
        setQuizResult(data);
        setDialogContent('result');
      } else {
        alert('Failed to submit quiz: ' + data.error);
      }
    } catch (error) {
      console.error('Error submitting quiz:', error);
      alert('Failed to submit quiz');
    }
  };

  const closeDialog = () => {
    setIsDialogOpen(false);
    setDialogContent(null);
    setSelectedSession(null);
    setTranscript('');
    setSummary('');
    setQuiz(null);
    setCurrentAnswers({});
    setQuizResult(null);
  };

  if (loading) return <Spinner />;

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-6xl mx-auto space-y-8"
      >
        <div className="bg-white/80 backdrop-blur-lg shadow-md rounded-2xl p-6 border border-blue-100">
          <h1 className="text-3xl font-extrabold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Session Materials
          </h1>
          <p className="text-gray-600 mt-1">{classData?.className}</p>
        </div>

        <div className="grid gap-6">
          {sessions.map((session) => {
            const attempt = studentAttempts[session.sessionId];
            return (
              <Card key={session.id} className="border border-blue-100 shadow-md">
                <CardHeader>
                  <CardTitle className="text-xl text-blue-700">
                    {session.sessionName}
                  </CardTitle>
                  <CardDescription>
                    {new Date(session.startTime).toLocaleString()}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Button
                      onClick={() => viewTranscript(session)}
                      className="flex items-center gap-2 bg-green-500 hover:bg-green-600 text-white"
                    >
                      <FileText className="h-4 w-4" />
                      View Transcript
                    </Button>
                    <Button
                      onClick={() => viewSummary(session)}
                      className="flex items-center gap-2 bg-blue-500 hover:bg-blue-600 text-white"
                    >
                      <BookOpen className="h-4 w-4" />
                      View Summary
                    </Button>
                    <div className="relative">
                      <Button
                        onClick={() => startQuiz(session)}
                        className="w-full flex items-center gap-2 bg-purple-500 hover:bg-purple-600 text-white"
                      >
                        <ClipboardList className="h-4 w-4" />
                        Take Quiz
                      </Button>
                      {attempt && (
                        <Badge className="absolute -top-2 -right-2 bg-yellow-500">
                          Score: {attempt.score}%
                        </Badge>
                      )}
                    </div>
                  </div>
                  {attempt && (
                    <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                      <p className="text-sm text-yellow-800">
                        <Trophy className="inline h-4 w-4 mr-1" />
                        Previous attempt: {attempt.correctAnswers}/{attempt.totalQuestions} correct ({attempt.score}%)
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}

          {sessions.length === 0 && (
            <Card className="border border-dashed border-blue-300">
              <CardContent className="flex flex-col items-center justify-center py-12">
                <BookOpen className="h-16 w-16 text-blue-300 mb-4" />
                <p className="text-gray-600 text-center">
                  No session materials available yet. Check back after your next class!
                </p>
              </CardContent>
            </Card>
          )}
        </div>
      </motion.div>

      <Dialog open={isDialogOpen} onOpenChange={closeDialog}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto rounded-2xl">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold text-blue-700">
              {selectedSession?.sessionName}
            </DialogTitle>
          </DialogHeader>

          {dialogContent === 'transcript' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-green-700 flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Full Transcript
              </h3>
              <div className="p-4 bg-gray-50 rounded-lg whitespace-pre-wrap text-sm">
                {transcript}
              </div>
            </div>
          )}

          {dialogContent === 'summary' && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-blue-700 flex items-center gap-2">
                <BookOpen className="h-5 w-5" />
                Session Summary
              </h3>
              <div className="p-4 bg-blue-50 rounded-lg whitespace-pre-wrap">
                {summary}
              </div>
            </div>
          )}

          {dialogContent === 'quiz' && quiz && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-purple-700 flex items-center gap-2">
                  <ClipboardList className="h-5 w-5" />
                  Quiz ({quiz.numberOfQuestions} Questions)
                </h3>
                <Badge className="bg-purple-500">
                  <Clock className="h-3 w-3 mr-1" />
                  Time: {Math.floor((Date.now() - quizStartTime) / 1000)}s
                </Badge>
              </div>

              {quiz.questions?.map((question, index) => (
                <Card key={question.questionId} className="border border-purple-200">
                  <CardHeader>
                    <CardTitle className="text-base">
                      {index + 1}. {question.questionText}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {Object.entries(question.options).map(([key, value]) => (
                      <div
                        key={key}
                        className={`p-3 rounded-lg border-2 cursor-pointer transition ${
                          currentAnswers[question.questionId] === key
                            ? 'border-purple-500 bg-purple-50'
                            : 'border-gray-200 hover:border-purple-300'
                        }`}
                        onClick={() => handleAnswerSelect(question.questionId, key)}
                      >
                        <Label className="cursor-pointer flex items-center gap-2">
                          <input
                            type="radio"
                            name={question.questionId}
                            value={key}
                            checked={currentAnswers[question.questionId] === key}
                            onChange={() => handleAnswerSelect(question.questionId, key)}
                            className="text-purple-500"
                          />
                          <span><strong>{key})</strong> {value}</span>
                        </Label>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              ))}

              <Button
                onClick={submitQuiz}
                disabled={Object.keys(currentAnswers).length !== quiz.questions?.length}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white text-lg py-6"
              >
                Submit Quiz
              </Button>
            </div>
          )}

          {dialogContent === 'result' && quizResult && (
            <div className="space-y-6">
              <div className="text-center p-8 bg-gradient-to-r from-purple-100 to-blue-100 rounded-2xl">
                <Trophy className="h-16 w-16 mx-auto text-yellow-500 mb-4" />
                <h3 className="text-3xl font-bold text-purple-700 mb-2">
                  Quiz Complete!
                </h3>
                <p className="text-5xl font-extrabold text-purple-900 mb-2">
                  {quizResult.score}%
                </p>
                <p className="text-lg text-gray-700">
                  {quizResult.correctAnswers} out of {quizResult.totalQuestions} correct
                </p>
              </div>

              <div className="space-y-4">
                <h4 className="text-lg font-semibold text-gray-800">Answer Review:</h4>
                {quizResult.answerDetails?.map((detail, index) => (
                  <Card
                    key={index}
                    className={`border-2 ${
                      detail.isCorrect ? 'border-green-300 bg-green-50' : 'border-red-300 bg-red-50'
                    }`}
                  >
                    <CardHeader>
                      <CardTitle className="text-base flex items-center gap-2">
                        {detail.isCorrect ? (
                          <CheckCircle className="h-5 w-5 text-green-600" />
                        ) : (
                          <XCircle className="h-5 w-5 text-red-600" />
                        )}
                        {index + 1}. {detail.questionText}
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm">
                        <strong>Your answer:</strong>{' '}
                        <span className={detail.isCorrect ? 'text-green-700' : 'text-red-700'}>
                          {detail.studentAnswer}
                        </span>
                      </p>
                      {!detail.isCorrect && (
                        <p className="text-sm mt-1">
                          <strong>Correct answer:</strong>{' '}
                          <span className="text-green-700">{detail.correctAnswer}</span>
                        </p>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>

              <Button
                onClick={closeDialog}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white"
              >
                Close
              </Button>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </main>
  );
}
