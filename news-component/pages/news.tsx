/**
 * Example News Page
 * This shows how to use the NewsHub component in a Next.js page
 */

import React from 'react';
import Head from 'next/head';
import NewsHub from '../components/NewsHub';

export default function NewsPage() {
  return (
    <>
      <Head>
        <title>News Hub - Balanced News Aggregation</title>
        <meta
          name="description"
          content="Get balanced news coverage from across the political spectrum"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <main className="min-h-screen bg-gray-50">
        <NewsHub />
      </main>
    </>
  );
}
