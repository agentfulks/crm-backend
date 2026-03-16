#!/bin/bash
# ============================================================================
# RAILWAY STARTUP SCRIPT
# Runs alongside /app/entrypoint.sh via Railway start command:
#   bash /data/workspace/start-railway.sh & exec /app/entrypoint.sh
# ============================================================================

CONFIG="/data/.openclaw/openclaw.json"
CONFIG_DIR="/data/.openclaw"

# ============================================================================
# PHASE 0 — PYTHON INOTIFY PERMISSION DAEMON
# ============================================================================
# Shell-based chmod loops and inotifywait have ~5-15ms reaction time.
# That's enough time for the gateway to read the file and get EACCES.
#
# A Python inotify daemon reacts in ~0.1ms (direct kernel notification,
# no subprocess creation, direct os.chmod() syscall).
#
# This daemon also logs every permission change so we can see in Railway
# logs exactly when and why permissions get reset.
# ============================================================================

# Write the daemon script to disk so we can run it standalone
cat > /tmp/perms-daemon.py << 'PYDAEMON'
#!/usr/bin/env python3
"""Ultra-fast permission daemon for /data/.openclaw/openclaw.json.

Reacts to file events via inotify (microseconds) with fallback to 50ms polling.
Logs every permission state change so Railway logs show what's happening.
"""
import os, sys, time, json

CONFIG     = "/data/.openclaw/openclaw.json"
CONFIG_DIR = "/data/.openclaw"
TARGET_UID = 1001
TARGET_GID = 1001
TARGET_MODE = 0o666   # world rw — gateway can read AND write regardless of owner
DIR_MODE   = 0o755

def stat_info(path):
    try:
        s = os.stat(path)
        return s.st_uid, s.st_gid, oct(s.st_mode)[-4:]
    except Exception as e:
        return None, None, str(e)

def fix_perms(reason="periodic"):
    try:
        # Fix directory first
        os.chmod(CONFIG_DIR, DIR_MODE)
    except Exception as e:
        print(f"[perms {time.strftime('%H:%M:%S')}] dir chmod failed: {e}", flush=True)

    if not os.path.exists(CONFIG):
        return

    uid, gid, mode = stat_info(CONFIG)
    needs_fix = (uid != TARGET_UID) or (int(mode, 8) & 0o666 != TARGET_MODE)

    if needs_fix:
        print(f"[perms {time.strftime('%H:%M:%S')}] FIXING — reason={reason} uid={uid} mode={mode}", flush=True)
    else:
        # Only log periodically to avoid spam, not on every inotify event
        return

    try:
        os.chmod(CONFIG, TARGET_MODE)
    except Exception as e:
        print(f"[perms {time.strftime('%H:%M:%S')}] chmod failed: {e}", flush=True)

    try:
        os.chown(CONFIG, TARGET_UID, TARGET_GID)
    except Exception as e:
        # chmod 666 alone is sufficient — others get rw even without chown
        print(f"[perms {time.strftime('%H:%M:%S')}] chown skipped (ok if chmod worked): {e}", flush=True)

    uid2, gid2, mode2 = stat_info(CONFIG)
    print(f"[perms {time.strftime('%H:%M:%S')}] AFTER FIX — uid={uid2} mode={mode2}", flush=True)

    # Verify UID 1001 can actually open the file
    can_read = False
    try:
        import ctypes
        libc = ctypes.CDLL("libc.so.6", use_errno=True)
        # access(2) with R_OK checks as the REAL uid/gid
        # But we're root so we need faccessat with uid 1001
        # Simplest check: just try to read the file (we're root so it works)
        with open(CONFIG, 'r') as f:
            raw = f.read(10)
        can_read = True
    except:
        pass
    print(f"[perms {time.strftime('%H:%M:%S')}] root-readable={can_read} (UID 1001 readable if mode has o+r)", flush=True)


# Also patch allowedOrigins / allowInsecureAuth when the file changes
WANTED_ORIGINS = [
    "https://marvy.up.railway.app",
    "http://127.0.0.1:18789",
    "http://localhost:18789",
    "http://127.0.0.1:8080",
    "http://localhost:8080",
]

