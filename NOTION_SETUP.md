# UTM Processor in Notion — Setup Guide

**Goal:** Embed the UTM processor app into a Notion page so Daniel and third parties can access it.

---

## Step 1: Get the Vercel URL

After deploying, you'll have a URL like:
```
https://utm-processor-xxxxx.vercel.app
```

Save this—you'll use it in Notion.

---

## Step 2: Create a Notion Page

1. Open your Notion workspace
2. Create a new page (or use an existing one)
3. Give it a title: **"UTM Campaign Processor"**

---

## Step 3: Add the Embed

1. In the Notion page, click **"+"** (add block)
2. Search for **"Embed"**
3. Click **"Embed"** block type
4. Paste the Vercel URL:
   ```
   https://utm-processor-xxxxx.vercel.app
   ```
5. Press Enter

The embedded app should now appear in Notion!

---

## Step 4: Add Instructions (Optional but Recommended)

Add a text block above the embed explaining how to use it:

```markdown
# UTM Campaign Processor

Use this tool to process HTML files with UTM tracking parameters.

## How to use:
1. Paste your HTML email template or landing page
2. Enter the base URL (e.g., https://gsiexchange.com/offer)
3. Fill in UTM parameters:
   - **Source** (e.g., The_Early_Bird)
   - **Campaign** (e.g., ddr_may18)
   - **Medium** (e.g., email)
   - **Term** (optional, e.g., may18)
   - **Content** (optional, e.g., featured)
4. Click "Process HTML"
5. Download the processed file

Your links will be automatically tagged with the UTM parameters you specified.
```

---

## Step 5: Share with Third Parties

### Option A: Share the Notion Page Publicly

1. Click **Share** (top right of Notion page)
2. Toggle **"Share to web"**
3. Copy the public link
4. Send to Daniel and third parties

They can access it directly—no Notion account needed.

### Option B: Share the Vercel URL Directly

Just send them:
```
https://utm-processor-xxxxx.vercel.app
```

They get the app without Notion. Your choice!

---

## What It Looks Like

When embedded, users see:

```
┌─────────────────────────────────────────┐
│  📊 UTM Processor                       │
│  Add UTM tracking parameters to links   │
├─────────────────────────────────────────┤
│ HTML Content *                          │
│ ┌─────────────────────────────────────┐ │
│ │ [Paste HTML here]                   │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Base URL *                              │
│ [https://example.com/offer]             │
│                                         │
│ UTM Parameters                          │
│ [Source]   [Campaign]                   │
│ [Medium]   [Term]                       │
│ [Content]                               │
│                                         │
│ Output Filename                         │
│ [campaign.html]                         │
│                                         │
│ [Process HTML]  [Download File]         │
│                                         │
│ ✓ 42 links found and updated           │
│ Sample: https://example.com/offer?...  │
└─────────────────────────────────────────┘
```

Clean, simple, ready to use.

---

## Troubleshooting

**Embed shows blank or error:**
- Make sure the Vercel URL is correct
- Wait a few seconds (sometimes takes time to load)
- Try refreshing the Notion page
- Check the URL in your browser directly first

**"This embed can't be previewed":**
- Some Notion workspaces restrict embeds
- Ask your Notion admin to allow embeds from vercel.app
- Or share the Vercel URL directly instead

**Form isn't working inside Notion:**
- Try opening the Vercel URL in a new tab (outside Notion)
- Notion embeds sometimes have sandbox restrictions
- Direct link always works as fallback

---

## For Daniel & Third Parties

**Instructions to send them:**

> Hi! We've built a free UTM processor tool. You can use it here:
> 
> **[Notion Page Link or Vercel URL]**
>
> Just:
> 1. Paste your HTML email/landing page
> 2. Enter your base URL + UTM parameters
> 3. Click "Process HTML"
> 4. Download the processed file
>
> No account needed. Questions? Let me know.

---

## Advanced: Make It Look Like Your Brand

**Customize Notion Page:**
- Add a custom icon/cover image
- Match your brand colors in the instructions
- Add company logo

**Customize the App:**
- Edit colors in `templates/index.html` (in the CSS)
- Update the header text and description
- Redeploy to Vercel

---

## Keeping It Updated

If you make changes to the app:

1. Edit `app.py` or `templates/index.html`
2. Push to GitHub (or redeploy via Vercel CLI)
3. Vercel auto-deploys
4. Changes appear immediately in Notion

No need to re-embed or re-share—it updates automatically.

---

## One More Thing: Usage Tips

**For you (internal team):**
- Bookmark the Vercel URL for quick access
- Share the Notion page in your team channels
- Encourage using it for all campaign links

**For Daniel & third parties:**
- They don't need to know about Vercel, Notion, or Flask
- Just see: "Here's a tool to process campaign links"
- Done!

---

**You're all set!** The UTM processor is now publicly accessible and easy to use.
