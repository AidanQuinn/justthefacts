# Quick Start Guide

Get the News Component up and running in 5 minutes.

## Prerequisites

- Node.js 18+ installed
- A Next.js project (or follow standalone setup below)

## Option A: Test Standalone (Fastest)

Test the component as a standalone Next.js app:

```bash
# Navigate to the news-component directory
cd news-component

# Install dependencies
npm install

# The .env.local file is already configured for this project
# It points to: /Users/aidan/Documents/Just_The_Facts/news_data

# Start the development server
npm run dev
```

Open [http://localhost:3000/news](http://localhost:3000/news) in your browser.

## Option B: Integrate into Your Next.js Project

### Step 1: Copy Files (1 minute)

```bash
# From the news-component directory
cp -r components /path/to/your/nextjs/project/
cp -r types /path/to/your/nextjs/project/
cp -r hooks /path/to/your/nextjs/project/
cp -r lib /path/to/your/nextjs/project/
cp -r pages/api/news /path/to/your/nextjs/project/pages/api/
```

### Step 2: Install Dependencies (1 minute)

```bash
cd /path/to/your/nextjs/project
npm install swr date-fns @tailwindcss/typography
```

### Step 3: Configure (1 minute)

Create `.env.local` in your project root:

```bash
NEWS_DATA_PATH=./news_data
```

Update `tailwind.config.js`:

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

### Step 4: Create a Page (1 minute)

Create `pages/news.tsx`:

```typescript
import NewsHub from '../components/NewsHub';

export default function NewsPage() {
  return (
    <main className="min-h-screen bg-gray-50">
      <NewsHub />
    </main>
  );
}
```

### Step 5: Run (1 minute)

```bash
npm run dev
```

Visit [http://localhost:3000/news](http://localhost:3000/news)

## Troubleshooting

### "Module not found: Can't resolve 'swr'"

Install the dependency:
```bash
npm install swr
```

### "News index not found"

Check your `.env.local` file - the `NEWS_DATA_PATH` should point to the correct location.

### Styles not showing

1. Ensure Tailwind is installed: `npm install -D tailwindcss`
2. Ensure `@tailwind` directives are in your CSS
3. Clear cache: `rm -rf .next && npm run dev`

### TypeScript errors

Restart your TypeScript server or run:
```bash
npm run type-check
```

## Next Steps

- Read [README.md](./README.md) for full documentation
- See [INTEGRATION.md](./INTEGRATION.md) for advanced integration options
- Check [EXAMPLES.md](./EXAMPLES.md) for usage examples

## File Structure

```
news-component/
├── components/          # React components
│   ├── NewsHub.tsx     # Main container
│   ├── StoryCard.tsx   # Story display
│   ├── DatePicker.tsx  # Date navigation
│   ├── SourceBadge.tsx # Source indicator
│   └── ImportanceScores.tsx # Score visualization
├── types/
│   └── news.ts         # TypeScript types
├── hooks/
│   └── useNews.ts      # Data fetching
├── lib/
│   └── config.ts       # Configuration
├── pages/
│   ├── _app.tsx        # App wrapper
│   ├── news.tsx        # Example page
│   └── api/news/       # API routes
│       ├── dates.ts
│       ├── stories.ts
│       └── latest.ts
└── styles/
    └── globals.css     # Global styles
```

## Key Features

- **Date Navigation**: Browse news by date
- **Political Balance**: Sources from left, center, and right
- **Importance Scoring**: 7 dimensions of importance
- **Responsive**: Works on all devices
- **Type-Safe**: Full TypeScript support
- **Performant**: SWR caching and optimization

## API Endpoints

Once running, these endpoints are available:

- `GET /api/news/latest` - Latest stories
- `GET /api/news/dates` - Available dates
- `GET /api/news/stories?date=YYYY-MM-DD` - Stories for specific date

## Customization

### Change Colors

Edit `lib/config.ts`:

```typescript
export const LEAN_COLORS = {
  left: { bg: 'bg-purple-50', ... },
  // ... customize
};
```

### Change Layout

Edit grid columns in `components/NewsHub.tsx`:

```typescript
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
```

### Adjust Cache Times

Edit `hooks/useNews.ts`:

```typescript
refreshInterval: 300000, // 5 minutes in milliseconds
```

## Support

Need help? Check:
- [README.md](./README.md) - Full documentation
- [INTEGRATION.md](./INTEGRATION.md) - Integration guide
- [EXAMPLES.md](./EXAMPLES.md) - Usage examples

Happy coding!
