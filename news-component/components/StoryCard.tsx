/**
 * StoryCard Component
 * Individual story display with all metadata
 */

import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Story } from '../types/news';
import SourceBadge from './SourceBadge';
import ImportanceScores from './ImportanceScores';

interface StoryCardProps {
  story: Story;
  defaultExpanded?: boolean;
}

export default function StoryCard({ story, defaultExpanded = false }: StoryCardProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  // Extract just the summary part (everything before "Sources:")
  const summaryText = story.summary.split('\nSources:')[0].trim();

  // For truncation, show first 400 chars
  const shouldTruncate = summaryText.length > 400;
  const displaySummary = expanded || !shouldTruncate
    ? summaryText
    : summaryText.substring(0, 400) + '...';

  // Parse timestamp for display
  const formattedTime = new Date(story.timestamp).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <article className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow duration-200">
      {/* Header */}
      <div className="mb-4">
        <h2 className="text-xl font-bold text-gray-900 leading-tight mb-2">
          {story.title}
        </h2>
        <div className="flex items-center gap-3 text-xs text-gray-500">
          <span className="flex items-center gap-1">
            <svg
              className="w-4 h-4"
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
            {story.cluster_size} articles
          </span>
          <span>•</span>
          <time dateTime={story.timestamp}>{formattedTime}</time>
        </div>
      </div>

      {/* Summary */}
      <div className="mb-4">
        <div className="prose prose-sm max-w-none text-gray-700">
          <ReactMarkdown
            components={{
              // Customize rendering to maintain minimalist styling
              p: ({ children }) => <p className="mb-3 leading-relaxed">{children}</p>,
              strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
              em: ({ children }) => <em className="italic">{children}</em>,
              ul: ({ children }) => <ul className="mb-3 ml-5 list-disc space-y-1">{children}</ul>,
              ol: ({ children }) => <ol className="mb-3 ml-5 list-decimal space-y-1">{children}</ol>,
              li: ({ children }) => <li className="leading-relaxed">{children}</li>,
              a: ({ href, children }) => (
                <a
                  href={href}
                  className="text-blue-600 hover:text-blue-700 underline transition-colors"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {children}
                </a>
              ),
              h1: ({ children }) => <h1 className="text-lg font-bold text-gray-900 mb-2 mt-4">{children}</h1>,
              h2: ({ children }) => <h2 className="text-base font-bold text-gray-900 mb-2 mt-3">{children}</h2>,
              h3: ({ children }) => <h3 className="text-sm font-semibold text-gray-900 mb-2 mt-2">{children}</h3>,
              blockquote: ({ children }) => (
                <blockquote className="border-l-4 border-gray-300 pl-4 italic text-gray-600 my-3">
                  {children}
                </blockquote>
              ),
              code: ({ children }) => (
                <code className="bg-gray-100 text-gray-800 px-1.5 py-0.5 rounded text-sm font-mono">
                  {children}
                </code>
              ),
            }}
          >
            {displaySummary}
          </ReactMarkdown>
        </div>
        {shouldTruncate && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="mt-2 text-sm font-medium text-blue-600 hover:text-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded px-1 -mx-1 transition-colors"
            aria-expanded={expanded}
          >
            {expanded ? 'Show less' : 'Read more'}
          </button>
        )}
      </div>

      {/* Sources */}
      <div className="mb-4 pb-4 border-b border-gray-100">
        <h3 className="text-xs font-semibold text-gray-700 uppercase tracking-wide mb-2">
          Sources
        </h3>
        <div className="flex flex-wrap gap-2">
          {story.sources.map((source, index) => (
            <SourceBadge key={`${source.url}-${index}`} source={source} />
          ))}
        </div>
      </div>

      {/* Importance Scores */}
      <ImportanceScores
        scores={story.importance_scores}
        average={story.importance_avg}
      />
    </article>
  );
}
