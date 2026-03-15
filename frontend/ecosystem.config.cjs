module.exports = {
  apps: [{
    name: 'dashboard-proxy',
    script: './proxy-server.cjs',
    cwd: '/data/workspace/frontend',
    
    // Auto-restart configuration
    autorestart: true,
    max_restarts: 10,
    min_uptime: '10s',
    restart_delay: 3000,
    
    // Memory limits
    max_memory_restart: '500M',
    
    // Logging
    log_file: '/home/openclaw/.pm2/logs/dashboard-proxy-combined.log',
    out_file: '/home/openclaw/.pm2/logs/dashboard-proxy-out.log',
    error_file: '/home/openclaw/.pm2/logs/dashboard-proxy-error.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    
    // Environment
    env: {
      NODE_ENV: 'production'
    },
    
    // Process management
    kill_timeout: 5000,
    listen_timeout: 10000,
    
    // Don't restart if crashing too fast
    exp_backoff_restart_delay: 100
  }]
};
