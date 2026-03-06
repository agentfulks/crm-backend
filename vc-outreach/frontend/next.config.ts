import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'standalone',
  env: {
    MATON_API_KEY: process.env.MATON_API_KEY,
  },
};

export default nextConfig;
