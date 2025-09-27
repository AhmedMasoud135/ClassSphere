import { Inter } from 'next/font/google';
import './globals.css';
import { AuthContextProvider } from '@/app/context/AuthContext'; 

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'Class Sphere',
  description: 'AI-Powered Education Platform',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthContextProvider>
          {children}
        </AuthContextProvider>
      </body>
    </html>
  );
}
