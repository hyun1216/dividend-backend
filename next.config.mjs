/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  async redirects() {
    return [
      {
        source: '/:path*',
        has: [
          {
            type: 'host',
            value: 'www.mydividend.co.kr',
          },
        ],
        destination: 'https://mydividend.co.kr/:path*',
        permanent: true,
      },
    ];
  },
  async rewrites() {
    const isDev = process.env.NODE_ENV === 'development';
    return [
      {
        source: '/api/posts/:path*',
        destination: isDev ? 'http://127.0.0.1:5000/api/posts/:path*' : '/api/index.py',
      },
      {
        source: '/api/posts',
        destination: isDev ? 'http://127.0.0.1:5000/api/posts' : '/api/index.py',
      },
      {
        source: '/api/init_db',
        destination: isDev ? 'http://127.0.0.1:5000/api/init_db' : '/api/index.py',
      },
    ];
  },
};

export default nextConfig;
