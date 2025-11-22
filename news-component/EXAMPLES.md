# Usage Examples

This document provides real-world examples of how to use the News Component in different scenarios.

## Example 1: Simple Standalone Page

The simplest way to use the component - a dedicated news page.

```typescript
// pages/news.tsx
import Head from 'next/head';
import NewsHub from '../components/NewsHub';

export default function NewsPage() {
  return (
    <>
      <Head>
        <title>Latest News - Your Site</title>
        <meta name="description" content="Balanced news from across the spectrum" />
      </Head>

      <main className="min-h-screen bg-gray-50">
        <NewsHub />
      </main>
    </>
  );
}
```

## Example 2: Homepage Widget

Show the latest 3 stories on your homepage.

```typescript
// pages/index.tsx
import Head from 'next/head';
import Link from 'next/link';
import { useLatestStories } from '../hooks/useNews';
import StoryCard from '../components/StoryCard';

export default function HomePage() {
  const { stories, isLoading } = useLatestStories();
  const topStories = stories.slice(0, 3);

  return (
    <>
      <Head>
        <title>Home - Your Site</title>
      </Head>

      <main>
        <section className="hero">
          <h1>Welcome to Your Site</h1>
        </section>

        <section className="py-16 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between mb-8">
              <h2 className="text-3xl font-bold text-gray-900">Latest News</h2>
              <Link
                href="/news"
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                View all news →
              </Link>
            </div>

            {isLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[1, 2, 3].map((n) => (
                  <div key={n} className="bg-white rounded-lg p-6 animate-pulse">
                    <div className="h-6 bg-gray-200 rounded w-3/4 mb-4"></div>
                    <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {topStories.map((story) => (
                  <StoryCard key={story.story_id} story={story} />
                ))}
              </div>
            )}
          </div>
        </section>
      </main>
    </>
  );
}
```

## Example 3: Blog Post Sidebar

Show related news in a blog post sidebar.

```typescript
// components/BlogPost.tsx
import { useLatestStories } from '../hooks/useNews';
import SourceBadge from '../components/SourceBadge';

export default function BlogPost({ post }: { post: any }) {
  const { stories, isLoading } = useLatestStories();

  // Get top 2 most important stories
  const topStories = stories
    .sort((a, b) => b.importance_avg - a.importance_avg)
    .slice(0, 2);

  return (
    <div className="max-w-7xl mx-auto px-4 py-12">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main content */}
        <article className="lg:col-span-2">
          <h1 className="text-4xl font-bold mb-4">{post.title}</h1>
          <div className="prose max-w-none">{post.content}</div>
        </article>

        {/* Sidebar */}
        <aside className="space-y-6">
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">Top News Today</h3>

            {isLoading ? (
              <div className="space-y-4">
                <div className="animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {topStories.map((story) => (
                  <div key={story.story_id} className="border-b border-gray-100 pb-4 last:border-0">
                    <h4 className="font-semibold text-sm text-gray-900 mb-2 line-clamp-2">
                      {story.title}
                    </h4>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs text-gray-600">
                        {story.cluster_size} sources
                      </span>
                      <span className="text-xs font-medium text-blue-600">
                        {story.importance_avg.toFixed(1)}/10
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {story.sources.slice(0, 3).map((source, idx) => (
                        <SourceBadge key={idx} source={source} showUrl={false} />
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}
```

## Example 4: Custom Filtered View

Show only high-importance stories (>8.0 average).

```typescript
// pages/important-news.tsx
import { useLatestStories } from '../hooks/useNews';
import StoryCard from '../components/StoryCard';

export default function ImportantNewsPage() {
  const { stories, isLoading, isError } = useLatestStories();

  // Filter for high importance stories
  const importantStories = stories.filter(
    (story) => story.importance_avg >= 8.0
  );

  return (
    <main className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            High-Importance News
          </h1>
          <p className="text-lg text-gray-600">
            Stories with importance score ≥ 8.0
          </p>
        </div>

        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          </div>
        ) : isError ? (
          <div className="text-center py-12 text-red-600">
            Failed to load stories
          </div>
        ) : importantStories.length === 0 ? (
          <div className="text-center py-12 text-gray-600">
            No high-importance stories today
          </div>
        ) : (
          <>
            <div className="mb-4 text-sm text-gray-600">
              {importantStories.length} high-importance{' '}
              {importantStories.length === 1 ? 'story' : 'stories'}
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {importantStories.map((story) => (
                <StoryCard key={story.story_id} story={story} />
              ))}
            </div>
          </>
        )}
      </div>
    </main>
  );
}
```

## Example 5: Mobile App-Style Interface

Create a mobile-optimized swipeable news feed.

