#!/bin/bash
# Railway Startup Script
# Installs and starts ClawMetry and Rustunnel on every deploy
# This ensures monitoring is always available

set -e

echo "🚀 Starting Railway services..."

# ============================================================================
# Patch openclaw config on every boot (runs in background, waits for openclaw
# to create its config file, then fixes model IDs and allowedOrigins)
# ============================================================================
(
  CONFIG="/home/openclaw/.openclaw/openclaw.json"
  echo "⏳ Waiting for openclaw config to be ready..."
  for i in $(seq 1 90); do
    if [ -f "$CONFIG" ]; then
      echo "🔧 Patching openclaw config..."
      python3 - "$CONFIG" <<'PYEOF'
import json, sys

path = sys.argv[1]
with open(path, 'r') as f:
    config = json.load(f)

# Fix model IDs (moonshot-ai -> moonshotai)
config_str = json.dumps(config)
config_str = config_str.replace('moonshot-ai/kimi-k2.5', 'moonshotai/kimi-k2.5')
config_str = config_str.replace('moonshot-ai/kimi-lite', 'moonshotai/kimi-lite')
config = json.loads(config_str)

# Ensure Railway domain is in allowedOrigins
origins = config.setdefault('gateway', {}).setdefault('controlUi', {}).setdefault('allowedOrigins', [])
railway_domain = 'https://marvy.up.railway.app'
if railway_domain not in origins:
    origins.append(railway_domain)

with open(path, 'w') as f:
    json.dump(config, f, indent=2)

print('✅ openclaw config patched successfully!')
PYEOF
      # Restart gateway so it picks up the new config
      sleep 2
      pkill -f openclaw-gateway 2>/dev/null || true
      echo "✅ openclaw-gateway restarted with patched config"
      break
    fi
    sleep 2
  done
  if [ ! -f "$CONFIG" ]; then
    echo "⚠️ openclaw config never appeared — skipping patch"
  fi
) &

# ============================================================================
# Install ClawMetry (if not present)
# ============================================================================
if ! command -v clawmetry &> /dev/null; then
    echo "📦 Installing ClawMetry..."
    curl -fsSL https://clawmetry.com/install.sh | bash
    
    # Add to PATH if installed to local bin
    if [ -f "$HOME/.local/bin/clawmetry" ]; then
        export PATH="$HOME/.local/bin:$PATH"
    fi
    
    echo "✅ ClawMetry installed"
else
    echo "✅ ClawMetry already installed"
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
if command -v clawmetry &> /dev/null; then
    nohup clawmetry --port 8900 --workspace "$OPENCLAW_WORKSPACE" --name "VANTAGE" > /tmp/clawmetry.log 2>&1 &
    echo "✅ ClawMetry started on port 8900"
    echo "📊 Dashboard: http://localhost:8900 (will be tunneled)"
else
    echo "⚠️ ClawMetry not available, skipping..."
fi

# Wait for ClawMetry to start
sleep 3

# ============================================================================
# Start Rustunnel
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