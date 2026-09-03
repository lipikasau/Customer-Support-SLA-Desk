import React, { useEffect, useState } from 'react';
import { differenceInMinutes, parseISO } from 'date-fns';

interface SlaBadgeProps {
  dueAt: string;
  isBreached: boolean;
  isResolved: boolean;
  label: string;
}

export default function SlaBadge({ dueAt, isBreached, isResolved, label }: SlaBadgeProps) {
  const [minutesLeft, setMinutesLeft] = useState<number>(0);

  useEffect(() => {
    const calculateTime = () => {
      const now = new Date();
      const due = parseISO(dueAt);
      setMinutesLeft(differenceInMinutes(due, now));
    };
    
    calculateTime();
    const interval = setInterval(calculateTime, 60000); // Update every minute
    return () => clearInterval(interval);
  }, [dueAt]);

  let colorClass = 'bg-green-500/10 text-green-400 border-green-500/20';
  let statusText = `${minutesLeft}m left`;

  if (isResolved) {
    colorClass = 'bg-slate-800 text-slate-400 border-slate-700';
    statusText = 'Resolved';
  } else if (isBreached) {
    colorClass = 'bg-red-500/10 text-red-400 border-red-500/20 animate-pulse';
    statusText = 'Breached';
  } else if (minutesLeft <= 60) {
    colorClass = 'bg-amber-500/10 text-amber-400 border-amber-500/20';
  }

  return (
    <div className={`inline-flex items-center px-2.5 py-1 rounded-full border text-xs font-medium transition-colors ${colorClass}`}>
      <span className="mr-1.5 opacity-70">{label}:</span>
      <span>{statusText}</span>
    </div>
  );
}
