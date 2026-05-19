# UTM Processor Web App — Deployment Guide

**What it is:** A free-hosted web app where users paste HTML, add UTM parameters, and download processed files.

**Where it lives:** Vercel (free tier)

**Who accesses it:** Daniel, third parties (via Notion embed)

---

## Quick Start (5 minutes)

### 1. Deploy to Vercel

**Option A: Via CLI (Recommended)**

```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to app directory
cd /Users/g6openclaw/.openclaw/workspace/utm-processor-web

# Deploy
vercel
```

Follow the prompts:
- Link to Vercel account (create free account if needed)
- Project name: `utm-processor`
- Framework: `Other` (it's Flask)
- Deploy

**Your app will be live at:** `utm-processor-xxx.vercel.app`

---

### Option B: Via GitHub (Even Easier)

1. Push the app folder to GitHub
2. Go to vercel.com → "Import Project"
3. Connect GitHub repo
4. Select the folder containing `app.py`
5. Deploy

Vercel auto-deploys on every push.

---

## File Structure

```
utm-processor-web/
├── app.py                 # Flask backend
├── templates/
│   └── index.html        # Web interface
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel config
└── DEPLOYMENT.md        # This file
```

---

## How It Works

### User Flow:
1. Visit `utm-processor-xxx.vercel.app` (or embedded in Notion)
2. Paste HTML content
3. Enter base URL + UTM params
4. Click "Process HTML"
5. Download processed file

### Backend:
- Flask API at `/api/process` (handles HTML + UTM injection)
- Frontend JavaScript (simple form + file handling)
- No database, no authentication needed

---

## Embed in Notion

### Step 1: Copy the Vercel URL
After deployment, you'll have a URL like:
```
https://utm-processor-xxxxx.vercel.app
```

### Step 2: Create Notion Page
1. Open a Notion workspace/page
2. Click "+" to add a new block
3. Choose "Embed"
4. Paste: `https://utm-processor-xxxxx.vercel.app`
5. Click "Embed web page"

### Step 3: Make it Public (Optional)
- Click Share button
- Toggle "Share to web"
- Copy public link
- Share with Daniel and third parties

**They'll see:**
- A clean form interface
- Paste HTML → add params → download file
- No need for accounts or permissions

---

## Customize (Optional)

### Change the branding/colors in `templates/index.html`

Line 22 (gradient colors):
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

Change to your colors. Or update:
- `#667eea` → Primary color
- `#764ba2` → Secondary color

### Update header text
```html
<h1>📊 UTM Processor</h1>
<p>Add UTM tracking parameters to campaign links</p>
```

Change to whatever you want.

---

## Environment Variables (Advanced)

If you need to add API keys or configs later:

1. In Vercel dashboard → Project settings
2. Add to "Environment Variables"
3. Access in Python via `os.getenv('VAR_NAME')`

(Currently, this app doesn't need any env vars.)

---

## Testing Locally (Before Deploying)

```bash
cd /Users/g6openclaw/.openclaw/workspace/utm-processor-web

# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py
```

Visit: `http://localhost:5000`

Test the form, make sure everything works, then deploy to Vercel.

---

## Troubleshooting

**"ModuleNotFoundError: No module named 'flask'"**
→ Run: `pip install -r requirements.txt`

**Deployment fails on Vercel**
→ Check `vercel.json` config is correct
→ Ensure `app.py` is in root directory
→ Check Python version is 3.9+

**Form not submitting**
→ Open browser console (F12 → Console tab)
→ Look for JavaScript errors
→ Most common: URL is wrong (check Vercel deployment URL)

**Downloaded file is empty**
→ Make sure HTML was actually processed
→ Check the "Sample URL" shows correctly in results

---

## Rate Limiting & Security

**Current setup:**
- No rate limiting (free tier of Vercel has limits built-in)
- No authentication (public for all)
- Max file size: 5MB
- Processes synchronously (fast for typical emails)

**If you get heavily used:**
- Vercel will handle scaling automatically
- Add rate limiting: implement Redis/similar
- Add API key authentication if needed

For now, this is wide open — fine for team + limited third-party use.

---

## Support

**Deploy fails?**
→ Check Vercel docs: https://vercel.com/docs/frameworks/flask

**Want to add features?**
→ Edit `app.py` (backend) or `templates/index.html` (frontend)
→ Push to GitHub (if using GitHub integration)
→ Vercel auto-redeploys

**Issues with Notion embed?**
→ Make sure Notion page is shared publicly
→ Try embedding in a test page first
→ Copy/paste the Vercel URL directly (don't use shorteners)

---

## Next Steps

1. **Deploy:** Run `vercel` from the app directory
2. **Test:** Visit the Vercel URL in your browser
3. **Share:** Add to Notion or send link to Daniel
4. **Done!** Users can access it immediately

Total time: ~5 minutes.
