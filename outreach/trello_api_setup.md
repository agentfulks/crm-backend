# Trello API Setup Guide

## Problem Summary
- Maton API calls timing out (2+ minute response times)
- Direct Trello API returns "invalid token" errors
- Credentials need to be properly configured in `.env`

---

## Step-by-Step: Getting Trello API Credentials

### Step 1: Get Your API Key

1. Visit: https://trello.com/app-key
2. Log in with your Trello account if prompted
3. You'll see your **API Key** displayed on the page
4. Copy this key - you'll need it for the `.env` file

### Step 2: Generate an Access Token

1. On the same page (https://trello.com/app-key), scroll down to find:
   > "You can manually generate a Token if you need one"
2. Click the **Token** link
3. Authorize the app (click "Allow")
4. Copy the generated **Token** - this is your access token

### Step 3: Get Your Board ID

You already have the Board ID: `699d2728fd2ae8c35d1f7a44`

If you need to find other board IDs:
1. Open the board in Trello web interface
2. Look at the URL: `https://trello.com/b/BOARD_ID/board-name`
3. The Board ID is the part after `/b/`

### Step 4: Configure Your .env File

Create or edit `/data/workspace/outreach/.env`:

```bash
# Trello API Credentials
TRELLO_API_KEY=your_api_key_here
TRELLO_TOKEN=your_token_here
TRELLO_BOARD_ID=699d2728fd2ae8c35d1f7a44

# Optional: List IDs (will be auto-discovered if not set)
# TRELLO_LIST_ID_COLD=xxxx
# TRELLO_LIST_ID_CONTACTED=xxxx
# TRELLO_LIST_ID_FOLLOW_UP=xxxx
# TRELLO_LIST_ID_CONVERTED=xxxx
```

**Security Note:**
- Never commit `.env` to version control
- Add `.env` to your `.gitignore`
- Rotate tokens periodically (Trello doesn't expire them automatically)

---

## Testing Your Credentials

Run the test command:

```bash
curl "https://api.trello.com/1/members/me?key=YOUR_KEY&token=YOUR_TOKEN"
```

You should see your Trello user profile as JSON. If you get "invalid token":
1. Double-check the token was copied correctly (no extra spaces)
2. Ensure you're logged into the same Trello account
3. Try generating a fresh token

---

## API Rate Limits

Trello API limits:
- **300 requests per 10 seconds** per API key
- **100 requests per 10 seconds** per token
- **10 concurrent requests** per token

The `fetch_board.py` script includes rate limiting to stay within these bounds.

---

## Troubleshooting

### "invalid token" Error
- Token may have been revoked or expired
- Re-generate token at https://trello.com/app-key
- Ensure token matches the API key

### "invalid key" Error  
- Wrong API key
- Verify at https://trello.com/app-key

### Timeouts / Slow Responses
- Trello API can be slow during peak hours
- The fetch_board.py script has built-in timeout handling (10s default)
- Results are cached locally to avoid repeated API calls

### 401 Unauthorized
- Token doesn't have access to the board
- Ensure you're a member of the board
- Try the API test above to verify credentials work

---

## Alternative: OAuth (For Multi-User Apps)

If building a multi-user application, use OAuth instead of personal tokens:

1. Register app at: https://trello.com/power-ups/admin
2. Implement OAuth flow
3. Store user-specific tokens securely

For this single-board integration, personal tokens are simpler and sufficient.

---

## Next Steps

1. Get your credentials using the steps above
2. Add them to `.env`
3. Run `python fetch_board.py` to verify everything works
4. Check the cache file `trello_cache.json` for persisted data
