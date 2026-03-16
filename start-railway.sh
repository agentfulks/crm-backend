#!/bin/bash
# ============================================================================
# RAILWAY STARTUP SCRIPT
# Runs alongside /app/entrypoint.sh via:
#   bash /data/workspace/start-railway.sh & exec /app/entrypoint.sh
#
# The entrypoint takes ~5s before starting the gateway (runs doctor --fix first).
# Phase 0 exploits this window to patch the config before the gateway reads it.
# ============================================================================

# NOTE: No set -euo pipefail here — we want failures to be non-fatal

# ============================================================================
# PHASE 0: CONFIG PATCH (synchronous — must finish before gateway starts)
# The OpenClaw wrapper runs `openclaw doctor --fix` before starting the gateway,
# giving us ~5 seconds to patch the config file on disk.
# ============================================================================
CONFIG="/data/.openclaw/openclaw.json"

echo "[Phase 0] Patching OpenClaw config..."

if [[ -f "$CONFIG" ]]; then
    python3 - <<'PYEOF'
import json, sys

CONFIG = "/data/.openclaw/openclaw.json"

try:
    with open(CONFIG, "r") as f:
        cfg = json.load(f)
except Exception as e:
    print(f"[Phase 0] ERROR reading config: {e}", file=sys.stderr)
    sys.exit(1)

# Ensure nested structure exists
cfg.setdefault("gateway", {}).setdefault("controlUi", {})

# Set allowed origins (all three variants needed)
cfg["gateway"]["controlUi"]["allowedOrigins"] = [
    "https://marvy.up.railway.app",
    "http://127.0.0.1:18789",
    "http://localhost:18789"
]

# Keep insecure auth enabled (required for tunnel access)
cfg["gateway"]["controlUi"]["allowInsecureAuth"] = True

try:
    with open(CONFIG, "w") as f:
        json.dump(cfg, f, indent=2)
    print("[Phase 0] Config patched successfully")
    print(f"[Phase 0] allowedOrigins = {cfg['gateway']['controlUi']['allowedOrigins']}")
except Exception as e:
    print(f"[Phase 0] ERROR writing config: {e}", file=sys.stderr)
    sys.exit(1)
PYEOF

    # Fix ownership immediately — gateway runs as UID 1001 and can't read root-owned files
    chown 1001:1001 "$CONFIG" 2>/dev/null && echo "[Phase 0] chown 1001:1001 applied" || echo "[Phase 0] chown failed (non-fatal)"
else
    echo "[Phase 0] Config file not found at $CONFIG — will apply via openclaw config set after gateway starts"
fi

# ============================================================================
# CONFIGURATION
# ============================================================================
export OPENCLAW_DIR="${OPENCLAW_DIR:-/data/.openclaw}"
export OPENCLAW_WORKSPACE="${OPENCLAW_WORKSPACE:-/data/workspace}"
export OPENCLAW_GATEWAY_TOKEN="${OPENCLAW_GATEWAY_TOKEN:-h5couvehu4j0dtotctts24sypujtvkec}"
export RUSTUNNEL_TOKEN="${RUSTUNNEL_TOKEN:-3f61720a-c691-4f22-81a9-889cd31e460c}"

CLAWMETRY_PORT=8900
BACKEND_PORT=8000
GATEWAY_PORT=18789

exec > >(tee -a /tmp/railway-startup.log) 2>&1

echo "═══════════════════════════════════════════════════════════════"
echo "  RAILWAY STARTUP SCRIPT - $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "═══════════════════════════════════════════════════════════════"

# ============================================================================
# PHASE 1: CLEANUP
# ============================================================================
echo ""
echo "🔍 PHASE 1: Cleanup"

pkill -f "clawmetry" 2>/dev/null || true
pkill -f "rustunnel" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
sleep 1