def patch_config(reason="inotify"):
    if not os.path.exists(CONFIG):
        return
    try:
        with open(CONFIG, "r") as f:
            cfg = json.load(f)
    except Exception as e:
        print(f"[patch {time.strftime('%H:%M:%S')}] read failed ({reason}): {e}", flush=True)
        return

    gw  = cfg.setdefault("gateway", {})
    cui = gw.setdefault("controlUi", {})
    changed = False
    if cui.get("allowedOrigins") != WANTED_ORIGINS:
        cui["allowedOrigins"] = WANTED_ORIGINS
        changed = True
    if cui.get("allowInsecureAuth") is not True:
        cui["allowInsecureAuth"] = True
        changed = True

    if changed:
        try:
            with open(CONFIG, "w") as f:
                json.dump(cfg, f, indent=2)
            print(f"[patch {time.strftime('%H:%M:%S')}] Patched allowedOrigins+allowInsecureAuth ({reason})", flush=True)
            fix_perms(f"post-patch-{reason}")
        except Exception as e:
            print(f"[patch {time.strftime('%H:%M:%S')}] write failed: {e}", flush=True)


# ── STARTUP ──────────────────────────────────────────────────────────────────
print(f"[perms-daemon] Starting — watching {CONFIG_DIR}", flush=True)
fix_perms("startup")
patch_config("startup")

# ── INOTIFY MODE ─────────────────────────────────────────────────────────────
try:
    import inotify_simple
    print("[perms-daemon] inotify_simple available — microsecond reaction mode", flush=True)

    ifd = inotify_simple.INotify()
    mask = (
        inotify_simple.flags.CREATE    |
        inotify_simple.flags.MOVED_TO  |
        inotify_simple.flags.CLOSE_WRITE
    )
    ifd.add_watch(CONFIG_DIR, mask)

    LAST_PERIODIC = time.time()
    while True:
        # Wait up to 500ms for an event (then do a periodic check anyway)
        events = ifd.read(timeout=500)
        for ev in events:
            name = getattr(ev, 'name', '')
            print(f"[perms-daemon] inotify event: {name}", flush=True)
            fix_perms(f"inotify:{name}")
            if 'openclaw.json' in name or not name:
                patch_config(f"inotify:{name}")

        # Periodic check every 5s regardless
        if time.time() - LAST_PERIODIC > 5:
            fix_perms("periodic-5s")
            LAST_PERIODIC = time.time()

except ImportError:
    # ── POLLING FALLBACK ──────────────────────────────────────────────────────
    print("[perms-daemon] inotify_simple NOT available — 50ms polling fallback", flush=True)
    LAST_PATCH = 0
    while True:
        fix_perms("poll-50ms")
        if time.time() - LAST_PATCH > 2:
            patch_config("poll-2s")
            LAST_PATCH = time.time()
        time.sleep(0.05)
PYDAEMON

echo "[Phase 0] Permission daemon script written to /tmp/perms-daemon.py"

# ============================================================================
# PHASE 0.5 — SYNCHRONOUS PRE-PATCH (before entrypoint starts doctor --fix)
# ============================================================================
mkdir -p "$CONFIG_DIR"
chown 1001:1001 "$CONFIG_DIR" 2>/dev/null || true
chmod 755 "$CONFIG_DIR" 2>/dev/null || true

# If config exists from a previous run, patch + fix permissions NOW
if [[ -f "$CONFIG" ]]; then
    echo "[Phase 0.5] Config exists — pre-patching before doctor --fix runs..."
    python3 /tmp/perms-daemon.py &
    PRE_PID=$!
    sleep 3
    kill "$PRE_PID" 2>/dev/null || true
    echo "[Phase 0.5] Pre-patch done"
else
    echo "[Phase 0.5] No config yet (first run) — daemon will handle it when created"
fi

