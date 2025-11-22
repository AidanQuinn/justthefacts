/**
 * Custom hook for fetching news data with SWR
 */

import useSWR from 'swr';
import { DateInfo, NewsResponse } from '../types/news';

const fetcher = (url: string) => fetch(url).then((res) => res.json());

/**
 * Hook to fetch available dates
 */
export function useDates() {
  const { data, error, isLoading } = useSWR<DateInfo>('/api/news/dates', fetcher, {
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
    // Refresh every 5 minutes
    refreshInterval: 300000,
  });

  return {
    dates: data,
    isLoading,
    isError: error,
  };
}

/**
 * Hook to fetch stories for a specific date
 * @param date - Date in YYYY-MM-DD format, or null to fetch latest
 */
export function useStories(date: string | null) {
  const url = date ? `/api/news/stories?date=${date}` : '/api/news/latest';

  const { data, error, isLoading } = useSWR<NewsResponse>(url, fetcher, {
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
    // Refresh every 5 minutes for current day, less frequently for past dates
    refreshInterval: date === new Date().toISOString().split('T')[0] ? 300000 : 3600000,
  });

  return {
    stories: data?.stories || [],
    date: data?.date,
    isLoading,
    isError: error,
  };
}

/**
 * Hook to fetch latest stories (convenience wrapper)
 */
export function useLatestStories() {
  return useStories(null);
}
