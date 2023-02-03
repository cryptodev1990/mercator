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
  poweredByHeader: false,
  staticPageGenerationTimeout: 1000,
  webpack: (config, { isServer }) => {
    if (!isServer) config.resolve.fallback.fs = false;
    // config.optimization.minimize = false;
    config.experiments = { asyncWebAssembly: true, layers: true };
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
