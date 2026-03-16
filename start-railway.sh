#!/bin/bash
# ============================================================================
# BULLETPROOF RAILWAY DEPLOYMENT SCRIPT
# Fixes: Port drift, zombie processes, missing dependencies, variable ordering
# Version: 2.0 - Production Ready
# ============================================================================

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# ============================================================================
# CONFIGURATION
# ============================================================================
export OPENCLAW_DIR="${OPENCLAW_DIR:-/home/openclaw/.openclaw}"
export OPENCLAW_WORKSPACE="${OPENCLAW_WORKSPACE:-/data/workspace}"
export OPENCLAW_GATEWAY_TOKEN="${OPENCLAW_GATEWAY_TOKEN:-h5couvehu4j0dtotctts24sypujtvkec}"
export RUSTUNNEL_TOKEN="${RUSTUNNEL_TOKEN:-3f61720a-c691-4f22-81a9-889cd31e460c}"

# Railway requires this specific port for health checks
export PORT="${PORT:-8080}"

# Service ports (internal)
CLAWMETRY_PORT=8900
BACKEND_PORT=8000
GATEWAY_PORT=18789

# Logging
exec > >(tee -a /tmp/railway-startup.log) 2>&1

echo "═══════════════════════════════════════════════════════════════"
echo "  RAILWAY DEPLOYMENT - $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "═══════════════════════════════════════════════════════════════"
echo "Environment:"
echo "  PORT (Railway): $PORT"
echo "  WORKSPACE: $OPENCLAW_WORKSPACE"
echo "  OPENCLAW_DIR: $OPENCLAW_DIR"
echo ""

# ============================================================================
# PHASE 1: CLEANUP (Kill zombies, clear old state)
# ============================================================================
echo "🔍 PHASE 1: Environment Cleanup"

# Function to safely kill processes
safe_kill() {
    local pattern="$1"
    pkill -f "$pattern" 2>/dev/null || true
    sleep 1
    pkill -9 -f "$pattern" 2>/dev/null || true
}

# Kill any existing services
safe_kill "clawmetry"
safe_kill "rustunnel"
safe_kill "uvicorn"
safe_kill "python3 -m uvicorn"

