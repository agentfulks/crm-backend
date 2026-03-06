#!/bin/bash
# Rollback script - Run this to restore original OpenClaw setup
# Usage: ./rollback-openclaw.sh

echo "🔄 ROLLING BACK OPENCLAW SETUP..."
echo ""

# Find the most recent backup
BACKUP=$(ls -t /data/.openclaw/openclaw.json.backup-* 2>/dev/null | head -1)

if [ -z "$BACKUP" ]; then
    echo "❌ No backup found! Manual recovery needed."
    exit 1
fi

echo "📁 Restoring from: $BACKUP"
cp "$BACKUP" /data/.openclaw/openclaw.json
echo "✅ Config restored"

echo ""
echo "🛑 Stopping proxy server..."
pkill -f "node.*openclaw-proxy.js" 2>/dev/null
pkill -f "python3.*http.server.*3000" 2>/dev/null

echo ""
echo "🚀 Restarting OpenClaw gateway..."
pkill -f "openclaw-gateway" 2>/dev/null
sleep 2
openclaw gateway &

echo ""
echo "⏳ Waiting for gateway to start..."
sleep 3

echo ""
echo "✅ ROLLBACK COMPLETE!"
echo ""
echo "OpenClaw Control UI should be available at:"
echo "  https://marvy.up.railway.app (or http://localhost:8080)"
echo ""
echo "Test it:"
echo "  curl -s http://localhost:8080 | head -1"