```typescript
// pages/mobile-news.tsx
import { useState } from 'react';
import { useLatestStories } from '../hooks/useNews';
import StoryCard from '../components/StoryCard';

export default function MobileNewsPage() {
  const { stories, isLoading } = useLatestStories();
  const [currentIndex, setCurrentIndex] = useState(0);

  const handleNext = () => {
    if (currentIndex < stories.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const currentStory = stories[currentIndex];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold">News Feed</h1>
          <div className="text-sm text-gray-600">
            {currentIndex + 1} / {stories.length}
          </div>
        </div>
      </header>

      {/* Story */}
      <main className="flex-1 overflow-auto p-4">
        {currentStory && <StoryCard story={currentStory} />}
      </main>

      {/* Navigation */}
      <footer className="bg-white border-t border-gray-200 p-4">
        <div className="flex items-center justify-between max-w-md mx-auto">
          <button
            onClick={handlePrevious}
            disabled={currentIndex === 0}
            className="px-6 py-2 bg-white border border-gray-300 rounded-lg font-medium text-gray-700 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
          >
            ← Previous
          </button>

          <div className="flex gap-1">
            {stories.slice(0, 5).map((_, idx) => (
              <div
                key={idx}
                className={`w-2 h-2 rounded-full transition-colors ${
                  idx === currentIndex ? 'bg-blue-600' : 'bg-gray-300'
                }`}
              />
            ))}
            {stories.length > 5 && (
              <div className="text-xs text-gray-500 ml-2">
                +{stories.length - 5}
              </div>
            )}
          </div>

          <button
            onClick={handleNext}
            disabled={currentIndex === stories.length - 1}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium disabled:opacity-40 disabled:cursor-not-allowed hover:bg-blue-700 transition-colors"
          >
            Next →
          </button>
        </div>
      </footer>
    </div>
  );
}
```

## Example 6: Email Digest Component

Generate an email-friendly layout (for use with React Email or similar).

```typescript
// components/EmailDigest.tsx
import { Story } from '../types/news';

interface EmailDigestProps {
  stories: Story[];
  date: string;
}

export default function EmailDigest({ stories, date }: EmailDigestProps) {
  const topStories = stories
    .sort((a, b) => b.importance_avg - a.importance_avg)
    .slice(0, 5);

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', maxWidth: '600px', margin: '0 auto' }}>
      <div style={{ backgroundColor: '#1F2937', padding: '24px', textAlign: 'center' }}>
        <h1 style={{ color: 'white', margin: 0 }}>Daily News Digest</h1>
        <p style={{ color: '#D1D5DB', margin: '8px 0 0' }}>
          {new Date(date).toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
          })}
        </p>
      </div>

      <div style={{ padding: '24px' }}>
        {topStories.map((story, index) => (
          <div
            key={story.story_id}
            style={{
              borderBottom: '1px solid #E5E7EB',
              paddingBottom: '16px',
              marginBottom: '16px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <span
                style={{
                  backgroundColor: '#3B82F6',
                  color: 'white',
                  borderRadius: '12px',
                  padding: '2px 8px',
                  fontSize: '12px',
                  fontWeight: 'bold',
                }}
              >
                #{index + 1}
              </span>
              <span style={{ fontSize: '12px', color: '#6B7280' }}>
                {story.cluster_size} sources • {story.importance_avg.toFixed(1)}/10 importance
              </span>
            </div>

            <h2 style={{ fontSize: '18px', fontWeight: 'bold', margin: '0 0 8px' }}>
              {story.title}
            </h2>

            <p style={{ fontSize: '14px', color: '#4B5563', lineHeight: '1.6' }}>
              {story.summary.substring(0, 200)}...
            </p>

            <div style={{ marginTop: '8px' }}>
              {story.sources.slice(0, 3).map((source, idx) => (
                <a
                  key={idx}
                  href={source.url}
                  style={{
                    display: 'inline-block',
                    fontSize: '12px',
                    padding: '4px 8px',
                    marginRight: '4px',
                    marginBottom: '4px',
                    borderRadius: '4px',
                    textDecoration: 'none',
                    backgroundColor: source.lean === 'left' ? '#EFF6FF' : source.lean === 'right' ? '#FEF2F2' : '#F3F4F6',
                    color: source.lean === 'left' ? '#1E40AF' : source.lean === 'right' ? '#991B1B' : '#1F2937',
                  }}
                >
                  {source.name}
                </a>
              ))}
            </div>
          </div>
        ))}

        <div style={{ textAlign: 'center', marginTop: '24px' }}>
          <a
            href="https://yoursite.com/news"
            style={{
              display: 'inline-block',
              backgroundColor: '#3B82F6',
              color: 'white',
              padding: '12px 24px',
              borderRadius: '8px',
              textDecoration: 'none',
              fontWeight: 'bold',
            }}
          >
            View All Stories
          </a>
        </div>
      </div>

      <div
        style={{
          backgroundColor: '#F9FAFB',
          padding: '16px',
          textAlign: 'center',
          fontSize: '12px',
          color: '#6B7280',
        }}
      >
        <p>Balanced news from across the political spectrum</p>
      </div>
    </div>
  );
}
```

