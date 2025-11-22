/**
 * ImportanceScores Component
 * Visual display of the 7 importance dimensions
 */

import React, { useState } from 'react';
import { ImportanceScores as IScores } from '../types/news';
import { IMPORTANCE_LABELS } from '../lib/config';

interface ImportanceScoresProps {
  scores: IScores;
  average: number;
}

export default function ImportanceScores({ scores, average }: ImportanceScoresProps) {
  const [expanded, setExpanded] = useState(false);

  // Sort scores by value (descending) for better visual hierarchy
  const sortedScores = Object.entries(scores)
    .sort(([, a], [, b]) => b - a)
    .slice(0, expanded ? 7 : 3);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-semibold text-gray-700 uppercase tracking-wide">
          Importance
        </h4>
        <span className="text-sm font-bold text-gray-900" title="Average importance score">
          {average.toFixed(1)}/10
        </span>
      </div>

      <div className="space-y-1.5">
        {sortedScores.map(([key, value]) => (
          <div key={key} className="space-y-0.5">
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-600">
                {IMPORTANCE_LABELS[key as keyof IScores]}
              </span>
              <span className="font-medium text-gray-900">{value.toFixed(1)}</span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-1.5 overflow-hidden">
              <div
                className="bg-gradient-to-r from-blue-500 to-blue-600 h-full rounded-full transition-all duration-300"
                style={{ width: `${(value / 10) * 100}%` }}
                role="progressbar"
                aria-valuenow={value}
                aria-valuemin={0}
                aria-valuemax={10}
                aria-label={`${IMPORTANCE_LABELS[key as keyof IScores]}: ${value} out of 10`}
              />
            </div>
          </div>
        ))}
      </div>

      {Object.keys(scores).length > 3 && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-blue-600 hover:text-blue-700 font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded px-1 -mx-1"
          aria-expanded={expanded}
        >
          {expanded ? 'Show less' : `Show all ${Object.keys(scores).length} dimensions`}
        </button>
      )}
    </div>
  );
}
