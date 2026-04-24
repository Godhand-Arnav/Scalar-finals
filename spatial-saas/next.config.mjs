/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/health',
        destination: 'http://localhost:7860/health',
      },
      {
        source: '/tasks',
        destination: 'http://localhost:7860/tasks',
      },
      {
        source: '/actions',
        destination: 'http://localhost:7860/actions',
      },
      {
        source: '/reset',
        destination: 'http://localhost:7860/reset',
      },
      {
        source: '/step',
        destination: 'http://localhost:7860/step',
      },
      {
        source: '/state',
        destination: 'http://localhost:7860/state',
      },
      {
        source: '/leaderboard',
        destination: 'http://localhost:7860/leaderboard',
      },
      {
        source: '/episodes/:path*',
        destination: 'http://localhost:7860/episodes/:path*',
      },
    ];
  },
};

export default nextConfig;