## Example 7: API Route for External Consumption

Create a custom API endpoint that other services can consume.

```typescript
// pages/api/news/summary.ts
import { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';
import { NEWS_DATA_PATH } from '../../../lib/config';
import { Story } from '../../../types/news';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    res.setHeader('Allow', ['GET']);
    return res.status(405).json({ error: 'Method Not Allowed' });
  }

  try {
    // Read latest stories
    const indexPath = path.join(NEWS_DATA_PATH, 'index.json');
    const indexData = JSON.parse(fs.readFileSync(indexPath, 'utf-8'));
    const latestDate = indexData.latest_date;

    const dateForFilename = latestDate.replace(/-/g, '');
    const storiesPath = path.join(NEWS_DATA_PATH, `stories_${dateForFilename}.json`);
    const stories: Story[] = JSON.parse(fs.readFileSync(storiesPath, 'utf-8'));

    // Create summary
    const summary = {
      date: latestDate,
      total_stories: stories.length,
      total_sources: stories.reduce((sum, s) => sum + s.cluster_size, 0),
      average_importance: (
        stories.reduce((sum, s) => sum + s.importance_avg, 0) / stories.length
      ).toFixed(2),
      top_story: {
        title: stories[0]?.title,
        importance: stories[0]?.importance_avg,
        sources: stories[0]?.cluster_size,
      },
      source_breakdown: {
        left: stories.reduce(
          (sum, s) => sum + s.sources.filter((src) => src.lean === 'left').length,
          0
        ),
        center: stories.reduce(
          (sum, s) => sum + s.sources.filter((src) => src.lean === 'center').length,
          0
        ),
        right: stories.reduce(
          (sum, s) => sum + s.sources.filter((src) => src.lean === 'right').length,
          0
        ),
      },
    };

    res.setHeader('Cache-Control', 'public, s-maxage=300');
    return res.status(200).json(summary);
  } catch (error) {
    console.error('Error generating summary:', error);
    return res.status(500).json({ error: 'Failed to generate summary' });
  }
}
```

## Example 8: Search and Filter Interface

Add search and filtering capabilities.

```typescript
// pages/search-news.tsx
import { useState, useMemo } from 'react';
import { useLatestStories } from '../hooks/useNews';
import StoryCard from '../components/StoryCard';

export default function SearchNewsPage() {
  const { stories, isLoading } = useLatestStories();
  const [searchTerm, setSearchTerm] = useState('');
  const [minImportance, setMinImportance] = useState(0);
  const [selectedLean, setSelectedLean] = useState<'all' | 'left' | 'center' | 'right'>('all');

  const filteredStories = useMemo(() => {
    return stories.filter((story) => {
      // Search filter
      const matchesSearch =
        searchTerm === '' ||
        story.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        story.summary.toLowerCase().includes(searchTerm.toLowerCase());

      // Importance filter
      const matchesImportance = story.importance_avg >= minImportance;

      // Lean filter
      const matchesLean =
        selectedLean === 'all' ||
        story.sources.some((source) => source.lean === selectedLean);

      return matchesSearch && matchesImportance && matchesLean;
    });
  }, [stories, searchTerm, minImportance, selectedLean]);

  return (
    <main className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-8">Search News</h1>

        {/* Filters */}
        <div className="bg-white border border-gray-200 rounded-lg p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Search */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search
              </label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search stories..."
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Importance */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Min Importance: {minImportance.toFixed(1)}
              </label>
              <input
                type="range"
                min="0"
                max="10"
                step="0.5"
                value={minImportance}
                onChange={(e) => setMinImportance(parseFloat(e.target.value))}
                className="w-full"
              />
            </div>

            {/* Political Lean */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Source Lean
              </label>
              <select
                value={selectedLean}
                onChange={(e) => setSelectedLean(e.target.value as any)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">All Sources</option>
                <option value="left">Left-leaning</option>
                <option value="center">Center</option>
                <option value="right">Right-leaning</option>
              </select>
            </div>
          </div>
        </div>

        {/* Results */}
        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          </div>
        ) : (
          <>
            <div className="mb-4 text-sm text-gray-600">
              {filteredStories.length} {filteredStories.length === 1 ? 'story' : 'stories'} found
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredStories.map((story) => (
                <StoryCard key={story.story_id} story={story} />
              ))}
            </div>
          </>
        )}
      </div>
    </main>
  );
}
```

These examples demonstrate the flexibility of the News Component package and show how it can be adapted to various use cases and interfaces.
