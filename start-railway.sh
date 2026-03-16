#!/bin/bash
# ============================================================================
# RAILWAY STARTUP SCRIPT
# Runs alongside /app/entrypoint.sh via Railway start command:
#   bash /data/workspace/start-railway.sh & exec /app/entrypoint.sh
# ============================================================================

CONFIG="/data/.openclaw/openclaw.json"

# ============================================================================
# PHASE 0A: OWNERSHIP WATCHDOG — starts IMMEDIATELY, before anything else
# The OpenClaw wrapper (root) modifies openclaw.json at startup, making it
# root-owned. The gateway (UID 1001) then can't read it → EACCES crash loop.
# This watchdog continuously re-applies chown+chmod every second so the
# gateway always finds a readable file, no matter what the wrapper does.
# ============================================================================
(
    while true; do
        if [[ -f "$CONFIG" ]]; then
            chown 1001:1001 "$CONFIG" 2>/dev/null || true
            chmod 644 "$CONFIG"      2>/dev/null || true
        fi
        # Also fix the parent directory just in case
        chown 1001:1001 /data/.openclaw 2>/dev/null || true
        sleep 1
    done
) &
CHOWN_WATCHDOG_PID=$!
echo "[Phase 0a] Ownership watchdog started (PID: $CHOWN_WATCHDOG_PID, interval: 1s)"

# ============================================================================
# PHASE 0B: CONFIG PATCH — write allowedOrigins directly into the JSON file
# The wrapper's own allowedOrigins setter fails (exit=1), so we must patch
# the file on disk ourselves before the gateway reads it.
# ============================================================================
echo "[Phase 0b] Patching $CONFIG ..."

# Give the watchdog a moment to start
sleep 0.5

if [[ -f "$CONFIG" ]]; then
    python3 - <<'PYEOF'
import json, sys

CONFIG = "/data/.openclaw/openclaw.json"

try:
    with open(CONFIG, "r") as f:
        cfg = json.load(f)
except Exception as e:
    print(f"[Phase 0b] ERROR reading config: {e}", file=sys.stderr)
    sys.exit(0)  # Non-fatal — watchdog will fix ownership, gateway will retry

cfg.setdefault("gateway", {}).setdefault("controlUi", {})

cfg["gateway"]["controlUi"]["allowedOrigins"] = [
    "https://marvy.up.railway.app",
    "http://127.0.0.1:18789",
    "http://localhost:18789"
]
cfg["gateway"]["controlUi"]["allowInsecureAuth"] = True

try:
    with open(CONFIG, "w") as f:
        json.dump(cfg, f, indent=2)
    print(f"[Phase 0b] allowedOrigins patched OK → {cfg['gateway']['controlUi']['allowedOrigins']}")
except Exception as e:
    print(f"[Phase 0b] ERROR writing config: {e}", file=sys.stderr)
PYEOF

    # Fix ownership immediately after our write (we ran as root → file is root-owned)
    chown 1001:1001 "$CONFIG" 2>/dev/null && echo "[Phase 0b] chown 1001:1001 applied" || echo "[Phase 0b] chown failed"
    chmod 644 "$CONFIG" 2>/dev/null || true
else
    echo "[Phase 0b] Config not found yet — watchdog will fix ownership once it appears"
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

pkill -f "clawmetry"   2>/dev/null || true
pkill -f "rustunnel"   2>/dev/null || true
pkill -f "uvicorn"     2>/dev/null || true
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
# PHASE 3: START BACKGROUND SERVICES
# ============================================================================
echo ""
echo "🚀 PHASE 3: Starting services"

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
# PHASE 4: WATCHDOG (keep background services alive)
# The chown watchdog from Phase 0a handles openclaw.json ownership continuously.
# This loop handles ClawMetry and Rustunnel restarts.
# ============================================================================
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  STARTUP COMPLETE - Watchdog active"
echo "  ClawMetry:  http://127.0.0.1:$CLAWMETRY_PORT"
echo "  Chown loop: PID $CHOWN_WATCHDOG_PID (fixing $CONFIG every 1s)"
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
