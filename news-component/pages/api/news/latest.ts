/**
 * API Route: GET /api/news/latest
 * Returns latest stories (convenience endpoint that redirects to stories?date=latest)
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
    // Read index to get latest date
    const indexPath = path.join(NEWS_DATA_PATH, 'index.json');
    if (!fs.existsSync(indexPath)) {
      return res.status(404).json({ error: 'News index not found' });
    }

    const indexData = JSON.parse(fs.readFileSync(indexPath, 'utf-8'));
    const latestDate = indexData.latest_date;

    // Format filename (remove hyphens from date)
    const dateForFilename = latestDate.replace(/-/g, '');
    const storiesPath = path.join(NEWS_DATA_PATH, `stories_${dateForFilename}.json`);

    // Check if stories file exists
    if (!fs.existsSync(storiesPath)) {
      return res.status(404).json({ error: 'Latest stories not found' });
    }

    // Read and parse stories file
    const storiesData = fs.readFileSync(storiesPath, 'utf-8');
    const stories: Story[] = JSON.parse(storiesData);

    // Set cache headers (cache for 5 minutes since this is latest)
    res.setHeader('Cache-Control', 'public, s-maxage=300, stale-while-revalidate=600');

    return res.status(200).json({
      stories,
      date: latestDate,
    });
  } catch (error) {
    console.error('Error reading latest stories:', error);
    return res.status(500).json({ error: 'Failed to read latest stories' });
  }
}
