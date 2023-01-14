/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
};

const securityHeaders = [
  {
    key: "Cross-Origin-Opener-Policy",
    value: "same-origin",
  },
  {
    key: "Cross-Origin-Embedder-Policy",
    value: "require-corp",
  },
];

module.exports = {
  ...nextConfig,
  webpack: (config, { isServer }) => {
    if (!isServer) config.resolve.fallback.fs = false;
    return config;
  },
  async headers() {
    return [
      {
        source: "/api/sql",
        headers: [
          ...securityHeaders,
          { key: "Content-Type", value: "application/wasm" },
        ],
      },
    ];
  },
};
