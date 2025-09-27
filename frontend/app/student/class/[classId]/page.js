'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/app/context/AuthContext';
import { db } from '@/lib/firebase';
import {
  doc,
  getDoc,
  collection,
  query,
  where,
  onSnapshot,
  orderBy,
} from 'firebase/firestore';
import { useParams } from 'next/navigation';

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { CalendarCheck } from 'lucide-react';
import Spinner from '@/app/components/Spinner';

export default function StudentClassPage() {
  const { user } = useAuth();
  const [classData, setClassData] = useState(null);
  const [summaries, setSummaries] = useState([]);
  const [attendanceRecords, setAttendanceRecords] = useState([]); // State for attendance
  const [loading, setLoading] = useState(true);

  const params = useParams();
  const classId = params.classId;

  // Effect to fetch class data, summaries, and attendance
  useEffect(() => {
    if (!user || !classId) return;

    let summariesUnsubscribe;
    let attendanceUnsubscribe;

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

        // Listener for summaries
        const summariesQuery = query(
          collection(db, 'summaries'),
          where('classId', '==', classId),
          orderBy('createdAt', 'desc')
        );
        summariesUnsubscribe = onSnapshot(summariesQuery, (querySnapshot) => {
          const summariesData = querySnapshot.docs.map((doc) => ({
            id: doc.id,
            ...doc.data(),
          }));
          setSummaries(summariesData);
          setLoading(false); // Stop loading after first fetch
        });

        // Listener for this student's attendance in this class
        const attendanceQuery = query(
          collection(db, 'attendance'),
          where('classId', '==', classId),
          where('studentId', '==', user.uid),
          orderBy('date', 'desc')
        );
        attendanceUnsubscribe = onSnapshot(attendanceQuery, (querySnapshot) => {
          const recordsData = querySnapshot.docs.map((doc) => ({
            id: doc.id,
            ...doc.data(),
          }));
          setAttendanceRecords(recordsData);
        });
      } catch (error) {
        console.error('Error fetching data: ', error);
        setLoading(false);
      }
    };

    fetchData();

    return () => {
      if (summariesUnsubscribe) summariesUnsubscribe();
      if (attendanceUnsubscribe) attendanceUnsubscribe();
    };
  }, [user, classId]);

  if (loading) return <Spinner />;

  return (
    <div className="grid lg:grid-cols-3 gap-8">
      <div className="lg:col-span-2">
        <h1 className="text-3xl font-bold mb-6">{classData?.className}</h1>
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
          <p className="text-sm text-muted-foreground">
            No summaries are available for this class yet.
          </p>
        )}
      </div>

      <div className="lg:col-span-1">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CalendarCheck className="h-5 w-5" />
              My Attendance Record
            </CardTitle>
          </CardHeader>
          <CardContent>
            {attendanceRecords.length > 0 ? (
              <ul className="space-y-2">
                {attendanceRecords.map((record) => (
                  <li
                    key={record.id}
                    className="flex justify-between items-center text-sm p-2 bg-slate-50 rounded-md"
                  >
                    <span>{record.date}</span>
                    <span className="font-semibold capitalize px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                      {record.status}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-muted-foreground">
                No attendance records found.
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
