#!/usr/bin/env python3
"""
OpenClaw + VC Outreach Dashboard Proxy

This server runs on port 8080 and serves:
- /dashboard/* -> VC Outreach Frontend (static files from /data/workspace/frontend/dist)
- /* -> OpenClaw Control UI (proxied to localhost:8081)

Rollback: Run ./rollback-openclaw.sh from SSH
"""

import http.server
import socketserver
import urllib.request
import urllib.error
import os
import sys

PORT = 8080
OPENCLAW_PORT = 8081  # OpenClaw runs here internally
FRONTEND_DIR = '/data/workspace/frontend/dist'

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)
    
    def do_GET(self):
        # Serve dashboard files
        if self.path.startswith('/dashboard/'):
            # Strip /dashboard prefix and serve from frontend
            original_path = self.path
            self.path = self.path[10:]  # Remove '/dashboard'
            if self.path == '' or self.path == '/':
                self.path = '/index.html'
            try:
                return super().do_GET()
            except Exception as e:
                self.send_error(500, f"Error serving dashboard: {e}")
            finally:
                self.path = original_path
            return
        
        # Redirect /dashboard to /dashboard/
        if self.path == '/dashboard':
            self.send_response(302)
            self.send_header('Location', '/dashboard/')
            self.end_headers()
            return
        
        # Health check
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            health = {
                "status": "ok",
                "services": {
                    "proxy": "running",
                    "openclaw": f"http://localhost:{OPENCLAW_PORT}",
                    "dashboard": "/dashboard/"
                }
            }
            import json
            self.wfile.write(json.dumps(health).encode())
            return
        
        # Proxy everything else to OpenClaw
        try:
            target_url = f"http://localhost:{OPENCLAW_PORT}{self.path}"
            
            req = urllib.request.Request(
                target_url,
                headers=self.headers.items()
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                self.send_response(response.status)
                
                # Copy headers
                for header, value in response.headers.items():
                    if header.lower() not in ('transfer-encoding', 'content-length'):
                        self.send_header(header, value)
                
                self.send_header('Content-Length', len(response.read()))
                self.end_headers()
                
                # Copy body
                self.wfile.write(response.read())
                
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_error(502, f"Bad Gateway: {e}")
    
    def log_message(self, format, *args):
        # Custom logging
        print(f"[{self.log_date_time_string()}] {args[0]}")

if __name__ == "__main__":
    print(f"""
╔════════════════════════════════════════════════════════════╗
║  OpenClaw + VC Outreach Proxy Running                      ║
╠════════════════════════════════════════════════════════════╣
║  Port:        {PORT}                                         ║
║  OpenClaw:    http://localhost:{OPENCLAW_PORT} (internal)    ║
║  Dashboard:   http://localhost:{PORT}/dashboard/            ║
╠════════════════════════════════════════════════════════════╣
║  URLs:                                                     ║
║    • http://marvy.up.railway.app/          → OpenClaw     ║
║    • http://marvy.up.railway.app/dashboard → VC Outreach  ║
╠════════════════════════════════════════════════════════════╣
║  ROLLBACK (if needed):                                     ║
║    ./rollback-openclaw.sh                                  ║
╚════════════════════════════════════════════════════════════╝
""")
    
    # Check if OpenClaw is running on 8081
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', OPENCLAW_PORT))
    sock.close()
    
    if result != 0:
        print(f"⚠️  WARNING: OpenClaw not detected on port {OPENCLAW_PORT}")
        print("     Make sure OpenClaw is running on port 8081 first!")
        print("")
    
    with socketserver.TCPServer(("0.0.0.0", PORT), ProxyHandler) as httpd:
        print(f"🚀 Server running on port {PORT}")
        print("Press Ctrl+C to stop\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")
            sys.exit(0)
