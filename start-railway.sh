#!/bin/bash
# Railway Startup Script
# Installs and starts ClawMetry and Rustunnel on every deploy
# This ensures monitoring is always available

set -e

echo "🚀 Starting Railway services..."

# ============================================================================
# Grant openclaw user passwordless sudo on every boot
# Runs as root (Railway wrapper starts us as root in some configs) or is
# skipped silently if we lack privileges — SSH sessions as root will always
# have this set regardless.
# ============================================================================
if command -v apt-get &>/dev/null && ! dpkg -s sudo &>/dev/null 2>&1; then
    apt-get install -y sudo -qq 2>/dev/null || true
fi
mkdir -p /etc/sudoers.d 2>/dev/null || true
echo "openclaw ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/openclaw 2>/dev/null && \
    chmod 440 /etc/sudoers.d/openclaw 2>/dev/null && \
    echo "✅ openclaw granted passwordless sudo" || \
    echo "ℹ️  Could not write sudoers (not running as root — skipping)"

# ============================================================================
# Apply openclaw config settings using the official CLI
# This is more reliable than raw JSON patching
# ============================================================================
_apply_openclaw_config() {
  echo "🔧 Applying openclaw config settings..."

  # Wait for openclaw gateway to be running (it manages the config)
  local TRIES=0
  until openclaw config get gateway.controlUi.allowedOrigins >/dev/null 2>&1; do
    TRIES=$((TRIES + 1))
    [ $TRIES -ge 30 ] && echo "⚠️  Gave up waiting for openclaw" && return 1
    sleep 2
  done

  # Set allowed origins (idempotent — safe to run every boot)
  openclaw config set gateway.controlUi.allowedOrigins \
    '["https://marvy.up.railway.app","http://127.0.0.1:18789","http://localhost:18789"]' \
    2>&1 || echo "⚠️  Could not set allowedOrigins"

  # Fix model IDs if needed
  local CONFIG="/data/.openclaw/openclaw.json"
  if grep -qE 'moonshot-ai/kimi|gemini-2\.0-flash' "$CONFIG" 2>/dev/null; then
    echo "🔧 Fixing model IDs in config..."
    sed -i \
      -e 's|moonshot-ai/kimi-k2\.5|moonshotai/kimi-k2.5|g' \
      -e 's|moonshot-ai/kimi-lite|moonshotai/kimi-lite|g' \
      -e 's|google/gemini-2\.0-flash|google/gemini-3-flash-preview|g' \
      "$CONFIG" 2>/dev/null && echo "✅ Model IDs fixed" || echo "⚠️  sed failed"
  fi

  # Always fix ownership — openclaw config set / python writes may run as root
  # The gateway (UID 1001 / openclaw user) must be able to read the file
  chown 1001:1001 "$CONFIG" 2>/dev/null && echo "✅ Config ownership set to openclaw (1001)" || echo "⚠️  Could not chown config"

  # Restart the gateway so the new config takes effect
  echo "🔁 Restarting openclaw gateway to apply config..."
  # Find the openclaw-gateway process and send SIGTERM; the wrapper will restart it
  local GW_PID
  GW_PID=$(ps aux 2>/dev/null | awk '/openclaw-gateway/ && !/grep/{print $2}' | head -1)
  if [ -n "$GW_PID" ]; then
    kill -TERM "$GW_PID" 2>/dev/null && echo "✅ Gateway (PID $GW_PID) restarted" || echo "⚠️  Could not kill gateway"
  else
    echo "ℹ️  Gateway process not found, skipping restart"
  fi
}

# Run config fix in the background so it doesn't block service startup
# Runs once after gateway is up, then exits
( sleep 5 && _apply_openclaw_config && echo "✅ openclaw config applied" ) &

# ============================================================================
# Install ClawMetry (if not present)
# ============================================================================
export PATH="$HOME/.local/bin:$PATH"

