/**
 * NewsHub Component
 * Main container component that manages state and date selection
 */

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { useDates, useStories } from '../hooks/useNews';
import DatePicker from './DatePicker';
import StoryCard from './StoryCard';

interface NewsHubProps {
  initialDate?: string | null;
}

export default function NewsHub({ initialDate = null }: NewsHubProps) {
  const router = useRouter();
  const [selectedDate, setSelectedDate] = useState<string | null>(initialDate);

  // Fetch available dates
  const { dates, isLoading: datesLoading, isError: datesError } = useDates();

  // Fetch stories for selected date
  const { stories, date: currentDate, isLoading: storiesLoading, isError: storiesError } = useStories(selectedDate);

  // Initialize with latest date when dates are loaded
  useEffect(() => {
    if (dates && !selectedDate) {
      setSelectedDate(dates.latest_date);
    }
  }, [dates, selectedDate]);

  // Update URL when date changes
  useEffect(() => {
    if (selectedDate && router.isReady) {
      const currentQuery = router.query.date;
      if (currentQuery !== selectedDate) {
        router.push(
          {
            pathname: router.pathname,
            query: { ...router.query, date: selectedDate },
          },
          undefined,
          { shallow: true }
        );
      }
    }
  }, [selectedDate, router]);

  // Read date from URL on mount
  useEffect(() => {
    if (router.isReady && router.query.date && typeof router.query.date === 'string') {
      setSelectedDate(router.query.date);
    }
  }, [router.isReady, router.query.date]);

  const handleDateChange = (date: string) => {
    setSelectedDate(date);
  };

  // Error state
  if (datesError) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <svg
            className="w-12 h-12 text-red-400 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h2 className="text-xl font-semibold text-red-900 mb-2">
            Failed to load news dates
          </h2>
          <p className="text-red-700">
            Please try refreshing the page or check back later.
          </p>
        </div>
      </div>
    );
  }

  // Stories error state
  if (storiesError) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <svg
            className="w-12 h-12 text-yellow-400 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <h2 className="text-xl font-semibold text-yellow-900 mb-2">
            No stories found for this date
          </h2>
          <p className="text-yellow-700 mb-4">
            Try selecting a different date from the date picker.
          </p>
          {dates && (
            <button
              onClick={() => setSelectedDate(dates.latest_date)}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Go to Latest News
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <header className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">News Hub</h1>
        <p className="text-lg text-gray-600">
          Balanced news aggregation from across the political spectrum
        </p>
      </header>

      {/* Date Picker */}
      <div className="mb-8 bg-white border border-gray-200 rounded-lg px-6">
        <DatePicker
          availableDates={dates?.available_dates || []}
          selectedDate={selectedDate}
          onDateChange={handleDateChange}
          isLoading={datesLoading}
        />
      </div>

      {/* Loading State */}
      {(storiesLoading || datesLoading) && (
        <div className="flex flex-col gap-6 max-w-4xl mx-auto">
          {[1, 2, 3, 4, 5, 6].map((n) => (
            <div
              key={n}
              className="bg-white border border-gray-200 rounded-lg p-6 animate-pulse"
            >
              <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-5/6 mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      )}

      {/* Stories Grid */}
      {!storiesLoading && !datesLoading && stories.length > 0 && (
        <>
          <div className="mb-4 text-sm text-gray-600">
            {stories.length} {stories.length === 1 ? 'story' : 'stories'} for{' '}
            {currentDate && new Date(currentDate).toLocaleDateString('en-US', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric',
            })}
          </div>
          <div className="flex flex-col gap-6 max-w-4xl mx-auto">
            {stories
              .slice()
              .sort((a, b) => b.importance_avg - a.importance_avg)
              .map((story, index) => (
                <StoryCard key={story.story_id} story={story} defaultExpanded={index === 0} />
              ))}
          </div>
        </>
      )}

      {/* Empty State */}
      {!storiesLoading && !datesLoading && stories.length === 0 && (
        <div className="text-center py-12">
          <svg
            className="w-16 h-16 text-gray-300 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"
            />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No stories yet</h3>
          <p className="text-gray-600">Check back later for new stories.</p>
        </div>
      )}
    </div>
  );
}
