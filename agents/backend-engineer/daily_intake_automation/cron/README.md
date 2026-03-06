# Daily Intake Automation - Cron Configuration

## Quick Setup

### Option 1: Crontab (Simplest)

Add to your user's crontab:

```bash
# Edit crontab
crontab -e

# Add this line for 8am daily execution
0 8 * * * cd /data/workspace/agents/backend-engineer/daily_intake_automation && /usr/bin/python3 scripts/daily_intake.py >> /var/log/daily_intake.log 2>&1
```

### Option 2: Systemd Timer (Recommended for Production)

1. Copy the service and timer files:
```bash
sudo cp daily-intake.service /etc/systemd/system/
sudo cp daily-intake.timer /etc/systemd/system/
```

2. Reload systemd:
```bash
sudo systemctl daemon-reload
```

3. Enable and start the timer:
```bash
sudo systemctl enable daily-intake.timer
sudo systemctl start daily-intake.timer
```

4. Check timer status:
```bash
sudo systemctl status daily-intake.timer
sudo systemctl list-timers --all
```

### Option 3: Docker (Containerized)

See `docker-compose.cron.yml` for containerized scheduling.

## Monitoring

### Logs

```bash
# View systemd journal
sudo journalctl -u daily-intake.service -f

# View log file (if using crontab)
tail -f /var/log/daily_intake.log
```

### Health Check

```bash
# Run manually to verify setup
python scripts/daily_intake.py --dry-run
```

## Environment Setup

Ensure environment variables are available to the cron job:

### Option A: Environment File

Create `/etc/default/daily-intake`:
```bash
DATABASE_URL=postgresql://...
TRELLO_API_KEY=...
# ... etc
```

Update service file to load it:
```ini
[Service]
EnvironmentFile=/etc/default/daily-intake
```

### Option B: Dotenv File

Place `.env` file in the project directory. The script will load it automatically.

## Troubleshooting

### Permission Issues

Ensure the user running the cron job has:
- Read access to the project directory
- Write access to log files
- Network access to Trello API and database

### Timezone Issues

Verify your cron is using the correct timezone:
```bash
crontab -e
# Add at the top:
TZ=America/New_York
```
