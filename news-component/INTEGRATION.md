# Integration Guide

This guide provides step-by-step instructions for integrating the News Component into your existing Next.js project.

## Quick Start (5 minutes)

### 1. Copy Component Files

From this directory, copy the necessary files to your Next.js project:

```bash
# Assuming you're in the news-component directory
# and your Next.js project is at /path/to/your/project

# Copy components
cp -r components /path/to/your/project/

# Copy types
cp -r types /path/to/your/project/

# Copy hooks
cp -r hooks /path/to/your/project/

# Copy lib
cp -r lib /path/to/your/project/

# Copy API routes
cp -r pages/api/news /path/to/your/project/pages/api/

# Optional: Copy the example page
cp pages/news.tsx /path/to/your/project/pages/
```

### 2. Install Dependencies

```bash
cd /path/to/your/project
npm install swr date-fns @tailwindcss/typography
```

### 3. Configure Environment

Create or update `.env.local`:

```bash
# Point to your news_data directory
NEWS_DATA_PATH=./news_data
```

### 4. Update Tailwind Config

Add the typography plugin to your `tailwind.config.js`:

```javascript
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
```

### 5. Use the Component

```typescript
// pages/news.tsx
import NewsHub from '../components/NewsHub';

export default function NewsPage() {
  return (
    <main className="min-h-screen bg-gray-50">
      <NewsHub />
    </main>
  );
}
```

## Advanced Integration

### Custom Layout Integration

If you want to integrate the news component into a page with your own layout:

```typescript
// pages/index.tsx
import Layout from '../components/Layout'; // Your layout
import NewsHub from '../components/NewsHub';

export default function HomePage() {
  return (
    <Layout>
      <section className="container mx-auto py-12">
        <h1 className="text-4xl font-bold mb-8">Welcome</h1>
        <p className="mb-12">Check out the latest news:</p>

        <NewsHub />
      </section>
    </Layout>
  );
}
```

### Custom Styling

To override or extend the default styles:

1. **Create a custom wrapper component:**

```typescript
// components/CustomNewsHub.tsx
import NewsHub from './NewsHub';

export default function CustomNewsHub() {
  return (
    <div className="my-custom-wrapper">
      <style jsx>{`
        .my-custom-wrapper {
          /* Your custom styles */
        }
      `}</style>
      <NewsHub />
    </div>
  );
}
```

2. **Modify the source components directly** in the `components/` directory

### Using Individual Components

You can also use individual components separately:

```typescript
import { useStories } from '../hooks/useNews';
import StoryCard from '../components/StoryCard';

export default function CustomNewsView() {
  const { stories, isLoading } = useStories('2025-11-21');

  if (isLoading) return <div>Loading...</div>;

  return (
    <div className="grid grid-cols-2 gap-4">
      {stories.slice(0, 4).map(story => (
        <StoryCard key={story.story_id} story={story} />
      ))}
    </div>
  );
}
```

### Server-Side Rendering (SSR)

For better SEO and initial load performance:

```typescript
// pages/news.tsx
import { GetServerSideProps } from 'next';
import NewsHub from '../components/NewsHub';
import fs from 'fs';
import path from 'path';

export const getServerSideProps: GetServerSideProps = async () => {
  // Pre-fetch data on the server
  const newsDataPath = process.env.NEWS_DATA_PATH || path.join(process.cwd(), 'news_data');
  const indexPath = path.join(newsDataPath, 'index.json');
  const indexData = JSON.parse(fs.readFileSync(indexPath, 'utf-8'));

  return {
    props: {
      initialDate: indexData.latest_date,
    },
  };
};

export default function NewsPage({ initialDate }: { initialDate: string }) {
  return (
    <main className="min-h-screen bg-gray-50">
      <NewsHub initialDate={initialDate} />
    </main>
  );
}
```

### Static Site Generation (SSG)

For even better performance with static builds:

```typescript
// pages/news/[date].tsx
import { GetStaticPaths, GetStaticProps } from 'next';
import NewsHub from '../../components/NewsHub';
import fs from 'fs';
import path from 'path';

export const getStaticPaths: GetStaticPaths = async () => {
  const newsDataPath = process.env.NEWS_DATA_PATH || path.join(process.cwd(), 'news_data');
  const indexPath = path.join(newsDataPath, 'index.json');
  const indexData = JSON.parse(fs.readFileSync(indexPath, 'utf-8'));

  const paths = indexData.available_dates.map((date: string) => ({
    params: { date },
  }));

  return { paths, fallback: 'blocking' };
};

export const getStaticProps: GetStaticProps = async ({ params }) => {
  return {
    props: {
      initialDate: params?.date || null,
    },
    revalidate: 300, // Revalidate every 5 minutes
  };
};

export default function NewsDatePage({ initialDate }: { initialDate: string | null }) {
  return (
    <main className="min-h-screen bg-gray-50">
      <NewsHub initialDate={initialDate} />
    </main>
  );
}
```

