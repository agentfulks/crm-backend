const { spawn } = require('child_process');
const http = require('http');

console.log('🚀 MASTER SUPERVISOR STARTING (PID 1)...');

// 1. Start the actual background bootstrapper
const boot = spawn('bash', ['/data/workspace/start-railway.sh'], {
    detached: true,
    stdio: 'inherit'
});
boot.unref();

// 2. Start the OpenClaw Gateway
const gateway = spawn('node', ['/usr/local/lib/node_modules/openclaw/dist/entry.js', 'gateway', 'run', '--bind', 'loopback', '--port', '18789', '--auth', 'none'], {
    stdio: 'inherit'
});

// 3. Keep Port 8080 ALIVE for Railway Health Checks
const server = http.createServer((req, res) => {
    res.writeHead(200);
    res.end('VANTAGE_STABLE_HEARTBEAT');
});

server.listen(8080, '0.0.0.0', () => {
    console.log('✅ Port 8080 Health Responder Active');
});

console.log('✨ All systems integrated into PID 1.');
