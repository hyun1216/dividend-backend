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
};

export default nextConfig;
