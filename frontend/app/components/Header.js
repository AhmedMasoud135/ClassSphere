'use client';
import { useAuth } from '@/app/context/AuthContext';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { auth } from '@/lib/firebase';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { GraduationCap, LogOut } from 'lucide-react';

export default function Header() {
  const { user } = useAuth();
  const router = useRouter();

  const handleSignOut = async () => {
    try {
      await auth.signOut();
      router.push('/login');
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  if (!user) return null;

  return (
    <header className="flex h-16 items-center justify-between border-b bg-gradient-to-r from-indigo-600 via-blue-500 to-indigo-700 px-6 shadow-md text-white">
      {/* Logo or Title */}
      <div className="flex items-center gap-2">
        <GraduationCap className="h-6 w-6 text-white" />
        <h1 className="text-lg font-semibold tracking-wide">
          Smart Attendance System
        </h1>
      </div>

      {/* User Dropdown */}
      <DropdownMenu>
        <DropdownMenuTrigger className="focus:outline-none">
          <div className="flex items-center gap-3 bg-white/10 hover:bg-white/20 transition-colors px-3 py-1.5 rounded-full">
            <Avatar className="h-8 w-8 border-2 border-white">
              <AvatarImage src={user.photoURL} alt={user.displayName} />
              <AvatarFallback>
                {user.displayName?.charAt(0).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <span className="hidden sm:inline text-sm font-medium">
              {user.displayName}
            </span>
          </div>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-48 mt-2 shadow-lg">
          <DropdownMenuLabel className="text-gray-700 font-semibold">
            {user.displayName}
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem
            onClick={handleSignOut}
            className="cursor-pointer text-red-600 hover:bg-red-50 flex items-center gap-2"
          >
            <LogOut className="h-4 w-4" /> Sign Out
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  );
}
