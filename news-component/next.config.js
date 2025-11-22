/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,

  // Configure to use Pages Router
  pageExtensions: ['tsx', 'ts', 'jsx', 'js'],

  // Environment variables
  env: {
    NEWS_DATA_PATH: process.env.NEWS_DATA_PATH || '../news_data',
  },
}

module.exports = nextConfig
