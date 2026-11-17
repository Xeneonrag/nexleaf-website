# Nexleaf website

The official website for Nexleaf and its game Dicebound: studio home page, player support, and the legal pages the app stores link to.

Live address (once published): https://xeneonrag.github.io/nexleaf-website/

It is a plain static site (HTML, CSS, a few lines of JavaScript). A small Python script, `build.py`, puts the shared header and footer around each page. There are no paid services, no database and nothing to install besides Python 3.

## Where things are

| What | File |
|---|---|
| Studio name, email, menu, **games list**, store links, announcement | `site.json` |
| Home page text | `src/pages/index.html` |
| Privacy Policy | `src/pages/privacy-policy.html` |
| Terms of Service | `src/pages/terms-of-service.html` |
| Account Deletion | `src/pages/account-deletion.html` |
| Community Guidelines | `src/pages/community-guidelines.html` |
| Virtual Items and Refunds | `src/pages/virtual-items.html` |
| Support | `src/pages/support.html` |
| Header, footer, page frame | `src/template.html` |
| Colours, fonts, layout | `src/assets/css/style.css` (colours are the variables at the top) |
| Images | `src/assets/img/` |
| Publishing to GitHub Pages | `.github/workflows/deploy.yml` |

The address of each page comes from its file name: `src/pages/privacy-policy.html` becomes `/privacy-policy/`. **Do not rename the legal pages** once their addresses are entered in Google Play Console or the game.

## Preview on your computer

```bash
python build.py --drafts
```

```bash
python -m http.server 8080 --directory _site
```

Then open http://localhost:8080/. `--drafts` includes pages that are not approved yet, with a yellow banner.

## Drafts and approval

Each page starts with a settings block. `status: draft` keeps the page **out of the published site**; `status: published` puts it in.

Anything that still needs a decision is wrapped like this and shows highlighted in the preview:

```html
<mark class="review">REVIEW: ...</mark>
```

To approve a page: resolve and delete every review note, update the `updated:` date, and change `status: draft` to `status: published`. The build refuses to publish a page that still has a review note, and refuses to build if any link or image is broken.

## Publish changes

Every push to the `main` branch rebuilds and republishes the site automatically (GitHub Actions, about a minute).

```bash
git add -A
```

```bash
git commit -m "Describe the change"
```

```bash
git push
```

## Common edits

- **Change text:** edit the page in `src/pages/`. For a legal page, also change its `updated:` date.
- **Announcement bar on the home page:** set `"announcement"` in `site.json` (leave it `""` for none).
- **Store links:** set `"google_play_url"` / `"app_store_url"` for the game in `site.json`. The "Coming soon" buttons turn into real links.
- **Screenshots:** put images in `src/assets/img/` and list them in the game's `"screenshots"` in `site.json`, e.g. `["assets/img/dicebound-shot-1.jpg"]`. Portrait images about 720 px wide work best.
- **Add a game:** copy the Dicebound block in `"games"` in `site.json` and change its details.
- **Add a page:** add `src/pages/new-page.html` with a settings block (copy one from another page). Add it to `"nav"` or `"footer_legal"` in `site.json` to link it.
- **Change the look:** edit the colour variables at the top of `src/assets/css/style.css`.

## Editing with Claude

Open this folder in Claude Code and say what you want, for example "add these three screenshots to Dicebound" or "update the Privacy Policy to mention rewarded ads". Ask it to run `python build.py --drafts` and preview before pushing.

## First-time GitHub setup

1. Create a **public** repository named `nexleaf-website` on GitHub (no README or licence, so it starts empty).
2. In this folder: `git remote add origin https://github.com/Xeneonrag/nexleaf-website.git` then `git push -u origin main`.
3. On GitHub: **Settings > Pages > Build and deployment > Source: GitHub Actions**.
4. Check the **Actions** tab for a green run, then open the live address above.

Only this folder is published. The Dicebound Unity project is a separate, private repository and is never uploaded here.
