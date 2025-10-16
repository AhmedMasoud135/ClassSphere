'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/app/context/AuthContext';
import { db } from '@/lib/firebase';
import {
  collection,
  addDoc,
  query,
  where,
  onSnapshot,
  deleteDoc,
  doc,
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
  DialogFooter,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Users, PlusCircle, ClipboardCopy, RefreshCw, Trash2 } from 'lucide-react';

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

  // Delete confirmation states
  const [classToDelete, setClassToDelete] = useState(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

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

  const handleDeleteClass = async () => {
    if (!classToDelete) return;

    setIsDeleting(true);
    try {
      await deleteDoc(doc(db, 'classes', classToDelete.id));
      setIsDeleteDialogOpen(false);
      setClassToDelete(null);
    } catch (error) {
      console.error('Error deleting class: ', error);
      alert('Failed to delete class: ' + error.message);
    } finally {
      setIsDeleting(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  const handleUpdateModel = async () => {
    setIsUpdating(true);
    setUpdateMessage('Model is updating, please wait...');
    try {
      const response = await fetch('http://127.0.0.1:5000/update_embeddings', {
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
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 p-8 font-inter">
      <header className="flex justify-between items-center mb-10">
        <div>
          <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">
            Teacher Dashboard
          </h1>
          <p className="text-gray-500 text-sm mt-1">
            Manage your classes and students
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            onClick={handleUpdateModel}
            disabled={isUpdating}
            variant="outline"
            className="text-sm border-gray-300 hover:bg-gray-100"
          >
            <RefreshCw
              className={`mr-2 h-4 w-4 ${isUpdating ? 'animate-spin' : ''}`}
            />
            {isUpdating ? 'Updating...' : 'Update Model'}
          </Button>

          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button className="bg-gradient-to-r from-indigo-600 to-blue-500 hover:from-indigo-700 hover:to-blue-600 shadow-md">
                <PlusCircle className="mr-2 h-4 w-4" /> Create Class
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle className="text-lg font-semibold text-gray-900">
                  Create a New Class
                </DialogTitle>
              </DialogHeader>
              <form onSubmit={handleCreateClass} className="space-y-4 mt-2">
                <div>
                  <Label htmlFor="className" className="text-sm text-gray-700">
                    Class Name
                  </Label>
                  <Input
                    id="className"
                    value={className}
                    onChange={(e) => setClassName(e.target.value)}
                    placeholder="e.g., Grade 10 - Science"
                    className="mt-1"
                  />
                </div>
                <Button
                  type="submit"
                  className="w-full bg-indigo-600 hover:bg-indigo-700"
                >
                  Create
                </Button>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </header>

      {updateMessage && (
        <p className="text-center text-sm text-gray-500 mb-4">
          {updateMessage}
        </p>
      )}

      <section>
        <h2 className="text-2xl font-semibold text-gray-800 mb-6 flex items-center gap-2">
          <Users className="h-5 w-5 text-indigo-600" /> Your Classes
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {classes.length > 0 ? (
            classes.map((c) => (
              <Card
                key={c.id}
                className="bg-white hover:shadow-xl transition-all border border-gray-100 rounded-2xl overflow-hidden group relative"
              >
                <div className="h-2 bg-gradient-to-r from-indigo-500 to-purple-500 group-hover:from-indigo-600 group-hover:to-purple-600" />

                <Button
                  variant="ghost"
                  size="icon"
                  className="absolute top-4 right-4 z-10 bg-white hover:bg-red-100 rounded-full p-2 shadow-sm transition-all duration-200 text-gray-500 hover:text-red-600"
                  onClick={(e) => {
                    e.preventDefault();
                    setClassToDelete(c);
                    setIsDeleteDialogOpen(true);
                  }}
                >
                  <Trash2 className="h-4 w-4 text-red-500" />
                </Button>

                <Link href={`/teacher/class/${c.id}`}>
                  <CardHeader className="pt-5 pb-3">
                    <CardTitle className="text-lg font-semibold text-gray-900 pr-8">
                      {c.className}
                    </CardTitle>
                    <CardDescription className="text-sm text-gray-500">
                      Created by {c.teacherName}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center text-sm text-gray-600 mb-3">
                      <Users className="h-4 w-4 mr-2 text-indigo-600" />
                      <span>{c.studentIds.length} students enrolled</span>
                    </div>
                    <div className="flex items-center justify-between bg-gray-50 border rounded-md p-2">
                      <span className="font-mono text-sm tracking-widest text-gray-700">
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
                        <ClipboardCopy className="h-4 w-4 text-gray-600" />
                      </Button>
                    </div>
                  </CardContent>
                </Link>
              </Card>
            ))
          ) : (
            <p className="text-gray-600 text-center col-span-full">
              You haven&apos;t created any classes yet.
            </p>
          )}
        </div>
      </section>

      {/* Delete Confirmation Dialog */}
      <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="text-lg font-semibold text-gray-900">
              Delete Class Are you sure you want to delete the class
              <span className="font-bold text-indigo-600">
                {' '}
                {classToDelete?.className}{' '}
              </span>
              ? This action cannot be undone.
            </DialogTitle>
          </DialogHeader>
          <DialogFooter className="flex justify-end gap-3 mt-4">
            <Button
              variant="outline"
              onClick={() => setIsDeleteDialogOpen(false)}
              disabled={isDeleting}
            >
              Cancel
            </Button>
            <Button
              onClick={handleDeleteClass}
              disabled={isDeleting}
              className="bg-red-600 hover:bg-red-700 text-white"
            >
              {isDeleting ? 'Deleting...' : 'Delete'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
           