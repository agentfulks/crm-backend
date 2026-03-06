#!/bin/bash
# Setup script for OpenClaw + VC Outreach Dashboard integration
# This configures the system to serve both on port 8080
# 
# Usage: ./setup-openclaw-dashboard.sh
# Rollback: ./rollback-openclaw.sh (if anything breaks)

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Setting up OpenClaw + VC Outreach Dashboard               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Creating backup...${NC}"
BACKUP_FILE="/data/.openclaw/openclaw.json.backup-$(date +%Y%m%d-%H%M%S)"
cp /data/.openclaw/openclaw.json "$BACKUP_FILE"
echo -e "${GREEN}✅ Backup created: $BACKUP_FILE${NC}"
echo ""

echo -e "${YELLOW}Step 2: Stopping current OpenClaw gateway...${NC}"
pkill -f "openclaw-gateway" 2>/dev/null || true
pkill -f "python3.*http.server.*8080" 2>/dev/null || true
sleep 2
echo -e "${GREEN}✅ OpenClaw stopped${NC}"
echo ""

echo -e "${YELLOW}Step 3: Modifying OpenClaw config for port 8081...${NC}"
# Use sed to change port from 18789 to 8081
sed -i 's/"port": 18789/"port": 8081/g' /data/.openclaw/openclaw.json || true
echo -e "${GREEN}✅ Config updated (OpenClaw now on port 8081)${NC}"
echo ""

echo -e "${YELLOW}Step 4: Starting OpenClaw on port 8081...${NC}"
openclaw gateway &
OPENCLAW_PID=$!
sleep 3

# Check if OpenClaw started
if ! kill -0 $OPENCLAW_PID 2>/dev/null; then
    echo -e "${RED}❌ OpenClaw failed to start! Rolling back...${NC}"
    cp "$BACKUP_FILE" /data/.openclaw/openclaw.json
    openclaw gateway &
    exit 1
fi

echo -e "${GREEN}✅ OpenClaw running on port 8081 (PID: $OPENCLAW_PID)${NC}"
echo ""

echo -e "${YELLOW}Step 5: Verifying frontend build...${NC}"
if [ ! -d "/data/workspace/frontend/dist" ]; then
    echo -e "${RED}❌ Frontend dist folder not found! Building...${NC}"
    cd /data/workspace/frontend
    npm run build
fi
echo -e "${GREEN}✅ Frontend ready${NC}"
echo ""

echo -e "${YELLOW}Step 6: Starting proxy server on port 8080...${NC}"
cd /data/workspace
python3 openclaw-proxy.py &
PROXY_PID=$!
sleep 2

# Check if proxy started
if ! kill -0 $PROXY_PID 2>/dev/null; then
    echo -e "${RED}❌ Proxy failed to start!${NC}"
    echo "Check logs: cat /tmp/openclaw-proxy.log"
    exit 1
fi

echo -e "${GREEN}✅ Proxy running on port 8080 (PID: $PROXY_PID)${NC}"
echo ""

echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  SETUP COMPLETE!                                          ${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Access your applications:"
echo ""
echo "  🎮 OpenClaw Control UI:"
echo "     http://marvy.up.railway.app/"
echo ""
echo "  📊 VC Outreach Dashboard:"
echo "     http://marvy.up.railway.app/dashboard/"
echo ""
echo "Health check:"
echo "  curl http://localhost:8080/health"
echo ""
echo -e "${YELLOW}IMPORTANT:${NC}"
echo "  If anything breaks, run: ./rollback-openclaw.sh"
echo ""
echo "PIDs (for reference):"
echo "  OpenClaw: $OPENCLAW_PID"
echo "  Proxy:    $PROXY_PID"
echo ""
