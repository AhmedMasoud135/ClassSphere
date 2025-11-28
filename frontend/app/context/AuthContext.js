'use client';

import { useContext, createContext, useState, useEffect } from 'react';
import { onAuthStateChanged } from 'firebase/auth';
import { auth, db } from '@/lib/firebase';
import { doc, getDoc } from 'firebase/firestore'; // Import Firestore functions

const AuthContext = createContext();

export const AuthContextProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true); // Add a loading state

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (currentUser) => {
      if (currentUser) {
        // If user is authenticated, get their document from Firestore
        const userDocRef = doc(db, 'users', currentUser.uid);
        try {
          const userDoc = await getDoc(userDocRef);
          if (userDoc.exists()) {
            // Set user state with combined auth and firestore data
            setUser({ ...currentUser, ...userDoc.data() });
          } else {
            // Handle case where user exists in Auth but not Firestore
            setUser(currentUser);
          }
        } catch (err) {
          // Log detailed error info to help debug Firestore permission issues
          // This error typically means Firestore security rules blocked the read
          try {
            console.error('Firestore getDoc error for user:', currentUser.uid);
            // Log known FirebaseError fields explicitly (some are non-enumerable)
            console.error('error.name:', err?.name);
            console.error('error.code:', err?.code);
            console.error('error.message:', err?.message);
            console.error('error.stack:', err?.stack);
            // Also log the raw object for completeness
            console.error('error object:', err);
          } catch (logErr) {
            // If logging fails for any reason, at least log the raw value
            console.error('Error logging failed value:', err, logErr);
          }
          // Fall back to the auth user object so app can continue
          setUser(currentUser);
        }
      } else {
        setUser(null);
      }
      setLoading(false); // Set loading to false once user state is determined
    });

    return () => unsubscribe();
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  return useContext(AuthContext);
};