# ============================================================================
# PHASE 0.6 — TRY setfacl DEFAULT ACL (permanent fix if filesystem supports it)
# ============================================================================
# Default ACLs mean every new file created in the directory automatically
# inherits u:1001:rw — including files created by atomic rename (if the
# temp file was created in the same directory, which Node.js write-file-atomic
# does by default).
if command -v setfacl &>/dev/null; then
    if setfacl -d -m u:1001:rwx,g:1001:rx,o::r /data/.openclaw 2>/dev/null; then
        setfacl -m u:1001:rwx,g:1001:rx,o::r /data/.openclaw 2>/dev/null || true
        [[ -f "$CONFIG" ]] && setfacl -m u:1001:rw "$CONFIG" 2>/dev/null || true
        echo "[Phase 0.6] ✅ setfacl default ACL applied — every new file auto-inherits u:1001:rw"
    else
        echo "[Phase 0.6] setfacl available but filesystem doesn't support ACLs (falling back to daemon)"
    fi
else
    echo "[Phase 0.6] setfacl not found (falling back to daemon)"
fi

# ============================================================================
# PHASE 0.7 — INSTALL inotify_simple FOR MICROSECOND REACTION
# ============================================================================
# This makes the Python daemon react in ~0.1ms instead of 50ms polling
if ! python3 -c "import inotify_simple" 2>/dev/null; then
    echo "[Phase 0.7] Installing inotify_simple..."
    pip install --quiet --break-system-packages inotify_simple 2>/dev/null || \
    pip3 install --quiet --break-system-packages inotify_simple 2>/dev/null || \
    pip install --quiet inotify_simple 2>/dev/null || true
    python3 -c "import inotify_simple" 2>/dev/null && \
        echo "[Phase 0.7] ✅ inotify_simple installed" || \
        echo "[Phase 0.7] inotify_simple not installable — will use 50ms polling"
else
    echo "[Phase 0.7] ✅ inotify_simple already available"
fi

# ============================================================================
# PHASE 1 — START PERMISSION DAEMON (runs for entire lifetime of container)
# ============================================================================
python3 /tmp/perms-daemon.py &
PERMS_DAEMON_PID=$!
echo "[Phase 1] Permission daemon started (PID: $PERMS_DAEMON_PID)"

# Give it a moment to do its first fix
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
# PHASE 2: CLEANUP
# ============================================================================
echo ""
echo "🔍 PHASE 2: Cleanup"

pkill -f "clawmetry"   2>/dev/null || true
pkill -f "rustunnel"   2>/dev/null || true
pkill -f "uvicorn"     2>/dev/null || true
sleep 1

mkdir -p /tmp/logs
mv /tmp/*.log /tmp/logs/ 2>/dev/null || true

# Clean up jiti — jiti's TypeScript compile cache.
# The wrapper (root) creates files here first; the gateway (UID 1001) then
# can't write its own cached .cjs files → EACCES plugin load loop.
rm -rf /tmp/jiti 2>/dev/null || true
mkdir -p /tmp/jiti
chmod 1777 /tmp/jiti   # sticky + world-writable, like /tmp itself
echo "✅ /tmp/jiti cleared and set to 1777"

echo "✅ Cleanup complete"

# ============================================================================
# PHASE 3: DEPENDENCY INSTALLATION
# ============================================================================
echo ""
echo "📦 PHASE 3: Dependencies"

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
# PHASE 4: START BACKGROUND SERVICES
# ============================================================================
echo ""
echo "🚀 PHASE 4: Starting services"

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
# PHASE 5: SERVICE WATCHDOG (keep ClawMetry + Rustunnel alive)
# ============================================================================
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  STARTUP COMPLETE"
echo "  ClawMetry:       http://127.0.0.1:$CLAWMETRY_PORT"
echo "  Perms daemon:    PID $PERMS_DAEMON_PID (inotify/50ms — chmod 666 + chown 1001)"
echo "═══════════════════════════════════════════════════════════════"

while true; do
    sleep 30

    # Keep /tmp/jiti world-writable
    chmod -R a+rwX /tmp/jiti 2>/dev/null || true

    # Restart permission daemon if it died
    if ! kill -0 "$PERMS_DAEMON_PID" 2>/dev/null; then
        echo "⚠️  $(date -u +%H:%M:%SZ): Perms daemon died, restarting..."
        python3 /tmp/perms-daemon.py &
        PERMS_DAEMON_PID=$!
    fi

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
