/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx}',
  ],
  safelist: [
    // Source badge colors - needed because they're dynamically applied
    'bg-blue-100',
    'bg-blue-200',
    'text-blue-800',
    'border-blue-300',
    'hover:bg-blue-200',
    'bg-gray-100',
    'bg-gray-200',
    'text-gray-800',
    'border-gray-300',
    'hover:bg-gray-200',
    'bg-red-100',
    'bg-red-200',
    'text-red-800',
    'border-red-300',
    'hover:bg-red-200',
  ],
  theme: {
    extend: {
      typography: {
        DEFAULT: {
          css: {
            maxWidth: 'none',
            // Minimize default prose styling to maintain minimalist look
            '--tw-prose-body': 'inherit',
            '--tw-prose-headings': 'inherit',
            '--tw-prose-links': 'inherit',
            '--tw-prose-bold': 'inherit',
            '--tw-prose-bullets': 'inherit',
            '--tw-prose-quotes': 'inherit',
            // Remove default margins from prose to let custom component styles take over
            p: {
              marginTop: '0',
              marginBottom: '0',
            },
            ul: {
              marginTop: '0',
              marginBottom: '0',
            },
            ol: {
              marginTop: '0',
              marginBottom: '0',
            },
            li: {
              marginTop: '0',
              marginBottom: '0',
            },
          },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
