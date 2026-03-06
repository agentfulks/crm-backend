const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');

const app = express();
const PORT = 4173;

// Proxy API requests to backend
// When you use app.use('/api', proxy), it strips /api by default
// So we need to add it back in the target
// /api/bdr/companies/ → http://localhost:8000/api/bdr/companies/
app.use('/api', createProxyMiddleware({
  target: 'http://localhost:8000/api',
  changeOrigin: true,
  pathRewrite: {
    '^/api': '',  // Remove /api since it's in the target
  },
  on: {
    // Rewrite any redirect Location headers so the browser follows them
    // through the proxy instead of going directly to localhost:8000
    proxyRes: (proxyRes) => {
      if (proxyRes.headers['location']) {
        proxyRes.headers['location'] = proxyRes.headers['location']
          .replace(/^https?:\/\/localhost:8000\/api/, '/api')
          .replace(/^https?:\/\/localhost:8000/, '');
      }
    },
  },
}));

// Serve static files
app.use(express.static(path.join(__dirname, 'dist')));

// Handle SPA routing
app.use((req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`API proxy: http://localhost:${PORT}/api/* → http://localhost:8000/api/*`);
});
