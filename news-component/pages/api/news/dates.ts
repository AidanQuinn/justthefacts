/**
 * API Route: GET /api/news/dates
 * Returns list of available dates from index.json
 */

import { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';
import { NEWS_DATA_PATH } from '../../../lib/config';
import { DateInfo } from '../../../types/news';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<DateInfo | { error: string }>
) {
  // Only allow GET requests
  if (req.method !== 'GET') {
    res.setHeader('Allow', ['GET']);
    return res.status(405).json({ error: `Method ${req.method} Not Allowed` });
  }

  try {
    const indexPath = path.join(NEWS_DATA_PATH, 'index.json');

    // Check if index file exists
    if (!fs.existsSync(indexPath)) {
      return res.status(404).json({ error: 'News index not found' });
    }

    // Read and parse index file
    const indexData = fs.readFileSync(indexPath, 'utf-8');
    const index = JSON.parse(indexData);

    // Validate data structure
    if (!index.available_dates || !Array.isArray(index.available_dates)) {
      return res.status(500).json({ error: 'Invalid index data structure' });
    }

    // Set cache headers (cache for 5 minutes)
    res.setHeader('Cache-Control', 'public, s-maxage=300, stale-while-revalidate=600');

    return res.status(200).json({
      available_dates: index.available_dates,
      latest_date: index.latest_date,
    });
  } catch (error) {
    console.error('Error reading news dates:', error);
    return res.status(500).json({ error: 'Failed to read news dates' });
  }
}
