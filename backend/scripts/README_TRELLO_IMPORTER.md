# Trello Card Importer

Automated import of outreach cards from markdown files to Trello board.

## Quick Start

1. **Copy and configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Trello credentials
   ```

2. **Get Trello credentials:**
   - API Key: https://trello.com/app-key
   - API Token: Generated on the same page
   - Board ID: Open your board, copy ID from URL `https://trello.com/b/BOARD_ID/name`

3. **Install dependencies:**
   ```bash
   pip install requests python-dotenv
   # Or: uv pip install requests python-dotenv
   ```

## Usage

### Dry run (preview without creating cards)
```bash
python scripts/trello_importer.py --dry-run
```

### Import all batches
```bash
python scripts/trello_importer.py
```

### Import specific file
```bash
python scripts/trello_importer.py --file TRELLO_IMPORT_BATCH_2026-03-09-CYCLE25.md
```

### Import to different list
```bash
python scripts/trello_importer.py --list "Awaiting Approval"
```

## Features

- **Idempotent**: Skips cards that already exist (by name)
- **Rate limited**: Respects Trello's 10 cards/minute limit
- **Batch processing**: Handles multiple markdown files
- **Label support**: Auto-tags VC vs BDR cards
- **Error handling**: Continues on individual card failures

## File Structure

Reads markdown files from `../../output/trello-import-ready/` with format:
- `TRELLO_IMPORT_BATCH_YYYY-MM-DD-CYCLE##.md` (VC cards)
- `TRELLO_IMPORT_BATCH_YYYY-MM-DD-CYCLE##-BDR.md` (BDR cards)

## Rate Limiting

Trello API allows 10 cards/minute. The importer:
- Waits 6 seconds between card creations
- Waits 2 seconds between batch files
- Logs progress for monitoring

## Troubleshooting

**"Missing Trello credentials"**
- Ensure `.env` file exists with all required values
- Run from `/data/workspace/backend/` directory

**"List not found"**
- Check that `TRELLO_TARGET_LIST` matches exact list name
- Default is "To Do" — update .env if different

**Cards not appearing**
- Check Trello board filter (cards may have been created but filtered out)
- Check `trello_importer.py` logs for errors
