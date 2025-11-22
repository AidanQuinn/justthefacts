/**
 * Type definitions for the news aggregator component
 */

export interface ImportanceScores {
  impact: number;
  conflict: number;
  ramifications: number;
  accountability: number;
  informed_public: number;
  citizen_responsibility: number;
  transparency: number;
}

export interface Source {
  name: string;
  lean: 'left' | 'center' | 'right';
  url: string;
}

export interface Story {
  title: string;
  summary: string;
  sources: Source[];
  timestamp: string;
  cluster_size: number;
  story_id: string;
  importance_scores: ImportanceScores;
  importance_avg: number;
}

export interface NewsIndex {
  available_dates: string[];
  latest_date: string;
}

export interface NewsResponse {
  stories: Story[];
  date: string;
}

export interface DateInfo {
  available_dates: string[];
  latest_date: string;
}
