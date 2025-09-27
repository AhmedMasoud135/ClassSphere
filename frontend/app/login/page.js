
'use client';

import { GoogleAuthProvider, signInWithPopup } from 'firebase/auth';
import { auth, db } from '@/lib/firebase';
import { doc, setDoc, getDoc } from 'firebase/firestore';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from '@/components/ui/card';
import { GraduationCap, BookOpen } from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();

  const handleGoogleSignIn = async (role) => {
    const provider = new GoogleAuthProvider();
    try {
      const result = await signInWithPopup(auth, provider);
      const user = result.user;
      const userDocRef = doc(db, 'users', user.uid);
      const userDoc = await getDoc(userDocRef);
      if (!userDoc.exists()) {
        await setDoc(userDocRef, {
          uid: user.uid,
          email: user.email,
          fullName: user.displayName,
          role: role,
        });
      }
      router.push('/');
    } catch (error) {
      console.error('Error during sign-in:', error);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 p-4">
      <Card className="w-full max-w-sm">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold tracking-tight">
            Welcome to Class Sphere
          </CardTitle>
          <CardDescription>Sign in to access your dashboard</CardDescription>
        </CardHeader>
        <CardContent className="grid gap-4">
          <Button
            onClick={() => handleGoogleSignIn('student')}
            className="w-full"
          >
            <GraduationCap className="mr-2 h-4 w-4" />
            Sign in as Student
          </Button>
          <Button
            onClick={() => handleGoogleSignIn('teacher')}
            variant="outline"
            className="w-full"
          >
            <BookOpen className="mr-2 h-4 w-4" />
            Sign in as Teacher
          </Button>
        </CardContent>
      </Card>
    </main>
  );
}
