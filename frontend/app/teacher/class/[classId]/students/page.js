'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { db } from '@/lib/firebase'; // Adjust path if needed
import { doc, getDoc } from 'firebase/firestore';

import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { ArrowLeft, User } from 'lucide-react';
import Spinner from '@/app/components/Spinner';

export default function ManageStudentsPage() {
  const params = useParams();
  const router = useRouter();
  const { classId } = params;

  const [students, setStudents] = useState([]);
  const [classData, setClassData] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch class and student details
  useEffect(() => {
    const fetchStudents = async () => {
      if (!classId) return;

      const classDocRef = doc(db, 'classes', classId);
      const classDocSnap = await getDoc(classDocRef);

      if (classDocSnap.exists()) {
        const classInfo = classDocSnap.data();
        setClassData(classInfo);

        const studentUIDs = classInfo.studentIds || [];
        // Fetch details for each student
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

  if (loading) return <Spinner />;

  return (
    <div>
      <div className="flex items-center gap-4 mb-4">
        <Button variant="outline" size="icon" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <h1 className="text-3xl font-bold">
          Manage Students for {classData?.className}
        </h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Enrolled Students ({students.length})</CardTitle>
          <CardDescription>
            This is the list of all students currently enrolled in this class.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {students.length > 0 ? (
              students.map((student) => (
                <div
                  key={student.id}
                  className="flex items-center justify-between p-3 bg-slate-50 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <User className="h-5 w-5 text-muted-foreground" />
                    <div>
                      <p className="font-medium">{student.fullName}</p>
                      <p className="text-sm text-muted-foreground">
                        {student.email}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <p>No students are enrolled in this class yet.</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
