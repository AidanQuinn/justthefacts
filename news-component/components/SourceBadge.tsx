/**
 * SourceBadge Component
 * Displays a news source with political lean indicator
 */

import React from 'react';
import { Source } from '../types/news';
import { LEAN_COLORS } from '../lib/config';

interface SourceBadgeProps {
  source: Source;
  showUrl?: boolean;
}

export default function SourceBadge({ source, showUrl = true }: SourceBadgeProps) {
  // Get colors with fallback to center if lean is not recognized
  const colors = LEAN_COLORS[source.lean] || LEAN_COLORS.center;

  const badge = (
    <span
      className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${colors.bg} ${colors.text} ${colors.border} ${showUrl ? colors.hover : ''} transition-colors`}
      title={`${source.name} - ${source.lean}`}
    >
      {source.name}
    </span>
  );

  if (showUrl) {
    return (
      <a
        href={source.url}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-block"
        aria-label={`Read article from ${source.name}`}
      >
        {badge}
      </a>
    );
  }

  return badge;
}
