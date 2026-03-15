#!/bin/bash
# Install sudo if missing and grant openclaw passwordless superuser on every boot
if ! command -v sudo &>/dev/null; then
    apt-get update -qq && apt-get install -y sudo
fi
mkdir -p /etc/sudoers.d
echo "openclaw ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/openclaw
chmod 440 /etc/sudoers.d/openclaw
# Fix workspace ownership
chown -R 1001:1001 /data/workspace
cd /data/workspace/backend
exec /data/workspace/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
