# UTM Processor Web App

A simple, free-to-host web application for processing HTML files with UTM campaign tracking parameters.

**Status:** ✅ Ready to deploy

---

## What It Does

Users paste HTML (email, landing page, etc.) and provide:
- Base URL (where links should point)
- UTM parameters (source, campaign, medium, term, content)

The app replaces all links in the HTML with UTM-tagged versions and returns a download-ready file.

**Example:**
```
Input:  <a href="https://example.com/offer">Click here</a>
Output: <a href="https://example.com/offer?utm_source=The_Early_Bird&utm_campaign=ddr_may18">Click here</a>
```

---

## Features

- ✅ Paste HTML directly (no file upload needed)
- ✅ Supports any UTM parameters (source, campaign, medium, term, content)
- ✅ Preserves all HTML structure and styling
- ✅ Shows sample link after processing
- ✅ One-click file download
- ✅ Mobile-friendly interface
- ✅ No account required
- ✅ Free hosting (Vercel)

---

## Deployment (5 minutes)

### Prerequisites
- Free Vercel account (vercel.com)
- Node.js or Vercel CLI

### Deploy

```bash
cd utm-processor-web
vercel
```

Follow the prompts. Your app will be live at a URL like:
```
https://utm-processor-xxxxx.vercel.app
```

See `DEPLOYMENT.md` for detailed instructions.

---

## Run Locally

```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
python app.py
```

Visit `http://localhost:5000`

---

## Embed in Notion

1. Deploy to Vercel (get the URL)
2. Create a Notion page
3. Add an "Embed" block
4. Paste the Vercel URL
5. Share the Notion page publicly

See `NOTION_SETUP.md` for details.

---

## File Structure

```
utm-processor-web/
├── app.py                 # Flask backend
├── templates/
│   └── index.html        # Web interface (HTML + CSS + JS)
├── requirements.txt      # Python dependencies
├── vercel.json          # Vercel configuration
├── DEPLOYMENT.md        # How to deploy
├── NOTION_SETUP.md      # How to embed in Notion
└── README.md            # This file
```

---

## Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** HTML + CSS + JavaScript
- **Hosting:** Vercel (free tier)
- **Dependencies:** Flask, Werkzeug

---

## API Endpoints

### POST `/api/process`
Process HTML with UTM parameters.

**Request:**
```json
{
  "html": "<a href='...'>link</a>",
  "base_url": "https://example.com/offer",
  "utm_source": "The_Early_Bird",
  "utm_campaign": "ddr_may18",
  "utm_medium": "email",
  "utm_term": "may18",
  "utm_content": "featured"
}
```

**Response:**
```json
{
  "success": true,
  "processed_html": "<a href='https://example.com/offer?utm_source=...'>link</a>",
  "links_found": 42,
  "utm_url": "https://example.com/offer?utm_source=The_Early_Bird&utm_campaign=ddr_may18&utm_medium=email&utm_term=may18&utm_content=featured",
  "utm_params": { ... }
}
```

### POST `/api/download`
Download processed HTML as a `.html` file.

**Request:**
```json
{
  "html": "processed HTML content",
  "filename": "campaign.html"
}
```

**Response:** File download (attachment)

---

## Customization

**Change colors/branding:**
Edit `templates/index.html` (lines 22-28 in the `<style>` section)

**Change header text:**
Edit `templates/index.html` (lines 114-116)

**Add new features:**
Edit `app.py` (backend) or `templates/index.html` (frontend)

---

## Limitations

- Max file size: 5MB (Vercel limit)
- No database (no user accounts)
- No authentication (public access)
- Processes synchronously (should be instant for typical emails)

---

## Security

- No sensitive data stored
- No authentication required
- Input sanitization for filenames
- CORS not restricted (accessible from anywhere)
- HTTPS enforced by Vercel

---

## Support

**Deployment issues?**
→ Check `DEPLOYMENT.md`

**Notion embedding issues?**
→ Check `NOTION_SETUP.md`

**Feature requests or bugs?**
→ Edit the code and redeploy

---

## License

Internal tool. Use freely within the organization.

---

## Quick Links

- **Deploy:** `vercel` (from this directory)
- **Test locally:** `python app.py` then visit `http://localhost:5000`
- **Embed in Notion:** Copy Vercel URL, add to Notion page as embed
- **Share:** Send Vercel URL or Notion page link to users

---

**Ready to ship!** 🚀