if ! command -v clawmetry &> /dev/null; then
    echo "📦 Installing ClawMetry (Forced Venv mode)..."
    
    # 1. Create venv WITHOUT pip (avoids system package requirements)
    python3 -m venv /tmp/cenv --without-pip || true
    
    # 2. Manually inject pip into the venv
    curl -sS https://bootstrap.pypa.io/get-pip.py | /tmp/cenv/bin/python3 || true
    
    # 3. Install clawmetry using the newly injected pip
    /tmp/cenv/bin/pip install clawmetry || true
    
    # 4. Link binary to local bin
    mkdir -p "$HOME/.local/bin"
    ln -sf /tmp/cenv/bin/clawmetry "$HOME/.local/bin/clawmetry"
    
    echo "✅ ClawMetry installed"
fi

# Fallback: check if venv binary exists directly
if [ -f "/tmp/cenv/bin/clawmetry" ]; then
    CLAW_BIN="/tmp/cenv/bin/clawmetry"
else
    CLAW_BIN="clawmetry"
fi

# Ensure clawmetry is in PATH
if [ -f "$HOME/.local/bin/clawmetry" ]; then
    export PATH="$HOME/.local/bin:$PATH"
fi

# ============================================================================
# Install Rustunnel (if not present)
# ============================================================================
if ! command -v rustunnel &> /dev/null; then
    echo "📦 Installing Rustunnel..."
    
    # Download Rustunnel binary
    RUSTUNNEL_URL="https://github.com/joaoh82/rustunnel/releases/download/v0.2.3/rustunnel-v0.2.3-x86_64-unknown-linux-musl.tar.gz"
    curl -L -o /tmp/rustunnel.tar.gz "$RUSTUNNEL_URL"
    
    # Extract to local bin
    tar -xzf /tmp/rustunnel.tar.gz -C "$HOME/.local/bin/" 2>/dev/null || tar -xzf /tmp/rustunnel.tar.gz -C /tmp/
    
    # Make executable
    chmod +x "$HOME/.local/bin/rustunnel" 2>/dev/null || chmod +x /tmp/rustunnel
    
    # Add to PATH
    export PATH="$HOME/.local/bin:$PATH"
    export PATH="/tmp:$PATH"
    
    echo "✅ Rustunnel installed"
else
    echo "✅ Rustunnel already installed"
fi

# Ensure rustunnel is in PATH
export PATH="$HOME/.local/bin:$PATH"
export PATH="/tmp:$PATH"

# ============================================================================
# Verify installations
# ============================================================================
echo ""
echo "🔍 Verifying installations..."

if command -v clawmetry &> /dev/null; then
    echo "✅ ClawMetry: $(clawmetry --version 2>/dev/null || echo 'installed')"
else
    echo "❌ ClawMetry not found in PATH"
    echo "PATH: $PATH"
    ls -la "$HOME/.local/bin/" 2>/dev/null || echo "No .local/bin"
fi

if command -v rustunnel &> /dev/null; then
    echo "✅ Rustunnel: $(rustunnel --version 2>/dev/null || echo 'installed')"
else
    echo "❌ Rustunnel not found in PATH"
    # Try to use /tmp/rustunnel directly
    if [ -f "/tmp/rustunnel" ]; then
        echo "📍 Found at /tmp/rustunnel"
    fi
fi

# ============================================================================
# Start ClawMetry
# ============================================================================
echo ""
echo "🦞 Starting ClawMetry..."

export OPENCLAW_DIR="${OPENCLAW_DIR:-/home/openclaw/.openclaw}"
export OPENCLAW_GATEWAY_TOKEN="${OPENCLAW_GATEWAY_TOKEN:-h5couvehu4j0dtotctts24sypujtvkec}"
export OPENCLAW_WORKSPACE="${OPENCLAW_WORKSPACE:-/data/workspace}"

# Kill any existing clawmetry processes
pkill -f "clawmetry.*8900" 2>/dev/null || true

# Start ClawMetry in background
nohup "$CLAW_BIN" --port 8900 --workspace "$OPENCLAW_WORKSPACE" --sessions-dir "/data/.openclaw/agents/main/sessions" --name "VANTAGE" > /tmp/clawmetry.log 2>&1 &
echo "✅ ClawMetry started on port 8900"
echo "📊 Dashboard: http://localhost:8900 (will be tunneled)"

