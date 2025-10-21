'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/app/context/AuthContext';
import { db } from '@/lib/firebase';
import {
  doc,
  getDoc,
  collection,
  addDoc,
  query,
  where,
  onSnapshot,
  orderBy,
} from 'firebase/firestore';
import { useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { PlusCircle, Video, Users, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';
import Spinner from '@/app/components/Spinner';

export default function TeacherClassPage() {
  const { user } = useAuth();
  const [classData, setClassData] = useState(null);
  const [summaries, setSummaries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [summaryTitle, setSummaryTitle] = useState('');
  const [summaryContent, setSummaryContent] = useState('');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const params = useParams();
  const classId = params.classId;

  useEffect(() => {
    if (!user || !classId) return;
    let unsubscribe;

    const fetchData = async () => {
      try {
        const classDocRef = doc(db, 'classes', classId);
        const docSnap = await getDoc(classDocRef);

        if (docSnap.exists()) {
          setClassData({ id: docSnap.id, ...docSnap.data() });
        } else {
          console.error('Class not found');
          setLoading(false);
          return;
        }

        const q = query(
          collection(db, 'summaries'),
          where('classId', '==', classId),
          orderBy('createdAt', 'desc')
        );

        unsubscribe = onSnapshot(q, (querySnapshot) => {
          const summariesData = [];
          querySnapshot.forEach((doc) =>
            summariesData.push({ id: doc.id, ...doc.data() })
          );
          setSummaries(summariesData);
          setLoading(false);
        });
      } catch (error) {
        console.error('Error fetching class data:', error);
        setLoading(false);
      }
    };

    fetchData();
    return () => unsubscribe && unsubscribe();
  }, [user, classId]);

  const handleAddSummary = async (e) => {
    e.preventDefault();
    if (!summaryTitle.trim() || !summaryContent.trim()) return;

    try {
      await addDoc(collection(db, 'summaries'), {
        title: summaryTitle,
        content: summaryContent,
        classId: classId,
        teacherId: user.uid,
        createdAt: new Date(),
      });
      setSummaryTitle('');
      setSummaryContent('');
      setIsDialogOpen(false);
    } catch (error) {
      console.error('Error adding summary:', error);
    }
  };

  if (loading) return <Spinner />;

  return (
    <main className="min-h-screen bg-gradient-to-br from-indigo-100 via-white to-pink-100 p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="max-w-5xl mx-auto space-y-8"
      >
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white/80 backdrop-blur-lg shadow-md rounded-2xl p-6 border border-indigo-100">
          <h1 className="text-3xl font-extrabold bg-gradient-to-r from-indigo-600 to-pink-600 bg-clip-text text-transparent">
            {classData?.className}
          </h1>
          <div className="flex flex-wrap gap-3">
            <Link href={`/teacher/class/${classId}/students`}>
              <Button
                variant="outline"
                className="rounded-xl border-2 border-indigo-300 hover:bg-indigo-50"
              >
                <Users className="mr-2 h-4 w-4 text-indigo-600" /> Manage
                Students
              </Button>
            </Link>
            <Link href={`/teacher/class/${classId}/attendance`}>
              <Button
                variant="outline"
                className="rounded-xl border-2 border-pink-300 hover:bg-pink-50"
              >
                <Video className="mr-2 h-4 w-4 text-pink-600" /> Live Attendance
              </Button>
            </Link>
            <Link href={`/teacher/class/${classId}/violence`}>
              <Button
                variant="outline"
                className="rounded-xl border-2 border-red-300 hover:bg-red-50"
              >
                <AlertTriangle className="mr-2 h-4 w-4 text-red-600" /> Violence Detection
              </Button>
            </Link>
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button className="rounded-xl bg-gradient-to-r from-indigo-500 to-pink-500 hover:from-indigo-600 hover:to-pink-600 text-white shadow-md hover:shadow-lg">
                  <PlusCircle className="mr-2 h-4 w-4" /> Add Summary
                </Button>
              </DialogTrigger>
              <DialogContent className="rounded-2xl">
                <DialogHeader>
                  <DialogTitle className="text-xl font-semibold text-indigo-700">
                    Add New Lesson Summary
                  </DialogTitle>
                </DialogHeader>
                <form onSubmit={handleAddSummary} className="space-y-4">
                  <div className="grid gap-2">
                    <Label htmlFor="title">Summary Title</Label>
                    <Input
                      id="title"
                      value={summaryTitle}
                      onChange={(e) => setSummaryTitle(e.target.value)}
                      placeholder="e.g., Chapter 5: Algebra Basics"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="content">Summary Content</Label>
                    <Textarea
                      id="content"
                      value={summaryContent}
                      onChange={(e) => setSummaryContent(e.target.value)}
                      placeholder="Write the lesson summary here..."
                      rows={8}
                    />
                  </div>
                  <Button
                    type="submit"
                    className="w-full bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl"
                  >
                    Save Summary
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        <section className="bg-white/80 backdrop-blur-md shadow-md rounded-2xl border border-indigo-100 p-6">
          <h2 className="text-xl font-semibold mb-4 text-indigo-700">
            Lesson Summaries
          </h2>
          {summaries.length > 0 ? (
            <Accordion type="single" collapsible className="w-full">
              {summaries.map((summary) => (
                <AccordionItem value={summary.id} key={summary.id}>
                  <AccordionTrigger className="font-medium text-indigo-800 hover:text-indigo-600">
                    {summary.title}
                  </AccordionTrigger>
                  <AccordionContent className="whitespace-pre-wrap text-gray-700 bg-indigo-50/50 p-3 rounded-lg">
                    {summary.content}
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          ) : (
            <p className="text-gray-500 italic">
              No summaries have been added yet.
            </p>
          )}
        </section>
      </motion.div>
    </main>
  );
}
