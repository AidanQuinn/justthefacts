# News Component Package - Index

Welcome to the News Component Package! This index will help you navigate the documentation and find what you need quickly.

## Quick Navigation

### Getting Started (Choose One)

| Document | Best For | Time Required |
|----------|----------|---------------|
| [QUICKSTART.md](./QUICKSTART.md) | First-time users who want to see it working fast | 5 minutes |
| [README.md](./README.md) | Complete understanding before implementation | 15 minutes |
| [INTEGRATION.md](./INTEGRATION.md) | Integrating into existing Next.js project | 10 minutes |

### I Want To...

#### See It Working
→ [QUICKSTART.md](./QUICKSTART.md) - Section: "Option A: Test Standalone"

#### Integrate Into My Project
→ [QUICKSTART.md](./QUICKSTART.md) - Section: "Option B: Integrate into Your Next.js Project"
→ [INTEGRATION.md](./INTEGRATION.md) - For advanced options

#### Understand the Architecture
→ [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) - Complete technical overview
→ [README.md](./README.md) - Section: "Component Architecture"

#### See Usage Examples
→ [EXAMPLES.md](./EXAMPLES.md) - 8 real-world examples including:
- Simple standalone page
- Homepage widget
- Blog post sidebar
- Mobile interface
- Email digest
- Search & filter
- And more...

#### Customize the Component
→ [README.md](./README.md) - Section: "Customization"
→ [INTEGRATION.md](./INTEGRATION.md) - Section: "Configuration Options"

#### Troubleshoot Issues
→ [QUICKSTART.md](./QUICKSTART.md) - Section: "Troubleshooting"
→ [README.md](./README.md) - Section: "Troubleshooting"

## File Organization

### Documentation (5 files)
```
├── INDEX.md              ← You are here - Navigation guide
├── QUICKSTART.md         ← 5-minute getting started
├── README.md             ← Complete reference documentation
├── INTEGRATION.md        ← Advanced integration guide
├── EXAMPLES.md           ← 8 real-world usage examples
└── PROJECT_SUMMARY.md    ← Technical overview and architecture
```

### Source Code (14 files)
```
├── components/           ← React components (5 files)
│   ├── NewsHub.tsx      ← Main container
│   ├── StoryCard.tsx    ← Story display
│   ├── DatePicker.tsx   ← Date navigation
│   ├── SourceBadge.tsx  ← Source indicator
│   └── ImportanceScores.tsx ← Score visualization
│
├── pages/               ← Next.js pages and API routes (5 files)
│   ├── _app.tsx        ← App wrapper
│   ├── news.tsx        ← Example page
│   └── api/news/       ← API routes
│       ├── dates.ts    ← GET available dates
│       ├── stories.ts  ← GET stories by date
│       └── latest.ts   ← GET latest stories
│
├── types/              ← TypeScript types (1 file)
│   └── news.ts        ← All type definitions
│
├── hooks/              ← React hooks (1 file)
│   └── useNews.ts     ← Data fetching hooks
│
├── lib/                ← Configuration (1 file)
│   └── config.ts      ← Settings and constants
│
└── styles/             ← Styling (1 file)
    └── globals.css    ← Global CSS
```

### Configuration (6 files)
```
├── package.json       ← Dependencies and scripts
├── tsconfig.json      ← TypeScript config
├── tailwind.config.js ← Tailwind CSS config
├── postcss.config.js  ← PostCSS config
├── next.config.js     ← Next.js config
└── .gitignore         ← Git ignore rules
```

### Environment
```
├── .env.example       ← Example environment variables
└── .env.local         ← Your local configuration
```

## Documentation by Use Case

### For Developers

#### First-Time Setup
1. [QUICKSTART.md](./QUICKSTART.md) - Get it running
2. [README.md](./README.md) - Understand what you have
3. [EXAMPLES.md](./EXAMPLES.md) - See what's possible

