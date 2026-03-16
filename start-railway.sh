#!/bin/bash
# ============================================================================
# RAILWAY STARTUP SCRIPT
# Runs alongside /app/entrypoint.sh via Railway start command:
#   bash /data/workspace/start-railway.sh & exec /app/entrypoint.sh
# ============================================================================

CONFIG="/data/.openclaw/openclaw.json"

# ============================================================================
# PATCH HELPER — called both synchronously and from the watchdog
# ============================================================================
do_patch() {
    python3 - <<'PYEOF' 2>/dev/null
import json, sys

CONFIG = "/data/.openclaw/openclaw.json"
WANTED_ORIGINS = [
    "https://marvy.up.railway.app",
    "http://127.0.0.1:18789",
    "http://localhost:18789",
    "http://127.0.0.1:8080",
    "http://localhost:8080",
]

try:
    with open(CONFIG, "r") as f:
        cfg = json.load(f)
except Exception as e:
    print(f"[patch] Cannot read config: {e}", flush=True)
    sys.exit(0)

gw = cfg.setdefault("gateway", {})
cui = gw.setdefault("controlUi", {})

current_origins = cui.get("allowedOrigins")
current_insecure = cui.get("allowInsecureAuth")

changed = False
if current_origins != WANTED_ORIGINS:
    cui["allowedOrigins"] = WANTED_ORIGINS
    changed = True
if current_insecure is not True:
    cui["allowInsecureAuth"] = True
    changed = True

if changed:
    try:
        with open(CONFIG, "w") as f:
            json.dump(cfg, f, indent=2)
        print(f"[patch] Updated → allowedOrigins={WANTED_ORIGINS} allowInsecureAuth=True", flush=True)
    except Exception as e:
        print(f"[patch] Write failed: {e}", flush=True)
else:
    print(f"[patch] Already correct (origins={current_origins})", flush=True)
PYEOF
    chown 1001:1001 "$CONFIG" 2>/dev/null || true
    chmod 644 "$CONFIG"       2>/dev/null || true
}

# ============================================================================
# PHASE -1: SYNCHRONOUS PRE-PATCH (runs immediately, before the watchdog loop)
# ============================================================================
# The volume persists between restarts. If openclaw.json already exists,
# patch it NOW — before entrypoint.sh's doctor has a chance to overwrite it.
if [[ -f "$CONFIG" ]]; then
    echo "[Phase -1] Config exists, patching immediately..."
    do_patch
    echo "[Phase -1] Pre-patch done"
else
    echo "[Phase -1] Config not yet created (first run), watchdog will patch when it appears"
fi

# Also fix the parent directory
chown 1001:1001 /data/.openclaw 2>/dev/null || true

# ============================================================================
# PHASE 0: CONTINUOUS CONFIG+OWNERSHIP WATCHDOG
#
# Problem: The OpenClaw wrapper runs "openclaw doctor --fix" on every startup,
# which atomically REWRITES openclaw.json — clobbering both the file ownership
# (root takes it back) AND our allowedOrigins patch.
#
# Additionally, the gateway caches allowedOrigins at startup. So we need TWO
# mechanisms:
#   1. Keep the config patched (watchdog)
#   2. Restart the gateway ONCE after it starts, so it re-reads allowedOrigins
# ============================================================================
ALLOWED_ORIGINS='["https://marvy.up.railway.app","http://127.0.0.1:18789","http://localhost:18789"]'

(
    GATEWAY_RESTARTED=false
    GATEWAY_RESTART_WAIT=30  # seconds after gateway starts before we trigger restart

    while true; do
        if [[ -f "$CONFIG" ]]; then
            do_patch

            # ----------------------------------------------------------------
            # ONE-SHOT GATEWAY RESTART
            # The gateway caches allowedOrigins at startup. After patching,
            # kill the gateway once so the wrapper restarts it with the patched
            # config. We do this exactly once, 30 seconds after startup.
            # ----------------------------------------------------------------
            if [[ "$GATEWAY_RESTARTED" == "false" ]]; then
                UPTIME_SECS=$(awk '{print int($1)}' /proc/uptime 2>/dev/null || echo 0)
                CONTAINER_UPTIME=$((UPTIME_SECS))
                if [[ $CONTAINER_UPTIME -gt $GATEWAY_RESTART_WAIT ]]; then
                    GW_PID=$(pgrep -f "entry.js gateway" 2>/dev/null | head -1)
                    if [[ -n "$GW_PID" ]]; then
                        echo "[watchdog] Triggering ONE-TIME gateway restart (PID $GW_PID) to reload allowedOrigins..."
                        kill "$GW_PID" 2>/dev/null || true
                        GATEWAY_RESTARTED=true
                        echo "[watchdog] Gateway killed — wrapper should restart it with patched config"
                    fi
                fi
            fi
        fi

        # Keep parent directory accessible
        chown 1001:1001 /data/.openclaw 2>/dev/null || true

        # Keep /tmp/jiti world-writable so jiti cache writes never EACCES
        chmod -R a+rwX /tmp/jiti 2>/dev/null || true

        sleep 1
    done
) &
WATCHDOG_PID=$!
echo "[Phase 0] Config+ownership watchdog started (PID: $WATCHDOG_PID, interval: 1s)"
echo "[Phase 0] Watching: $CONFIG"
echo "[Phase 0] Will enforce allowedOrigins: $ALLOWED_ORIGINS"
echo "[Phase 0] Will trigger one-time gateway restart after ${GATEWAY_RESTART_WAIT:-30}s"

# Give the watchdog a moment before continuing
sleep 2

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

# Fix /tmp/jiti — jiti's TypeScript compile cache.
# OpenClaw processes running as root create files here first; the gateway
# (UID 1001) then can't write its own cached .cjs files → EACCES loop.
# Nuke it so it's recreated fresh with the right permissions.
rm -rf /tmp/jiti 2>/dev/null || true
mkdir -p /tmp/jiti
chmod 1777 /tmp/jiti  # sticky + world-writable, like /tmp itself
echo "✅ /tmp/jiti cleared and set to 1777"

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
# The config+ownership watchdog from Phase 0 handles openclaw.json continuously.
# This loop handles ClawMetry and Rustunnel restarts.
# ============================================================================
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  STARTUP COMPLETE - Watchdog active"
echo "  ClawMetry:  http://127.0.0.1:$CLAWMETRY_PORT"
echo "  Watchdog:   PID $WATCHDOG_PID (patching allowedOrigins + chown every 1s)"
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
