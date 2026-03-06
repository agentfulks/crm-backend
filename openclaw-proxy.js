#!/usr/bin/env node
/**
 * OpenClaw + VC Outreach Dashboard Proxy
 * 
 * This server runs on port 8080 and serves:
 * - /dashboard/* -> VC Outreach Frontend (static files)
 * - /* -> OpenClaw Control UI (proxied to localhost:8081)
 * 
 * Rollback: Run ./rollback-openclaw.sh
 */

const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');

const app = express();
const PORT = 8080;
const OPENCLAW_PORT = 8081;  // OpenClaw runs here internally

// Serve VC Outreach Dashboard on /dashboard
app.use('/dashboard', express.static('/data/workspace/frontend/dist', {
  fallthrough: false
}));

// Redirect /dashboard to /dashboard/ (add trailing slash)
app.get('/dashboard', (req, res) => {
  res.redirect('/dashboard/');
});

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    services: {
      proxy: 'running',
      openclaw: 'http://localhost:' + OPENCLAW_PORT,
      dashboard: '/dashboard/'
    }
  });
});

// Proxy all other requests to OpenClaw
app.use('/', createProxyMiddleware({
  target: 'http://localhost:' + OPENCLAW_PORT,
  changeOrigin: true,
  ws: true,  // WebSocket support
  onError: (err, req, res) => {
    console.error('Proxy error:', err.message);
    res.status(502).send(`
      <h1>Service Unavailable</h1>
      <p>OpenClaw gateway is not responding.</p>
      <p>Error: ${err.message}</p>
      <p><a href="/dashboard/">Try VC Outreach Dashboard</a></p>
      <p><a href="/health">Check Health</a></p>
    `);
  }
}));

app.listen(PORT, '0.0.0.0', () => {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║  OpenClaw + VC Outreach Proxy Running                      ║
╠════════════════════════════════════════════════════════════╣
║  Port:        ${PORT}                                         ║
║  OpenClaw:    http://localhost:${OPENCLAW_PORT} (internal)    ║
║  Dashboard:   http://localhost:${PORT}/dashboard/            ║
╠════════════════════════════════════════════════════════════╣
║  URLs:                                                     ║
║    • http://marvy.up.railway.app/          → OpenClaw     ║
║    • http://marvy.up.railway.app/dashboard → VC Outreach  ║
╠════════════════════════════════════════════════════════════╣
║  ROLLBACK (if needed):                                     ║
║    ./rollback-openclaw.sh                                  ║
╚════════════════════════════════════════════════════════════╝
  `);
});
