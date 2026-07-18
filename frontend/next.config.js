/** @type {import('next').NextConfig} */
// BUILD_TARGET=tauri produces a static export bundled into the Windows
// shell (Sprint 4) — the hosted web deployment keeps the normal SSR build.
// Frontend has no middleware/API routes and every data fetch already goes
// through lib/api.ts against NEXT_PUBLIC_API_URL with credentials:'include',
// so static export needs no auth/routing rework.
const isTauriBuild = process.env.BUILD_TARGET === 'tauri'

const nextConfig = {
  reactStrictMode: true,
  devIndicators: false,
  ...(isTauriBuild
    ? {
        output: 'export',
        images: { unoptimized: true },
      }
    : {}),
}
module.exports = nextConfig
