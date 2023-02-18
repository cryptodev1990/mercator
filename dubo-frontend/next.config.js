/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
};

const CopyWebpackPlugin = require("copy-webpack-plugin");

const withBundleAnalyzer = require("@next/bundle-analyzer")({
  enabled: process.env.ANALYZE === "true",
});

const config = {
  ...nextConfig,
  poweredByHeader: false,
  staticPageGenerationTimeout: 1000,
  webpack: (config, { isServer }) => {
    if (!isServer) config.resolve.fallback.fs = false;

    config.experiments = { asyncWebAssembly: true };

    config.plugins.push(
      new CopyWebpackPlugin({
        patterns: [
          {
            from: "./node_modules/sql.js/dist/sql-wasm.wasm",
            to: "./static/chunks",
          },
        ],
      })
    );

    return config;
  },
};

module.exports = withBundleAnalyzer(config);
