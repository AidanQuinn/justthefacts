# News Component Package

A complete, production-ready Next.js component package for displaying news aggregator stories. Designed as an embeddable component that can be integrated into any Next.js website.

## Features

- **Balanced News Aggregation**: Displays stories from across the political spectrum (left, center, right)
- **Date Navigation**: Easy-to-use date picker for browsing historical news
- **Importance Scoring**: Visual representation of 7 importance dimensions for each story
- **Source Attribution**: Clear source badges with political lean indicators
- **Responsive Design**: Mobile-first design that works beautifully on all devices
- **Performance Optimized**: Built with SWR for efficient data fetching and caching
- **Accessible**: Full keyboard navigation and ARIA labels
- **TypeScript**: Complete type safety throughout

## Live Demo

Visit `/news` in your Next.js application after installation.

## Installation

### Option 1: Integrate into Existing Next.js Project

1. **Copy the component files** into your Next.js project:

```bash
# From the news-component directory, copy these folders into your project root:
cp -r components /path/to/your/nextjs/project/
cp -r types /path/to/your/nextjs/project/
cp -r hooks /path/to/your/nextjs/project/
cp -r lib /path/to/your/nextjs/project/
cp -r pages/api/news /path/to/your/nextjs/project/pages/api/
```

2. **Install required dependencies**:

```bash
npm install swr date-fns
# or
yarn add swr date-fns
# or
pnpm add swr date-fns
```

3. **Install Tailwind CSS** (if not already installed):

```bash
npm install -D tailwindcss postcss autoprefixer @tailwindcss/typography
npx tailwindcss init -p
```

4. **Update your `tailwind.config.js`**:

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    // Add any other directories you use
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
```

5. **Add Tailwind directives** to your `styles/globals.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

6. **Configure the news data path** by creating a `.env.local` file:

```bash
# .env.local
NEWS_DATA_PATH=./news_data
```

Adjust the path based on where your `news_data` folder is located relative to your Next.js project root.

7. **Update `lib/config.ts`** if needed to adjust the path resolution:

```typescript
export const NEWS_DATA_PATH = process.env.NEWS_DATA_PATH || path.join(process.cwd(), 'news_data');
```

### Option 2: Standalone Next.js Application

This component package can also run as a standalone Next.js application:

```bash
cd news-component
npm install
# or
yarn install
# or
pnpm install

# Copy the example env file
cp .env.example .env.local

# Update NEWS_DATA_PATH in .env.local to point to your news_data directory

# Run the development server
npm run dev
```

Visit `http://localhost:3000/news` to see the component in action.

## Usage

### Basic Usage in a Page

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

### With Initial Date

```typescript
import NewsHub from '../components/NewsHub';

export default function NewsPage() {
  return (
    <main className="min-h-screen bg-gray-50">
      <NewsHub initialDate="2025-11-21" />
    </main>
  );
}
```

### As an Embedded Component

```typescript
import NewsHub from '../components/NewsHub';

export default function HomePage() {
  return (
    <div>
      <header>{/* Your header */}</header>

      <section className="py-12">
        <NewsHub />
      </section>

      <footer>{/* Your footer */}</footer>
    </div>
  );
}
```

## API Routes

The component includes three API routes that serve the news data:

### GET /api/news/dates

Returns list of available dates and the latest date.

**Response:**
```json
{
  "available_dates": ["2025-11-21", "2025-11-20", ...],
  "latest_date": "2025-11-21"
}
```

### GET /api/news/stories?date=YYYY-MM-DD

Returns stories for a specific date. Defaults to latest if no date provided.

**Parameters:**
- `date` (optional): Date in YYYY-MM-DD format

**Response:**
```json
{
  "stories": [...],
  "date": "2025-11-21"
}
```

### GET /api/news/latest

Returns the latest stories (convenience endpoint).

**Response:**
```json
{
  "stories": [...],
  "date": "2025-11-21"
}
```

## Component Architecture

### Main Components

- **`NewsHub.tsx`**: Main container that manages state and orchestrates child components
- **`StoryCard.tsx`**: Displays individual story with title, summary, sources, and importance scores
- **`DatePicker.tsx`**: Calendar-based navigation for selecting dates
- **`SourceBadge.tsx`**: Displays news source with political lean indicator
- **`ImportanceScores.tsx`**: Visual bars showing the 7 importance dimensions

### Hooks

- **`useNews.ts`**: Custom hooks for data fetching
  - `useDates()`: Fetches available dates
  - `useStories(date)`: Fetches stories for a specific date
  - `useLatestStories()`: Fetches latest stories

### Types

All TypeScript types are defined in `types/news.ts`:
- `Story`: Complete story structure
- `Source`: News source with lean information
- `ImportanceScores`: The 7 importance dimensions
- `DateInfo`: Available dates information
- `NewsResponse`: API response structure

