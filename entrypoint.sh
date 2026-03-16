#!/bin/bash
# ============================================================================
# RAILWAY PID 1 ENTRYPOINT
# ============================================================================
# This replaces the OpenClaw wrapper entirely.
#
# WHY: The wrapper drops privileges to UID 1001 for the gateway process,
#      but doctor --fix and config writes happen as root with restrictive
#      permissions (0o600). UID 1001 can't read them → EACCES.
#      No daemon or inotify trick can fully eliminate this race condition.
#
# FIX: Run everything as root. No privilege drop. No EACCES. Ever.
#
# Railway start command:
#   bash /data/workspace/entrypoint.sh
# ============================================================================

set -euo pipefail
umask 000

# Graceful shutdown — kill all children when container stops
cleanup() {
    echo "[entrypoint] SIGTERM received — shutting down..."
    kill $(jobs -p) 2>/dev/null || true
    wait 2>/dev/null || true
    exit 0
}
trap cleanup SIGTERM SIGINT

echo "═══════════════════════════════════════════════════════════════"
echo "  RAILWAY DEPLOYMENT - $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "  Mode: Direct gateway (root, no wrapper, no UID 1001)"
echo "═══════════════════════════════════════════════════════════════"

# ──────────────────────────────────────────────────────────────────
# STEP 1: Fix permissions (blanket — covers previous deploys)
# ──────────────────────────────────────────────────────────────────
mkdir -p /data/.openclaw /tmp/jiti
chmod -R a+rwX /data/.openclaw 2>/dev/null || true
chmod 1777 /tmp/jiti 2>/dev/null || true

# ──────────────────────────────────────────────────────────────────
# STEP 2: Start background services FIRST (ClawMetry, Rustunnel, Backend)
# These don't need port 8080 — they run on their own ports.
# ──────────────────────────────────────────────────────────────────
if [[ -f /data/workspace/start-railway.sh ]]; then
    bash /data/workspace/start-railway.sh &
    echo "[entrypoint] Background services starting (PID $!)"
fi

# ──────────────────────────────────────────────────────────────────
# STEP 3: Run doctor --fix (as root — no EACCES possible)
# ──────────────────────────────────────────────────────────────────
echo "[entrypoint] Running openclaw doctor --fix..."
node /usr/local/lib/node_modules/openclaw/dist/entry.js doctor --fix 2>&1 || true

# ──────────────────────────────────────────────────────────────────
# STEP 4: Fix permissions AGAIN (doctor may have restricted them)
# ──────────────────────────────────────────────────────────────────
chmod -R a+rwX /data/.openclaw 2>/dev/null || true
chmod 666 /data/.openclaw/openclaw.json 2>/dev/null || true
chmod 1777 /tmp/jiti 2>/dev/null || true
chmod -R a+rwX /tmp/jiti 2>/dev/null || true

# ──────────────────────────────────────────────────────────────────
# STEP 5: Patch config (allowedOrigins, allowInsecureAuth)
# ──────────────────────────────────────────────────────────────────
python3 << 'PATCH'
import json, os

config = "/data/.openclaw/openclaw.json"
if os.path.exists(config):
    try:
        with open(config) as f:
            cfg = json.load(f)

        gw  = cfg.setdefault("gateway", {})
        cui = gw.setdefault("controlUi", {})
        cui["allowedOrigins"] = [
            "https://marvy.up.railway.app",
            "http://127.0.0.1:18789",
            "http://localhost:18789",
            "http://127.0.0.1:8080",
            "http://localhost:8080",
        ]
        cui["allowInsecureAuth"] = True

        with open(config, "w") as f:
            json.dump(cfg, f, indent=2)
        os.chmod(config, 0o666)
        print("[entrypoint] Config patched: allowedOrigins + allowInsecureAuth")
    except Exception as e:
        print(f"[entrypoint] Config patch failed (non-fatal): {e}")
else:
    print("[entrypoint] No config file yet — gateway will create it")
PATCH

# ──────────────────────────────────────────────────────────────────
# STEP 6: Start gateway on port 8080 (as root — the whole point)
# exec replaces this shell with the gateway node process.
# ──────────────────────────────────────────────────────────────────
echo "[entrypoint] Starting OpenClaw gateway on :8080 (as root)..."
echo "═══════════════════════════════════════════════════════════════"

exec node /usr/local/lib/node_modules/openclaw/dist/entry.js gateway run \
    --bind 0.0.0.0 \
    --port 8080 \
    --auth none