#### Integration
1. [INTEGRATION.md](./INTEGRATION.md) - Integration options
2. [README.md](./README.md#installation) - Installation steps
3. [QUICKSTART.md](./QUICKSTART.md#option-b) - Quick integration

#### Customization
1. [README.md](./README.md#customization) - Customization guide
2. [lib/config.ts](./lib/config.ts) - Configuration file
3. [EXAMPLES.md](./EXAMPLES.md) - Customization examples

### For Project Managers

#### Understand the Scope
→ [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md) - Complete overview

#### Technical Specifications
→ [README.md](./README.md) - Features and requirements

#### Implementation Estimate
→ [QUICKSTART.md](./QUICKSTART.md) - 5 minutes to test
→ [INTEGRATION.md](./INTEGRATION.md) - 1-2 hours to integrate

### For Designers

#### Visual Design
→ [README.md](./README.md#design-system) - Design system
→ [lib/config.ts](./lib/config.ts) - Color configuration

#### UX Flow
→ [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md#user-experience) - UX features
→ [EXAMPLES.md](./EXAMPLES.md) - Interface examples

### For QA/Testers

#### Testing Setup
→ [QUICKSTART.md](./QUICKSTART.md#option-a) - Standalone test setup

#### Features to Test
→ [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md#key-features) - Feature list

#### Browser Support
→ [README.md](./README.md#browser-support) - Supported browsers

## Key Components Deep Dive

### NewsHub.tsx
- **Purpose**: Main container component
- **Dependencies**: All other components, useNews hook
- **Props**: `initialDate?: string | null`
- **Location**: [components/NewsHub.tsx](./components/NewsHub.tsx)
- **Documentation**: [README.md](./README.md#main-components)

### StoryCard.tsx
- **Purpose**: Display individual story
- **Dependencies**: SourceBadge, ImportanceScores
- **Props**: `story: Story`
- **Location**: [components/StoryCard.tsx](./components/StoryCard.tsx)
- **Example**: [EXAMPLES.md](./EXAMPLES.md#example-2-homepage-widget)

### DatePicker.tsx
- **Purpose**: Date navigation
- **Dependencies**: date-fns
- **Props**: `availableDates, selectedDate, onDateChange, isLoading`
- **Location**: [components/DatePicker.tsx](./components/DatePicker.tsx)

### SourceBadge.tsx
- **Purpose**: Display news source with lean indicator
- **Dependencies**: None
- **Props**: `source: Source, showUrl?: boolean`
- **Location**: [components/SourceBadge.tsx](./components/SourceBadge.tsx)

### ImportanceScores.tsx
- **Purpose**: Visualize importance dimensions
- **Dependencies**: None
- **Props**: `scores: ImportanceScores, average: number`
- **Location**: [components/ImportanceScores.tsx](./components/ImportanceScores.tsx)

## API Routes Deep Dive

### GET /api/news/dates
- **Returns**: Available dates and latest date
- **Cache**: 5 minutes
- **Location**: [pages/api/news/dates.ts](./pages/api/news/dates.ts)
- **Example**: `curl http://localhost:3000/api/news/dates`

### GET /api/news/stories
- **Parameters**: `?date=YYYY-MM-DD` (optional)
- **Returns**: Stories array for specified date
- **Cache**: 5 min (current) / 1 hour (past)
- **Location**: [pages/api/news/stories.ts](./pages/api/news/stories.ts)
- **Example**: `curl http://localhost:3000/api/news/stories?date=2025-11-21`

### GET /api/news/latest
- **Returns**: Latest stories
- **Cache**: 5 minutes
- **Location**: [pages/api/news/latest.ts](./pages/api/news/latest.ts)
- **Example**: `curl http://localhost:3000/api/news/latest`

## Common Tasks

### Change Political Lean Colors
1. Open [lib/config.ts](./lib/config.ts)
2. Modify `LEAN_COLORS` object
3. Use Tailwind color classes

### Add New Importance Dimension
1. Update [types/news.ts](./types/news.ts) - Add to `ImportanceScores`
2. Update [lib/config.ts](./lib/config.ts) - Add to `IMPORTANCE_LABELS`
3. Ensure backend outputs the new dimension

### Change Grid Layout
1. Open [components/NewsHub.tsx](./components/NewsHub.tsx)
2. Find the grid div (search for "grid grid-cols")
3. Modify the column classes (e.g., `lg:grid-cols-4` for 4 columns)

### Adjust Summary Truncation
1. Open [components/StoryCard.tsx](./components/StoryCard.tsx)
2. Find `shouldTruncate` variable
3. Change the number (default: 400 characters)

### Modify Cache Duration
1. Open [hooks/useNews.ts](./hooks/useNews.ts)
2. Find `refreshInterval` option
3. Change the value (in milliseconds, default: 300000 = 5 min)

## Cheat Sheet

### Quick Commands
```bash
# Test standalone
npm install && npm run dev

# Type check
npm run type-check

# Build for production
npm run build

# Start production server
npm start
```

### Environment Variables
```bash
# Required
NEWS_DATA_PATH=./news_data

# Example paths
NEWS_DATA_PATH=/absolute/path/to/news_data
NEWS_DATA_PATH=../news_data
NEWS_DATA_PATH=./news_data
```

### Import Statements
```typescript
// Main component
import NewsHub from '../components/NewsHub';

// Individual components
import StoryCard from '../components/StoryCard';
import DatePicker from '../components/DatePicker';
import SourceBadge from '../components/SourceBadge';
import ImportanceScores from '../components/ImportanceScores';

// Hooks
import { useDates, useStories, useLatestStories } from '../hooks/useNews';

// Types
import { Story, Source, ImportanceScores } from '../types/news';
```

## Need Help?

### Issue Type → Solution

| Issue | Check This |
|-------|-----------|
| Installation errors | [QUICKSTART.md](./QUICKSTART.md#troubleshooting) |
| Integration problems | [INTEGRATION.md](./INTEGRATION.md#common-issues) |
| Styling not working | [README.md](./README.md#troubleshooting) |
| TypeScript errors | [tsconfig.json](./tsconfig.json) + restart TS server |
| API 404 errors | Verify files in `pages/api/news/` |
| Data not loading | Check `NEWS_DATA_PATH` in `.env.local` |

## Learning Path

### Beginner Path (30 minutes)
1. Read [QUICKSTART.md](./QUICKSTART.md) - 5 min
2. Run standalone setup - 5 min
3. Browse [EXAMPLES.md](./EXAMPLES.md) - 10 min
4. Experiment with customization - 10 min

### Intermediate Path (1 hour)
1. Read [README.md](./README.md) - 15 min
2. Read [INTEGRATION.md](./INTEGRATION.md) - 15 min
3. Integrate into your project - 30 min

### Advanced Path (2 hours)
1. Read all documentation - 30 min
2. Review source code - 30 min
3. Build custom features from [EXAMPLES.md](./EXAMPLES.md) - 60 min

## Document Summaries

| Document | Pages | Purpose | Read When |
|----------|-------|---------|-----------|
| INDEX.md | 1 | Navigation guide | First |
| QUICKSTART.md | 2 | Fast setup | Want to test quickly |
| README.md | 8 | Complete reference | Need full documentation |
| INTEGRATION.md | 6 | Advanced integration | Integrating into existing project |
| EXAMPLES.md | 10 | Usage examples | Building features |
| PROJECT_SUMMARY.md | 5 | Technical overview | Understanding architecture |

## Questions?

Still have questions? Here's where to look:

- **"How do I...?"** → [EXAMPLES.md](./EXAMPLES.md)
- **"What is...?"** → [README.md](./README.md) or [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)
- **"Why doesn't...?"** → [QUICKSTART.md](./QUICKSTART.md#troubleshooting) or [INTEGRATION.md](./INTEGRATION.md#common-issues)
- **"Can I...?"** → [EXAMPLES.md](./EXAMPLES.md) or [INTEGRATION.md](./INTEGRATION.md)

---

**Start Here**: [QUICKSTART.md](./QUICKSTART.md)

**Full Documentation**: [README.md](./README.md)

**Examples & Recipes**: [EXAMPLES.md](./EXAMPLES.md)