## Directory Structure Options

### Option 1: Flat Structure (Recommended for small projects)

```
your-nextjs-project/
├── components/
│   ├── NewsHub.tsx
│   ├── StoryCard.tsx
│   ├── DatePicker.tsx
│   ├── SourceBadge.tsx
│   ├── ImportanceScores.tsx
│   └── ... (your other components)
├── types/
│   └── news.ts
├── hooks/
│   └── useNews.ts
└── ...
```

### Option 2: Namespaced Structure (Recommended for larger projects)

```
your-nextjs-project/
├── components/
│   ├── news/
│   │   ├── NewsHub.tsx
│   │   ├── StoryCard.tsx
│   │   ├── DatePicker.tsx
│   │   ├── SourceBadge.tsx
│   │   └── ImportanceScores.tsx
│   └── ... (your other components)
├── types/
│   └── news.ts
└── ...
```

Then update imports:
```typescript
import NewsHub from '../components/news/NewsHub';
```

### Option 3: Feature-based Structure

```
your-nextjs-project/
├── features/
│   └── news/
│       ├── components/
│       │   ├── NewsHub.tsx
│       │   ├── StoryCard.tsx
│       │   ├── DatePicker.tsx
│       │   ├── SourceBadge.tsx
│       │   └── ImportanceScores.tsx
│       ├── types/
│       │   └── news.ts
│       ├── hooks/
│       │   └── useNews.ts
│       └── lib/
│           └── config.ts
└── ...
```

Then update imports:
```typescript
import NewsHub from '../features/news/components/NewsHub';
```

## Configuration Options

### Custom News Data Path

If your `news_data` directory is in a non-standard location:

**Option 1: Environment Variable**
```bash
# .env.local
NEWS_DATA_PATH=/absolute/path/to/news_data
```

**Option 2: Update config.ts**
```typescript
// lib/config.ts
export const NEWS_DATA_PATH = '/absolute/path/to/news_data';
```

### Custom Color Scheme

Match your brand colors:

```typescript
// lib/config.ts
export const LEAN_COLORS = {
  left: {
    bg: 'bg-purple-50',    // Your brand color
    text: 'text-purple-700',
    border: 'border-purple-200',
    hover: 'hover:bg-purple-100',
  },
  center: {
    bg: 'bg-gray-50',
    text: 'text-gray-700',
    border: 'border-gray-200',
    hover: 'hover:bg-gray-100',
  },
  right: {
    bg: 'bg-orange-50',    // Your brand color
    text: 'text-orange-700',
    border: 'border-orange-200',
    hover: 'hover:bg-orange-100',
  },
};
```

## Deployment Considerations

### Vercel

1. Ensure `news_data` directory is committed to your repository
2. Set environment variable in Vercel dashboard:
   ```
   NEWS_DATA_PATH=./news_data
   ```

### Netlify

1. Add to `netlify.toml`:
   ```toml
   [build.environment]
     NEWS_DATA_PATH = "./news_data"
   ```

### Docker

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
COPY news_data ./news_data

ENV NEWS_DATA_PATH=./news_data

RUN npm run build

CMD ["npm", "start"]
```

## Common Issues

### TypeScript Errors

If you get import errors:
1. Ensure `tsconfig.json` includes the new directories
2. Restart your TypeScript server
3. Delete `.next` folder and rebuild

### Styles Not Applying

1. Verify Tailwind config includes component paths
2. Ensure `@tailwind` directives are in your CSS
3. Clear Next.js cache: `rm -rf .next`

### API Routes 404

1. Ensure API files are in `pages/api/news/`
2. Restart dev server
3. Check for build errors

## Performance Optimization

### Image Optimization

If you add images to stories in the future:

```typescript
import Image from 'next/image';

// In StoryCard.tsx
<Image
  src={story.imageUrl}
  alt={story.title}
  width={600}
  height={400}
  loading="lazy"
/>
```

### Code Splitting

Components are automatically code-split by Next.js. For further optimization:

```typescript
import dynamic from 'next/dynamic';

const NewsHub = dynamic(() => import('../components/NewsHub'), {
  loading: () => <p>Loading news...</p>,
  ssr: true,
});
```

### Caching Strategy

Adjust SWR cache times in `hooks/useNews.ts`:

```typescript
export function useStories(date: string | null) {
  const { data, error, isLoading } = useSWR<NewsResponse>(url, fetcher, {
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
    refreshInterval: 600000, // 10 minutes instead of 5
    dedupingInterval: 60000,  // Dedupe requests within 1 minute
  });
}
```

## Next Steps

1. Customize the styling to match your brand
2. Add analytics tracking to story clicks
3. Implement user preferences (favorite sources, topics)
4. Add sharing functionality
5. Create RSS feed from the API routes
6. Add search/filter capabilities

## Support

For additional help:
- Check the main README.md
- Review the TypeScript types in `types/news.ts`
- Examine the example page in `pages/news.tsx`
- Review API route implementations
