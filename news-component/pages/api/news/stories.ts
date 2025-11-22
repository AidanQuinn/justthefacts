/**
 * API Route: GET /api/news/stories?date=YYYY-MM-DD
 * Returns stories for specific date (defaults to latest if no date provided)
 */

import { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';
import { NEWS_DATA_PATH } from '../../../lib/config';
import { Story, NewsResponse } from '../../../types/news';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<NewsResponse | { error: string }>
) {
  // Only allow GET requests
  if (req.method !== 'GET') {
    res.setHeader('Allow', ['GET']);
    return res.status(405).json({ error: `Method ${req.method} Not Allowed` });
  }

  try {
    let targetDate: string;

    // If no date provided, use latest
    if (!req.query.date) {
      const indexPath = path.join(NEWS_DATA_PATH, 'index.json');
      if (!fs.existsSync(indexPath)) {
        return res.status(404).json({ error: 'News index not found' });
      }
      const indexData = JSON.parse(fs.readFileSync(indexPath, 'utf-8'));
      targetDate = indexData.latest_date;
    } else {
      targetDate = req.query.date as string;
    }

    // Validate date format (YYYY-MM-DD)
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(targetDate)) {
      return res.status(400).json({ error: 'Invalid date format. Use YYYY-MM-DD' });
    }

    // Format filename (remove hyphens from date)
    const dateForFilename = targetDate.replace(/-/g, '');
    const storiesPath = path.join(NEWS_DATA_PATH, `stories_${dateForFilename}.json`);

    // Check if stories file exists
    if (!fs.existsSync(storiesPath)) {
      return res.status(404).json({ error: `No stories found for date ${targetDate}` });
    }

    // Read and parse stories file
    const storiesData = fs.readFileSync(storiesPath, 'utf-8');
    const stories: Story[] = JSON.parse(storiesData);

    // Set cache headers (cache for 1 hour for past dates, 5 minutes for today)
    const isToday = targetDate === new Date().toISOString().split('T')[0];
    const cacheTime = isToday ? 300 : 3600;
    res.setHeader('Cache-Control', `public, s-maxage=${cacheTime}, stale-while-revalidate=${cacheTime * 2}`);

    return res.status(200).json({
      stories,
      date: targetDate,
    });
  } catch (error) {
    console.error('Error reading stories:', error);
    return res.status(500).json({ error: 'Failed to read stories' });
  }
}