# Wait for ClawMetry to start
sleep 3

# ============================================================================
# Start Rustunnel
# Start CRM Tunnel (Port 4173)
nohup "$RUSTUNNEL_BIN" http 4173 --server edge.rustunnel.com:4040 --token "$TOKEN" > /tmp/rustunnel-crm.log 2>&1 &
# ============================================================================
echo ""
echo "🔒 Starting Rustunnel..."

# Kill any existing rustunnel processes
pkill -f "rustunnel.*8900" 2>/dev/null || true

RUSTUNNEL_BIN="$(command -v rustunnel 2>/dev/null || echo '/tmp/rustunnel')"
TOKEN="${RUSTUNNEL_TOKEN:-3f61720a-c691-4f22-81a9-889cd31e460c}"

if [ -f "$RUSTUNNEL_BIN" ]; then
    nohup "$RUSTUNNEL_BIN" http 8900 \
        --server edge.rustunnel.com:4040 \
        --token "$TOKEN" \
        > /tmp/rustunnel.log 2>&1 &
    
    echo "✅ Rustunnel started"
    echo "🌐 Tunnel will be available shortly..."
    
    # Wait for tunnel to establish
    sleep 5
    
    # Show tunnel URL from log
    if [ -f /tmp/rustunnel.log ]; then
        TUNNEL_URL=$(grep -o 'http://[a-z0-9]*\.edge\.rustunnel\.com' /tmp/rustunnel.log | head -1)
        if [ -n "$TUNNEL_URL" ]; then
            echo "🔗 Tunnel URL: $TUNNEL_URL"
        fi
    fi
else
    echo "⚠️ Rustunnel not available, skipping..."
fi

# ============================================================================
# Start Python Backend (Port 8000)
# ============================================================================
echo ""
echo "🐍 Starting Python Backend..."

if [ -d "/data/workspace/backend" ]; then
    # Ensure dependencies are available in the venv
    if [ -f "/tmp/cenv/bin/pip" ]; then
        echo "📦 Installing backend dependencies..."
        /tmp/cenv/bin/pip install uvicorn fastapi httpx pydantic sqlalchemy python-dotenv fastapi-pagination python-multipart passlib python-jose[cryptography] pydantic-settings psycopg[binary] || true
    fi

    # Start using venv python
    nohup /tmp/cenv/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir /data/workspace/backend > /tmp/py-backend.log 2>&1 &
    echo "✅ Python backend started on port 8000"
else
    echo "⚠️  Backend directory not found, skipping..."
fi

# ============================================================================
# Start other services (if needed)
# ============================================================================
echo ""
echo "🔧 Checking other services..."

# Check if proxy server should run
if [ -f "/data/workspace/frontend/proxy-server.cjs" ]; then
    if ! pgrep -f "proxy-server.cjs" > /dev/null; then
        echo "🌐 Starting proxy server..."
        cd /data/workspace/frontend
        nohup node proxy-server.cjs > /tmp/proxy.log 2>&1 &
        echo "✅ Proxy server started on port 4173"
    else
        echo "✅ Proxy server already running"
    fi
fi

# ============================================================================
# Keep script running
# ============================================================================
echo ""
echo "✨ All services started!"
echo ""
echo "📋 Status:"
echo "  - ClawMetry: http://localhost:8900"
echo "  - Rustunnel: Check /tmp/rustunnel.log for URL"
echo "  - Proxy: http://localhost:4173 (if enabled)"
echo ""
echo "📝 Logs:"
echo "  - ClawMetry: /tmp/clawmetry.log"
echo "  - Rustunnel: /tmp/rustunnel.log"
echo "  - Proxy: /tmp/proxy.log"
echo ""
echo "⏳ Keeping script alive..."

# Keep the script running to satisfy Railway's requirement for a foreground process
tail -f /tmp/clawmetry.log /tmp/rustunnel.log 2>/dev/null || sleep infinity