// app/student/dashboard/page.js
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

  // Fetch enrolled classes
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
      // 1. Find the class with the given join code
      const q = query(
        collection(db, 'classes'),
        where('joinCode', '==', joinCode.trim().toUpperCase())
      );
      const querySnapshot = await getDocs(q);

      if (querySnapshot.empty) {
        setError('Invalid join code. Please check and try again.');
        return;
      }

      // 2. Get the class document
      const classDoc = querySnapshot.docs[0];
      const classData = classDoc.data();

      // 3. Check if student is already enrolled
      if (classData.studentIds.includes(user.uid)) {
        setError('You are already enrolled in this class.');
        return;
      }

      // 4. Add the student's UID to the class's studentIds array
      await updateDoc(doc(db, 'classes', classDoc.id), {
        studentIds: arrayUnion(user.uid),
      });

      setJoinCode(''); // Clear input on success
    } catch (err) {
      console.error('Error joining class:', err);
      setError('An error occurred. Please try again.');
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Student Dashboard</h1>

      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Join a New Class</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleJoinClass} className="flex items-start gap-4">
            <div className="flex-1">
              <Input
                placeholder="Enter 6-character join code"
                value={joinCode}
                onChange={(e) => setJoinCode(e.target.value)}
              />
              {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
            </div>
            <Button type="submit">Join</Button>
          </form>
        </CardContent>
      </Card>

      <h2 className="text-xl font-semibold mb-4">Your Enrolled Classes</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {classes.length > 0 ? (
          classes.map((c) => (
            // Add the <Link> component here
            <Link href={`/student/class/${c.id}`} key={c.id}>
              <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                {/* The rest of your CardHeader and CardContent goes here */}
                <CardHeader>
                  <CardTitle>{c.className}</CardTitle>
                  <CardDescription>Taught by {c.teacherName}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center">
                    <Users className="h-4 w-4 mr-2 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">
                      {c.studentIds.length} students enrolled
                    </span>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))
        ) : (
          <p>You are not enrolled in any classes yet.</p>
        )}
      </div>
    </div>
  );
}