# Clear old logs (keep last startup)
mkdir -p /tmp/logs
mv /tmp/*.log /tmp/logs/ 2>/dev/null || true
rm -f /tmp/clawmetry.log /tmp/rustunnel.log /tmp/py-backend.log /tmp/gateway.log

echo "✅ Cleanup complete"

# ============================================================================
# PHASE 2: DEPENDENCY INSTALLATION
# ============================================================================
echo ""
echo "📦 PHASE 2: Dependency Installation"

export PATH="$HOME/.local/bin:/tmp:$PATH"
mkdir -p "$HOME/.local/bin"

# --- Python Virtual Environment ---
VENV_PATH="/tmp/cenv"
if [[ ! -f "$VENV_PATH/bin/python3" ]]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$VENV_PATH" --without-pip
    curl -sS https://bootstrap.pypa.io/get-pip.py | "$VENV_PATH/bin/python3"
fi

# --- Install ClawMetry ---
if ! "$VENV_PATH/bin/pip" show clawmetry >/dev/null 2>&1; then
    echo "Installing ClawMetry..."
    "$VENV_PATH/bin/pip" install --quiet clawmetry
fi

# --- Install Backend Dependencies (CRITICAL FIX) ---
echo "Installing backend dependencies..."
"$VENV_PATH/bin/pip" install --quiet \
    uvicorn fastapi httpx pydantic sqlalchemy python-dotenv \
    fastapi-pagination python-multipart passlib \
    "python-jose[cryptography]" pydantic-settings "psycopg[binary]" 2>/dev/null || true

# --- Install Rustunnel ---
RUSTUNNEL_BIN="$HOME/.local/bin/rustunnel"
if [[ ! -f "$RUSTUNNEL_BIN" ]]; then
    echo "Installing Rustunnel..."
    curl -sL -o /tmp/rustunnel.tar.gz \
        "https://github.com/joaoh82/rustunnel/releases/download/v0.2.3/rustunnel-v0.2.3-x86_64-unknown-linux-musl.tar.gz"
    tar -xzf /tmp/rustunnel.tar.gz -C "$HOME/.local/bin/" 2>/dev/null || \
        tar -xzf /tmp/rustunnel.tar.gz -C /tmp/
    chmod +x "$RUSTUNNEL_BIN" 2>/dev/null || chmod +x /tmp/rustunnel
fi

# Verify binaries
echo ""
echo "🔍 Verifying installations:"
echo "  ClawMetry: $($VENV_PATH/bin/clawmetry --version 2>/dev/null || echo '✗')"
echo "  Rustunnel: $($RUSTUNNEL_BIN --version 2>/dev/null || /tmp/rustunnel --version 2>/dev/null || echo '✗')"
echo "  Uvicorn: $($VENV_PATH/bin/python3 -m uvicorn --version 2>/dev/null || echo '✗')"

# ============================================================================
# PHASE 3: CONFIGURATION SETUP
# ============================================================================
echo ""
echo "⚙️  PHASE 3: Configuration Setup"

# Ensure openclaw config directory exists
mkdir -p "$OPENCLAW_DIR"

# Apply openclaw config (background - non-blocking)
(
    sleep 3
    # Wait for gateway to be ready
    for i in {1..30}; do
        if openclaw config get gateway.controlUi.allowedOrigins >/dev/null 2>&1; then
            break
        fi
        sleep 2
    done
    
    # Set allowed origins
    openclaw config set gateway.controlUi.allowedOrigins \
        '["https://marvy.up.railway.app","http://127.0.0.1:18789","http://localhost:18789"]' 2>/dev/null || true
    
    # Fix config ownership
    chown 1001:1001 "$OPENCLAW_DIR/openclaw.json" 2>/dev/null || true
    
    echo "✅ OpenClaw config applied"
) &

# ============================================================================
# PHASE 4: SERVICE STARTUP (Using Supervisor Pattern)
# ============================================================================
echo ""
echo "🚀 PHASE 4: Starting Services"

# Function to wait for port
wait_for_port() {
    local port=$1
    local name=$2
    local max_attempts=${3:-30}
    
    for ((i=1; i<=max_attempts; i++)); do
        if timeout 2 bash -c "</dev/tcp/127.0.0.1/$port" 2>/dev/null; then
            echo "✅ $name ready on port $port"
            return 0
        fi
        sleep 1
    done
    echo "❌ $name failed to start on port $port"
    return 1
}

# --- Start 1: ClawMetry Dashboard ---
echo ""
echo "🦞 Starting ClawMetry (port $CLAWMETRY_PORT)..."

# CRITICAL FIX: Removed --no-reload (not supported in v0.12.47)
nohup "$VENV_PATH/bin/clawmetry" \
    --port "$CLAWMETRY_PORT" \
    --host 0.0.0.0 \
    --workspace "$OPENCLAW_WORKSPACE" \
    --sessions-dir "$OPENCLAW_DIR/agents" \
    --name "VANTAGE (ALL)" \
    --no-debug \
    > /tmp/clawmetry.log 2>&1 &

CLAWMETRY_PID=$!
echo "  PID: $CLAWMETRY_PID"

# Wait for ClawMetry
if ! wait_for_port "$CLAWMETRY_PORT" "ClawMetry" 30; then
    echo "⚠️  ClawMetry failed to start, checking logs:"
    tail -20 /tmp/clawmetry.log
fi

# --- Start 2: Rustunnel (tunnels port 8900) ---
echo ""
echo "🔒 Starting Rustunnel..."

RUSTUNNEL_CMD="$RUSTUNNEL_BIN"
[[ -f "$RUSTUNNEL_CMD" ]] || RUSTUNNEL_CMD="/tmp/rustunnel"

nohup "$RUSTUNNEL_CMD" http "$CLAWMETRY_PORT" \
    --server edge.rustunnel.com:4040 \
    --token "$RUSTUNNEL_TOKEN" \
    > /tmp/rustunnel.log 2>&1 &

RUSTUNNEL_PID=$!
echo "  PID: $RUSTUNNEL_PID"
sleep 5

# Capture tunnel URL
if [[ -f /tmp/rustunnel.log ]]; then
    TUNNEL_URL=$(grep -oP 'http://[a-z0-9]+\.edge\.rustunnel\.com' /tmp/rustunnel.log | head -1)
    if [[ -n "$TUNNEL_URL" ]]; then
        echo "  🌐 Tunnel URL: $TUNNEL_URL"
    fi
fi

# --- Start 3: Python Backend (if exists) ---
if [[ -d "$OPENCLAW_WORKSPACE/backend" ]]; then
    echo ""
    echo "🐍 Starting Python Backend (port $BACKEND_PORT)..."
    
    cd "$OPENCLAW_WORKSPACE/backend"
    nohup "$VENV_PATH/bin/python3" -m uvicorn \
        app.main:app \
        --host 0.0.0.0 \
        --port "$BACKEND_PORT" \
        > /tmp/py-backend.log 2>&1 &
    
    BACKEND_PID=$!
    echo "  PID: $BACKEND_PID"
    
    wait_for_port "$BACKEND_PORT" "Backend" 20 || true
else
    echo "  ℹ️  Backend directory not found, skipping"
fi

# --- Start 4: OpenClaw Gateway ---
echo ""
echo "🦞 Starting OpenClaw Gateway (port $GATEWAY_PORT)..."

# Kill any existing gateway
pkill -f "dist/entry.js gateway run" 2>/dev/null || true
sleep 2

nohup node /usr/local/lib/node_modules/openclaw/dist/entry.js \
    gateway run \
    --port "$GATEWAY_PORT" \
    --bind loopback \
    > /tmp/gateway.log 2>&1 &

GATEWAY_PID=$!
echo "  PID: $GATEWAY_PID"

wait_for_port "$GATEWAY_PORT" "Gateway" 20 || true

# Trust local connections
node /usr/local/lib/node_modules/openclaw/dist/entry.js \
    gateway trust-local --all --force 2>/dev/null || true

# ============================================================================
# PHASE 5: RAILWAY HEALTH ENDPOINT (CRITICAL FIX)
# ============================================================================
echo ""
echo "🌐 PHASE 5: Starting Railway Health Endpoint (port $PORT)"

# Create a simple Python health server on Railway's expected PORT
cat > /tmp/health-server.py << 'HEALTH_EOF'
import http.server
import socketserver
import json
import os

PORT = int(os.environ.get('PORT', '8080'))

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            # Check all services
            import socket
            checks = {
                'clawmetry': self._check_port(8900),
                'backend': self._check_port(8000),
                'gateway': self._check_port(18789)
            }
            healthy = all(checks.values())
            
            self.send_response(200 if healthy else 503)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'healthy' if healthy else 'degraded',
                'services': checks,
                'timestamp': str(__import__('datetime').datetime.utcnow())
            }).encode())
        else:
            # Proxy to ClawMetry
            self.send_response(302)
            self.send_header('Location', 'http://127.0.0.1:8900')
            self.end_headers()
    
    def _check_port(self, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            return result == 0
        except:
            return False
    
    def log_message(self, format, *args):
        pass  # Suppress logs

with socketserver.TCPServer(('0.0.0.0', PORT), Handler) as httpd:
    httpd.serve_forever()
HEALTH_EOF

nohup "$VENV_PATH/bin/python3" /tmp/health-server.py > /tmp/health-server.log 2>&1 &
HEALTH_PID=$!
echo "  PID: $HEALTH_PID"
sleep 2

# Verify health endpoint
if timeout 2 bash -c "</dev/tcp/127.0.0.1/$PORT" 2>/dev/null; then
    echo "✅ Health endpoint active on port $PORT"
else
    echo "⚠️  Health endpoint not responding"
fi

# ============================================================================
# PHASE 6: KEEP ALIVE WITH WATCHDOG
# ============================================================================
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  DEPLOYMENT COMPLETE - Entering Watchdog Mode"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Service Status:"
echo "  ClawMetry:   http://127.0.0.1:$CLAWMETRY_PORT"
echo "  Backend:     http://127.0.0.1:$BACKEND_PORT"
echo "  Gateway:     http://127.0.0.1:$GATEWAY_PORT"
echo "  Health:      http://0.0.0.0:$PORT/health"
echo ""
echo "Logs:"
echo "  /tmp/clawmetry.log"
echo "  /tmp/rustunnel.log"
echo "  /tmp/py-backend.log"
echo "  /tmp/gateway.log"
echo ""

# Simple watchdog loop - restart failed services
while true; do
    sleep 30
    
    # Check ClawMetry
    if ! timeout 2 bash -c "</dev/tcp/127.0.0.1/$CLAWMETRY_PORT" 2>/dev/null; then
        echo "⚠️  $(date): ClawMetry down, restarting..."
        pkill -f "clawmetry.*$CLAWMETRY_PORT" 2>/dev/null || true
        sleep 2
        nohup "$VENV_PATH/bin/clawmetry" \
            --port "$CLAWMETRY_PORT" \
            --host 0.0.0.0 \
            --workspace "$OPENCLAW_WORKSPACE" \
            --sessions-dir "$OPENCLAW_DIR/agents" \
            --name "VANTAGE (ALL)" \
            --no-debug \
            > /tmp/clawmetry.log 2>&1 &
        sleep 5
    fi
    
    # Check Rustunnel
    if ! pgrep -f "rustunnel.*$CLAWMETRY_PORT" > /dev/null; then
        echo "⚠️  $(date): Rustunnel down, restarting..."
        nohup "$RUSTUNNEL_CMD" http "$CLAWMETRY_PORT" \
            --server edge.rustunnel.com:4040 \
            --token "$RUSTUNNEL_TOKEN" \
            > /tmp/rustunnel.log 2>&1 &
    fi
    
    # Log status
    echo "$(date -u +%H:%M:%SZ) Watchdog check complete"
done
