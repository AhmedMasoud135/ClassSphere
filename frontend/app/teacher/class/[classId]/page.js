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
import { PlusCircle, Video } from 'lucide-react';
import Spinner from '@/app/components/Spinner';
import { Users } from "lucide-react"; 



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

  // Corrected useEffect block
  useEffect(() => {
    if (!user || !classId) {
      return;
    }

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

        unsubscribe = onSnapshot(
          q,
          (querySnapshot) => {
            const summariesData = [];
            querySnapshot.forEach((doc) => {
              summariesData.push({ id: doc.id, ...doc.data() });
            });
            setSummaries(summariesData);
            setLoading(false);
          },
          (error) => {
            console.error('Error fetching summaries: ', error);
            setLoading(false);
          }
        );
      } catch (error) {
        console.error('Error fetching class data: ', error);
        setLoading(false);
      }
    };

    fetchData();

    return () => {
      if (unsubscribe) {
        unsubscribe();
      }
    };
  }, [user, classId]);

  const handleAddSummary = async (e) => {
    e.preventDefault();
    if (summaryTitle.trim() === '' || summaryContent.trim() === '') return;
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
      console.error('Error adding summary: ', error);
    }
  };

  if (loading) return <Spinner />;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">{classData?.className}</h1>
        <div className="flex gap-2">
          <Link href={`/teacher/class/${classId}/students`}>
            <Button variant="outline">
              <Users className="mr-2 h-4 w-4" /> Manage Students
            </Button>
          </Link>
          <Link href={`/teacher/class/${classId}/attendance`}>
            <Button variant="outline">
              <Video className="mr-2 h-4 w-4" /> Live Attendance
            </Button>
          </Link>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <PlusCircle className="mr-2 h-4 w-4" /> Add Summary
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add New Lesson Summary</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleAddSummary} className="grid gap-4 py-4">
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
                    rows={10}
                  />
                </div>
                <Button type="submit">Save Summary</Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <h2 className="text-xl font-semibold mb-4">Lesson Summaries</h2>
      {summaries.length > 0 ? (
        <Accordion type="single" collapsible className="w-full">
          {summaries.map((summary) => (
            <AccordionItem value={summary.id} key={summary.id}>
              <AccordionTrigger>{summary.title}</AccordionTrigger>
              <AccordionContent className="whitespace-pre-wrap">
                {summary.content}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      ) : (
        <p>No summaries have been added for this class yet.</p>
      )}
    </div>
  );
}
