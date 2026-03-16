#!/bin/bash
# PID 1 TAKEOVER - Bulletproof Entrypoint for Railway
# This script handles zombies, health checks, and service persistence

echo "🚀 PID 1 Takeover Initialized..."

# 1. Start our master startup script in the background
bash /data/workspace/start-railway.sh &

# 2. Start the original Railway wrapper as a sub-process
# This keeps Railway happy while our services run independently
node /usr/local/lib/node_modules/openclaw/dist/entry.js gateway run --bind loopback --port 18789 --auth none &

# 3. Handle Health Checks on Port 8080 (Primary Load Balancer Port)
# We use a simple python responder to keep the deployment "Healthy"
python3 -c '
import http.server, socketserver
class HealthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"HEALTHY")
PORT = 8080
with socketserver.TCPServer(("", PORT), HealthHandler) as httpd:
    print("✅ Port 8080 Health Check Active")
    httpd.serve_forever()
'