mkdir -p /tmp/logs
mv /tmp/*.log /tmp/logs/ 2>/dev/null || true

echo "✅ Cleanup complete"

# ============================================================================
# PHASE 2: DEPENDENCY INSTALLATION
# ============================================================================
echo ""
echo "📦 PHASE 2: Dependencies"

export PATH="$HOME/.local/bin:/tmp:$PATH"
mkdir -p "$HOME/.local/bin"

VENV_PATH="/tmp/cenv"
if [[ ! -f "$VENV_PATH/bin/python3" ]]; then
    echo "Creating Python venv..."
    python3 -m venv "$VENV_PATH" --without-pip
    curl -sS https://bootstrap.pypa.io/get-pip.py | "$VENV_PATH/bin/python3"
fi

if ! "$VENV_PATH/bin/pip" show clawmetry >/dev/null 2>&1; then
    echo "Installing ClawMetry..."
    "$VENV_PATH/bin/pip" install --quiet clawmetry
fi

echo "Installing backend dependencies..."
"$VENV_PATH/bin/pip" install --quiet \
    uvicorn fastapi httpx pydantic sqlalchemy python-dotenv \
    fastapi-pagination python-multipart passlib \
    "python-jose[cryptography]" pydantic-settings "psycopg[binary]" 2>/dev/null || true

RUSTUNNEL_BIN="$HOME/.local/bin/rustunnel"
if [[ ! -f "$RUSTUNNEL_BIN" ]]; then
    echo "Installing Rustunnel..."
    curl -sL -o /tmp/rustunnel.tar.gz \
        "https://github.com/joaoh82/rustunnel/releases/download/v0.2.3/rustunnel-v0.2.3-x86_64-unknown-linux-musl.tar.gz"
    tar -xzf /tmp/rustunnel.tar.gz -C "$HOME/.local/bin/" 2>/dev/null || \
        tar -xzf /tmp/rustunnel.tar.gz -C /tmp/
    chmod +x "$RUSTUNNEL_BIN" 2>/dev/null || chmod +x /tmp/rustunnel 2>/dev/null || true
fi

echo "✅ Dependencies ready"

# ============================================================================
# PHASE 3: POST-GATEWAY CONFIG (fallback for first-boot when config didn't exist)
# ============================================================================
(
    sleep 8  # Wait for gateway to fully start
    
    # Only needed if Phase 0 skipped (config didn't exist at startup)
    if [[ ! -f "$CONFIG" ]]; then
        echo "[Phase 3] Applying config via openclaw config set (first-boot fallback)..."
        openclaw config set gateway.controlUi.allowedOrigins \
            '["https://marvy.up.railway.app","http://127.0.0.1:18789","http://localhost:18789"]' 2>/dev/null || true
        chown 1001:1001 "$CONFIG" 2>/dev/null || true
        
        # Restart gateway so it picks up the new config
        echo "[Phase 3] Killing gateway to force config reload..."
        pkill -f "dist/entry.js gateway run" 2>/dev/null || true
        echo "[Phase 3] Gateway will be restarted by the OpenClaw wrapper"
    fi
) &

# ============================================================================
# PHASE 4: START BACKGROUND SERVICES
# ============================================================================
echo ""
echo "🚀 PHASE 4: Starting background services"

wait_for_port() {
    local port=$1 name=$2 max=${3:-30}
    for ((i=1; i<=max; i++)); do
        if timeout 2 bash -c "</dev/tcp/127.0.0.1/$port" 2>/dev/null; then
            echo "✅ $name ready on :$port"
            return 0
        fi
        sleep 1
    done
    echo "❌ $name failed to start on :$port"
    return 1
}

# --- ClawMetry ---
echo ""
echo "🦞 Starting ClawMetry (port $CLAWMETRY_PORT)..."
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
wait_for_port "$CLAWMETRY_PORT" "ClawMetry" 30 || tail -20 /tmp/clawmetry.log

# --- Rustunnel ---
RUSTUNNEL_CMD="$RUSTUNNEL_BIN"
[[ -f "$RUSTUNNEL_CMD" ]] || RUSTUNNEL_CMD="/tmp/rustunnel"

if [[ -f "$RUSTUNNEL_CMD" ]]; then
    echo ""
    echo "🔒 Starting Rustunnel..."
    nohup "$RUSTUNNEL_CMD" http "$CLAWMETRY_PORT" \
        --server edge.rustunnel.com:4040 \
        --token "$RUSTUNNEL_TOKEN" \
        > /tmp/rustunnel.log 2>&1 &
    echo "  PID: $!"
    sleep 5
    TUNNEL_URL=$(grep -oP 'http://[a-z0-9]+\.edge\.rustunnel\.com' /tmp/rustunnel.log | head -1)
    [[ -n "$TUNNEL_URL" ]] && echo "  🌐 Tunnel: $TUNNEL_URL"
fi

# --- Python Backend (if present) ---
if [[ -d "$OPENCLAW_WORKSPACE/backend" ]]; then
    echo ""
    echo "🐍 Starting Python Backend (port $BACKEND_PORT)..."
    cd "$OPENCLAW_WORKSPACE/backend"
    nohup "$VENV_PATH/bin/python3" -m uvicorn \
        app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" \
        > /tmp/py-backend.log 2>&1 &
    echo "  PID: $!"
    wait_for_port "$BACKEND_PORT" "Backend" 20 || true
fi

# ============================================================================
# PHASE 5: WATCHDOG (keep background services alive)
# NOTE: The OpenClaw gateway is managed by /app/entrypoint.sh — don't touch it.
# ============================================================================
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  STARTUP COMPLETE - Watchdog active"
echo "  ClawMetry: http://127.0.0.1:$CLAWMETRY_PORT"
echo "  Tunnel:    $TUNNEL_URL"
echo "═══════════════════════════════════════════════════════════════"

while true; do
    sleep 30

    # Restart ClawMetry if down
    if ! timeout 2 bash -c "</dev/tcp/127.0.0.1/$CLAWMETRY_PORT" 2>/dev/null; then
        echo "⚠️  $(date -u +%H:%M:%SZ): ClawMetry down, restarting..."
        pkill -f "clawmetry" 2>/dev/null || true
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

    # Restart Rustunnel if down
    if [[ -f "$RUSTUNNEL_CMD" ]] && ! pgrep -f "rustunnel" > /dev/null; then
        echo "⚠️  $(date -u +%H:%M:%SZ): Rustunnel down, restarting..."
        nohup "$RUSTUNNEL_CMD" http "$CLAWMETRY_PORT" \
            --server edge.rustunnel.com:4040 \
            --token "$RUSTUNNEL_TOKEN" \
            > /tmp/rustunnel.log 2>&1 &
    fi
done
