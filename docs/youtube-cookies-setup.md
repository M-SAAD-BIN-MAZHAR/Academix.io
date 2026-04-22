# YouTube Cookies Setup for Production (Railway)

When deploying Academix.io to production environments like Railway, YouTube may detect automated access and block video downloads. This guide shows how to set up YouTube cookies to bypass this restriction.

## Why This Happens

Cloud servers (Railway, Heroku, AWS, etc.) are often flagged by YouTube's bot detection system. The error you'll see is:

```
ERROR: [youtube] Sign in to confirm you're not a bot. Use --cookies-from-browser or --cookies for the authentication.
```

## Solution: YouTube Cookies

### Step 1: Export YouTube Cookies

1. **Install Browser Extension:**
   - Chrome: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   - Firefox: [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)

2. **Export Cookies:**
   - Visit YouTube.com in your browser
   - Make sure you're logged in (optional but recommended)
   - Click the extension icon
   - Click "Export" or "Download"
   - Save as `youtube_cookies.txt`

### Step 2: Upload to Railway

1. **Add to Your Project:**
   ```bash
   # Add cookies file to your project root
   cp ~/Downloads/youtube_cookies.txt ./cua/youtube_cookies.txt
   ```

2. **Update .gitignore:**
   ```bash
   # Add to .gitignore to avoid committing cookies
   echo "youtube_cookies.txt" >> .gitignore
   ```

3. **Deploy to Railway:**
   - Upload the cookies file to your Railway deployment
   - Or use Railway CLI: `railway run --service your-service`

### Step 3: Configure Environment Variable

In your Railway dashboard:

1. Go to your project → Variables
2. Add new variable:
   - **Name:** `YOUTUBE_COOKIE_PATH`
   - **Value:** `/app/youtube_cookies.txt` (or your deployment path)

### Step 4: Verify Setup

The system will automatically use cookies when available. You should see in logs:

```
INFO: Using cookie file: /app/youtube_cookies.txt
INFO: YouTube extraction successful using method: youtube
```

## Alternative Solutions

### 1. Wait and Retry
Sometimes the bot detection is temporary. Wait 5-10 minutes and try again.

### 2. Different Videos
Try transcribing a different YouTube video to see if the issue is video-specific.

### 3. Local Development
The issue typically doesn't occur in local development, only in production.

## Troubleshooting

### Cookies Not Working
- Ensure cookies are in Netscape format (the extension should handle this)
- Make sure the file path is correct in Railway
- Check that the cookies file was uploaded properly

### Still Getting Bot Detection
- Try refreshing your cookies (export new ones)
- Ensure you're logged into YouTube when exporting
- Contact support if the issue persists

## Security Note

- Never commit cookies to your Git repository
- Cookies contain authentication information
- Regenerate cookies periodically for security
- Use environment variables for the cookie path

## Support

If you continue experiencing issues:
1. Check Railway logs for detailed error messages
2. Verify environment variables are set correctly
3. Try with a fresh set of cookies
4. Contact the development team with specific error logs