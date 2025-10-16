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
import { GraduationCap, BookOpen, School } from 'lucide-react';

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
    <main className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-600 relative overflow-hidden">
      {/* Background Overlay */}
      <div className="absolute inset-0 bg-[url('/images/school-bg.jpg')] bg-cover bg-center opacity-10"></div>

      <div className="text-center text-white space-y-3 absolute top-20">
        <div className="flex justify-center">
          <div className="bg-white/20 p-4 rounded-full">
            <School className="w-10 h-10 text-white" />
          </div>
        </div>
        <h1 className="text-4xl font-bold tracking-tight">School Portal</h1>
        <p className="text-lg text-blue-100">
          Welcome back! Please select your role to continue.
        </p>
      </div>

      <Card className="w-full max-w-md bg-white/90 backdrop-blur-md rounded-2xl shadow-2xl border border-white/20 p-6 mt-32">
        <CardHeader className="text-center mb-4">
          <CardTitle className="text-2xl font-bold text-gray-800">
            Choose Your Role
          </CardTitle>
          <CardDescription className="text-gray-600">
            Select how you want to access the portal
          </CardDescription>
        </CardHeader>

        <CardContent className="flex flex-col gap-4">
          <Button
            onClick={() => handleGoogleSignIn('teacher')}
            className="w-full py-4 text-lg font-semibold bg-blue-600 hover:bg-blue-700 text-white rounded-lg shadow-md transition-all flex items-center justify-center"
          >
            <BookOpen className="mr-2 h-5 w-5" /> Teacher Login
          </Button>

          <Button
            onClick={() => handleGoogleSignIn('student')}
            className="w-full py-4 text-lg font-semibold bg-purple-500 hover:bg-purple-600 text-white rounded-lg shadow-md transition-all flex items-center justify-center"
          >
            <GraduationCap className="mr-2 h-5 w-5" /> Student Login
          </Button>
        </CardContent>

        <div className="text-center mt-4 text-sm text-gray-600">
          Need help accessing your account?{' '}
          <a href="#" className="text-blue-600 hover:underline">
            Contact Support
          </a>
        </div>
      </Card>

      <footer className="absolute bottom-6 text-white/80 text-sm">
        © 2024 School Portal. All rights reserved.
      </footer>
    </main>
  );
}
