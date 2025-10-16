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
  const [attendanceRecords, setAttendanceRecords] = useState([]);
  const [loading, setLoading] = useState(true);

  const params = useParams();
  const classId = params.classId;

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
          setLoading(false);
        });

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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-6 animate-fadeIn">
      <div className="max-w-7xl mx-auto grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <h1 className="text-3xl font-bold mb-6 text-gray-800">
            {classData?.className}
          </h1>
          <h2 className="text-xl font-semibold mb-4 text-gray-700">
            Lesson Summaries
          </h2>
          {summaries.length > 0 ? (
            <Accordion
              type="single"
              collapsible
              className="w-full bg-white rounded-2xl shadow-md border border-gray-100"
            >
              {summaries.map((summary) => (
                <AccordionItem
                  value={summary.id}
                  key={summary.id}
                  className="transition-all hover:bg-gray-50 rounded-lg"
                >
                  <AccordionTrigger className="text-lg font-medium text-gray-800">
                    {summary.title}
                  </AccordionTrigger>
                  <AccordionContent className="whitespace-pre-wrap text-gray-600 p-4">
                    {summary.content}
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          ) : (
            <p className="text-sm text-gray-500">
              No summaries are available for this class yet.
            </p>
          )}
        </div>

        <div className="lg:col-span-1">
          <Card className="bg-white rounded-2xl shadow-md border border-gray-100">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-gray-800">
                <CalendarCheck className="h-5 w-5 text-blue-500" />
                My Attendance Record
              </CardTitle>
            </CardHeader>
            <CardContent>
              {attendanceRecords.length > 0 ? (
                <ul className="space-y-2">
                  {attendanceRecords.map((record) => (
                    <li
                      key={record.id}
                      className="flex justify-between items-center text-sm p-2 bg-gray-50 hover:bg-gray-100 transition rounded-lg"
                    >
                      <span className="text-gray-700">{record.date}</span>
                      <span
                        className={`font-semibold capitalize px-2 py-1 text-xs rounded-full ${
                          record.status === 'present'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                      >
                        {record.status}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-gray-500">
                  No attendance records found.
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
