// components/Spinner.js
import { Loader2 } from 'lucide-react';

export default function Spinner() {
  return (
    <div className="flex items-center justify-center">
      <Loader2 className="h-8 w-8 text-slate-400 animate-spin" />
    </div>
  );
}
