#!/bin/bash
# Start OpenClaw Gateway and Rustunnel

# Kill existing processes
pkill -f "openclaw gateway" 2>/dev/null
killall rustunnel 2>/dev/null
sleep 2

# Start OpenClaw Gateway
openclaw gateway > /tmp/gateway.log 2>&1 &
sleep 5

# Start Rustunnel (update token if needed)
rustunnel http 18789 --server edge.rustunnel.com:4040 --token 3f61720a-c691-4f22-81a9-889cd31e460c > /tmp/rustunnel.log 2>&1 &
sleep 3

echo "Gateway PID: $(pgrep -f 'openclaw gateway')"
echo "Rustunnel PID: $(pgrep -f rustunnel | head -1)"
echo "Check logs: tail -f /tmp/gateway.log /tmp/rustunnel.log"
