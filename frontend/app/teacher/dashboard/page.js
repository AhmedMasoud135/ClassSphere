'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/app/context/AuthContext'; // Adjust path if needed
import { db } from '@/lib/firebase'; // Adjust path if needed
import {
  collection,
  addDoc,
  query,
  where,
  onSnapshot,
} from 'firebase/firestore';

import { Button } from '@/components/ui/button';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Users, PlusCircle, ClipboardCopy, RefreshCw } from 'lucide-react';

// Helper function to generate a random 6-character code
const generateJoinCode = () => {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let result = '';
  for (let i = 0; i < 6; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
};

export default function TeacherDashboardPage() {
  const { user } = useAuth();
  const [className, setClassName] = useState('');
  const [classes, setClasses] = useState([]);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [updateMessage, setUpdateMessage] = useState('');

  useEffect(() => {
    if (user) {
      const q = query(
        collection(db, 'classes'),
        where('teacherId', '==', user.uid)
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

  const handleCreateClass = async (e) => {
    e.preventDefault();
    if (className.trim() === '') return;
    try {
      const joinCode = generateJoinCode();
      await addDoc(collection(db, 'classes'), {
        className: className,
        teacherId: user.uid,
        teacherName: user.displayName,
        studentIds: [],
        createdAt: new Date(),
        joinCode: joinCode,
      });
      setClassName('');
      setIsDialogOpen(false);
    } catch (error) {
      console.error('Error creating class: ', error);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  const handleUpdateModel = async () => {
    setIsUpdating(true);
    setUpdateMessage('Model is updating, please wait...');
    try {
      const response = await fetch('http://127.0.0.1:5001/update-embeddings', {
        method: 'POST',
      });
      const data = await response.json();
      setUpdateMessage(data.message || data.error);
    } catch (error) {
      console.error('Error updating model:', error);
      setUpdateMessage('Failed to connect to the server.');
    }
    setIsUpdating(false);
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Teacher Dashboard</h1>
        <div className="flex items-center gap-2">
          <Button
            onClick={handleUpdateModel}
            disabled={isUpdating}
            variant="outline"
          >
            <RefreshCw
              className={`mr-2 h-4 w-4 ${isUpdating ? 'animate-spin' : ''}`}
            />
            {isUpdating ? 'Updating...' : 'Update Recognition Model'}
          </Button>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <PlusCircle className="mr-2 h-4 w-4" /> Create Class
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create a New Class</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleCreateClass} className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="className" className="text-right">
                    Class Name
                  </Label>
                  <Input
                    id="className"
                    value={className}
                    onChange={(e) => setClassName(e.target.value)}
                    className="col-span-3"
                    placeholder="e.g., Grade 10 - Mathematics"
                  />
                </div>
                <Button type="submit">Create</Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {updateMessage && (
        <p className="text-center text-sm text-muted-foreground mb-4">
          {updateMessage}
        </p>
      )}

      <h2 className="text-xl font-semibold mb-4">Your Classes</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {classes.length > 0 ? (
          classes.map((c) => (
            <Link href={`/teacher/class/${c.id}`} key={c.id}>
              <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader>
                  <CardTitle>{c.className}</CardTitle>
                  <CardDescription>Created by {c.teacherName}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center text-sm text-muted-foreground mb-4">
                    <Users className="h-4 w-4 mr-2" />
                    <span>{c.studentIds.length} students enrolled</span>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-slate-100 rounded-md">
                    <span className="font-mono text-sm tracking-widest">
                      {c.joinCode}
                    </span>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={(e) => {
                        e.preventDefault();
                        copyToClipboard(c.joinCode);
                      }}
                    >
                      <ClipboardCopy className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))
        ) : (
          <p>You haven&apos;t created any classes yet.</p>
        )}
      </div>
    </div>
  );
}
