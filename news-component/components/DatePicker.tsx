/**
 * DatePicker Component
 * Calendar-based date picker for selecting news dates
 */

import React, { useMemo } from 'react';
import { format, parseISO } from 'date-fns';

interface DatePickerProps {
  availableDates: string[];
  selectedDate: string | null;
  onDateChange: (date: string) => void;
  isLoading?: boolean;
}

export default function DatePicker({
  availableDates,
  selectedDate,
  onDateChange,
  isLoading = false,
}: DatePickerProps) {
  // Create a Set for O(1) lookup
  const availableDatesSet = useMemo(
    () => new Set(availableDates),
    [availableDates]
  );

  // Format date for display
  const displayDate = useMemo(() => {
    if (!selectedDate) return 'Select a date';
    try {
      return format(parseISO(selectedDate), 'EEEE, MMMM d, yyyy');
    } catch {
      return selectedDate;
    }
  }, [selectedDate]);

  // Get min and max dates for the input
  const { minDate, maxDate } = useMemo(() => {
    if (availableDates.length === 0) {
      return { minDate: '', maxDate: '' };
    }
    const sorted = [...availableDates].sort();
    return {
      minDate: sorted[0],
      maxDate: sorted[sorted.length - 1],
    };
  }, [availableDates]);

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newDate = e.target.value;
    if (availableDatesSet.has(newDate)) {
      onDateChange(newDate);
    }
  };

  const goToPreviousDate = () => {
    if (!selectedDate) return;
    const sorted = [...availableDates].sort();
    const currentIndex = sorted.indexOf(selectedDate);
    if (currentIndex > 0) {
      onDateChange(sorted[currentIndex - 1]);
    }
  };

  const goToNextDate = () => {
    if (!selectedDate) return;
    const sorted = [...availableDates].sort();
    const currentIndex = sorted.indexOf(selectedDate);
    if (currentIndex < sorted.length - 1) {
      onDateChange(sorted[currentIndex + 1]);
    }
  };

  const goToLatest = () => {
    if (availableDates.length > 0) {
      const sorted = [...availableDates].sort();
      onDateChange(sorted[sorted.length - 1]);
    }
  };

  const hasPrevious = useMemo(() => {
    if (!selectedDate) return false;
    const sorted = [...availableDates].sort();
    return sorted.indexOf(selectedDate) > 0;
  }, [selectedDate, availableDates]);

  const hasNext = useMemo(() => {
    if (!selectedDate) return false;
    const sorted = [...availableDates].sort();
    const index = sorted.indexOf(selectedDate);
    return index >= 0 && index < sorted.length - 1;
  }, [selectedDate, availableDates]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-4">
        <div className="animate-pulse flex items-center space-x-4">
          <div className="h-8 w-8 bg-gray-200 rounded"></div>
          <div className="h-6 w-48 bg-gray-200 rounded"></div>
          <div className="h-8 w-8 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-4 py-4">
      <div className="flex items-center gap-2">
        <button
          onClick={goToPreviousDate}
          disabled={!hasPrevious}
          className="p-2 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
          aria-label="Previous date"
          title="Previous date"
        >
          <svg
            className="w-5 h-5 text-gray-700"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
        </button>

        <div className="relative">
          <input
            type="date"
            value={selectedDate || ''}
            onChange={handleDateChange}
            min={minDate}
            max={maxDate}
            className="sr-only"
            aria-label="Select date"
          />
          <button
            onClick={() => {
              const input = document.querySelector('input[type="date"]') as HTMLInputElement;
              input?.showPicker?.();
            }}
            className="px-4 py-2 text-sm font-medium text-gray-900 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors min-w-[240px] text-center"
          >
            {displayDate}
          </button>
        </div>

        <button
          onClick={goToNextDate}
          disabled={!hasNext}
          className="p-2 rounded-lg border border-gray-200 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
          aria-label="Next date"
          title="Next date"
        >
          <svg
            className="w-5 h-5 text-gray-700"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5l7 7-7 7"
            />
          </svg>
        </button>
      </div>

      <button
        onClick={goToLatest}
        disabled={selectedDate === maxDate}
        className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      >
        Latest News
      </button>
    </div>
  );
}
