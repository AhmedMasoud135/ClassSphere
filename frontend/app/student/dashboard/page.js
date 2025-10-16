'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/app/context/AuthContext';
import { db } from '@/lib/firebase';
import Link from 'next/link';
import {
  collection,
  query,
  where,
  onSnapshot,
  getDocs,
  updateDoc,
  doc,
  arrayUnion,
} from 'firebase/firestore';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from '@/components/ui/card';
import { Users } from 'lucide-react';

export default function StudentDashboardPage() {
  const { user } = useAuth();
  const [classes, setClasses] = useState([]);
  const [joinCode, setJoinCode] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (user) {
      const q = query(
        collection(db, 'classes'),
        where('studentIds', 'array-contains', user.uid)
      );
      const unsubscribe = onSnapshot(q, (querySnapshot) => {
        const classesData = [];
        querySnapshot.forEach((doc) => {
          classesData.push({ id: doc.id, ...doc.data() });
        });
        setClasses(classesData);
      });
      return () => unsubscribe();
    }
  }, [user]);

  const handleJoinClass = async (e) => {
    e.preventDefault();
    setError('');
    if (joinCode.trim().length !== 6) {
      setError('Please enter a valid 6-character code.');
      return;
    }

    try {
      const q = query(
        collection(db, 'classes'),
        where('joinCode', '==', joinCode.trim().toUpperCase())
      );
      const querySnapshot = await getDocs(q);

      if (querySnapshot.empty) {
        setError('Invalid join code. Please check and try again.');
        return;
      }

      const classDoc = querySnapshot.docs[0];
      const classData = classDoc.data();

      if (classData.studentIds.includes(user.uid)) {
        setError('You are already enrolled in this class.');
        return;
      }

      await updateDoc(doc(db, 'classes', classDoc.id), {
        studentIds: arrayUnion(user.uid),
      });

      setJoinCode('');
    } catch (err) {
      console.error('Error joining class:', err);
      setError('An error occurred. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 p-6 md:p-10">
      <h1 className="text-4xl font-bold mb-8 text-gray-800 text-center">
        Student Dashboard
      </h1>

      <Card className="max-w-3xl mx-auto mb-10 shadow-lg border border-blue-100 hover:shadow-xl transition-all duration-300">
        <CardHeader>
          <CardTitle className="text-xl font-semibold text-blue-700">
            Join a New Class
          </CardTitle>
          <CardDescription>
            Enter a join code provided by your teacher
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={handleJoinClass}
            className="flex flex-col md:flex-row items-start md:items-center gap-4"
          >
            <div className="flex-1 w-full">
              <Input
                placeholder="Enter 6-character join code"
                value={joinCode}
                onChange={(e) => setJoinCode(e.target.value)}
                className="border-blue-200 focus:ring-2 focus:ring-blue-500"
              />
              {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
            </div>
            <Button
              type="submit"
              className="bg-blue-600 hover:bg-blue-700 text-white transition-all duration-300"
            >
              Join Class
            </Button>
          </form>
        </CardContent>
      </Card>

      <h2 className="text-2xl font-semibold mb-6 text-gray-700 text-center">
        Your Enrolled Classes
      </h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {classes.length > 0 ? (
          classes.map((c) => (
            <Link href={`/student/class/${c.id}`} key={c.id}>
              <Card className="hover:shadow-xl hover:-translate-y-1 transition-all duration-300 border border-blue-100 bg-white/70 backdrop-blur-sm">
                <CardHeader>
                  <CardTitle className="text-blue-700">{c.className}</CardTitle>
                  <CardDescription className="text-gray-500">
                    Taught by {c.teacherName}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center text-gray-600">
                    <Users className="h-4 w-4 mr-2 text-blue-500" />
                    <span className="text-sm">
                      {c.studentIds.length} students enrolled
                    </span>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))
        ) : (
          <p className="text-center text-gray-500 col-span-full">
            You are not enrolled in any classes yet.
          </p>
        )}
      </div>
    </div>
  );
}
