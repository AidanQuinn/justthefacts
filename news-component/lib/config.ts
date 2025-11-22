/**
 * Configuration for the news component
 * Adjust these paths based on your project structure
 */

import path from 'path';

// Path to news_data directory relative to project root
// This assumes the news-component folder is at the root of your Next.js project
export const NEWS_DATA_PATH = process.env.NEWS_DATA_PATH || path.join(process.cwd(), 'news_data');

export const IMPORTANCE_LABELS: Record<keyof import('../types/news').ImportanceScores, string> = {
  impact: 'Impact',
  conflict: 'Conflict',
  ramifications: 'Ramifications',
  accountability: 'Accountability',
  informed_public: 'Informed Public',
  citizen_responsibility: 'Citizen Responsibility',
  transparency: 'Transparency',
};

export const LEAN_COLORS = {
  left: {
    bg: 'bg-blue-100',
    text: 'text-blue-800',
    border: 'border-blue-300',
    hover: 'hover:bg-blue-200',
  },
  center: {
    bg: 'bg-gray-100',
    text: 'text-gray-800',
    border: 'border-gray-300',
    hover: 'hover:bg-gray-200',
  },
  right: {
    bg: 'bg-red-100',
    text: 'text-red-800',
    border: 'border-red-300',
    hover: 'hover:bg-red-200',
  },
} as const;