## Customization

### Styling

The component uses Tailwind CSS for styling. You can customize:

1. **Colors**: Edit `lib/config.ts` to change the lean colors:

```typescript
export const LEAN_COLORS = {
  left: {
    bg: 'bg-blue-50',
    text: 'text-blue-700',
    border: 'border-blue-200',
    hover: 'hover:bg-blue-100',
  },
  // ... customize other leans
};
```

2. **Layout**: Modify grid columns in `NewsHub.tsx`:

```typescript
// Change from 3 columns to 4 on large screens
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
```

3. **Typography**: Update importance labels in `lib/config.ts`:

```typescript
export const IMPORTANCE_LABELS = {
  impact: 'Impact',
  // ... customize labels
};
```

### Behavior

1. **Cache Duration**: Adjust cache times in API routes (`pages/api/news/*.ts`)
2. **Truncation Length**: Change summary truncation in `StoryCard.tsx` (default: 400 chars)
3. **Initial Scores Shown**: Modify `ImportanceScores.tsx` to show more/fewer dimensions initially

## Data Requirements

The component expects news data in the following structure:

```
news_data/
├── index.json              # Available dates and latest date
├── stories_20251121.json   # Stories for Nov 21, 2025
├── stories_20251120.json   # Stories for Nov 20, 2025
└── ...
```

### index.json format:
```json
{
  "available_dates": ["2025-11-21", "2025-11-20"],
  "latest_date": "2025-11-21"
}
```

### stories_YYYYMMDD.json format:
```json
[
  {
    "title": "Story title",
    "summary": "Full story summary...",
    "sources": [
      {
        "name": "Source Name",
        "lean": "left|center|right",
        "url": "https://..."
      }
    ],
    "timestamp": "2025-11-22T02:00:34.922609+00:00",
    "cluster_size": 5,
    "story_id": "story_0_20251121",
    "importance_scores": {
      "impact": 9.0,
      "conflict": 8.0,
      "ramifications": 9.0,
      "accountability": 7.0,
      "informed_public": 8.0,
      "citizen_responsibility": 6.0,
      "transparency": 7.0
    },
    "importance_avg": 7.71
  }
]
```

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile browsers: iOS Safari 12+, Chrome Android latest

## Performance

- **Code Splitting**: Automatic with Next.js
- **Caching**: SWR provides efficient client-side caching
- **Server Caching**: API routes include Cache-Control headers
- **Lazy Loading**: Images and content load progressively
- **Bundle Size**: ~50KB gzipped (excluding Next.js framework)

## Accessibility

- Full keyboard navigation
- ARIA labels on all interactive elements
- Semantic HTML structure
- Focus indicators on all focusable elements
- Screen reader friendly

## Troubleshooting

### "News index not found" error

- Verify `NEWS_DATA_PATH` in your `.env.local` file points to the correct directory
- Ensure `index.json` exists in the news_data directory
- Check file permissions

### Styles not working

- Ensure Tailwind CSS is properly installed and configured
- Verify `@tailwind` directives are in your global CSS file
- Check that your `tailwind.config.js` includes the component paths

### API routes returning 404

- Verify the API files are in `pages/api/news/` directory
- Ensure Next.js is running in development mode or has been built
- Check the console for any build errors

### Date picker not working

- Install `date-fns` package: `npm install date-fns`
- Clear Next.js cache: `rm -rf .next`
- Rebuild: `npm run build`

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Type check
npm run type-check

# Lint
npm run lint
```

## File Structure

```
news-component/
├── components/           # React components
│   ├── NewsHub.tsx      # Main container
│   ├── StoryCard.tsx    # Story display
│   ├── DatePicker.tsx   # Date navigation
│   ├── SourceBadge.tsx  # Source indicator
│   └── ImportanceScores.tsx # Score visualization
├── types/
│   └── news.ts          # TypeScript definitions
├── hooks/
│   └── useNews.ts       # Data fetching hooks
├── lib/
│   └── config.ts        # Configuration
├── pages/
│   ├── _app.tsx         # App wrapper
│   ├── news.tsx         # Example page
│   └── api/news/        # API routes
│       ├── dates.ts
│       ├── stories.ts
│       └── latest.ts
├── styles/
│   └── globals.css      # Global styles
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── next.config.js
└── README.md
```

## License

This component package is provided as-is for use with the Just The Facts news aggregator.

## Support

For issues or questions, please refer to the main project documentation or create an issue in the project repository.

## Changelog

### Version 1.0.0
- Initial release
- Full TypeScript support
- Responsive design
- Date navigation
- Importance score visualization
- Source attribution with political lean
- API routes for news data
- SWR integration for caching
