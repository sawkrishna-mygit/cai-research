# CAI Research — Online Deployment Guide

Deploy Vaibhavi's CAI research portfolio and Streamlit playground using the **sawkrishna-mygit** GitHub account (personal account only — not enterprise GitHub).

## Live URLs (after deployment)

| Service | URL |
|---------|-----|
| Research Portfolio | https://sawkrishna-mygit.github.io/cai-research/ |
| Analysis Playground | https://cai-research-playground.streamlit.app |
| Source Code | https://github.com/sawkrishna-mygit/cai-research |

---

## Step 1 — One-time code prep (already in repo)

The repo includes:

- `cai_platform/web/` — static portfolio site
- `.github/workflows/deploy-pages.yml` — auto-deploys portfolio on push to `main`
- `cai_platform/requirements-deploy.txt` — Streamlit Cloud dependencies
- `cai_platform/web/js/config.js` — production/local URL switching

Regenerate data assets if needed:

```bash
cd cai_platform
python3 export_web_data.py
python3 generate_figures.py
```

---

## Step 2 — Push to GitHub (sawkrishna-mygit)

```bash
cd "/Users/krishnasaw/Downloads/Vaibhavi project"
git init
git add .
git commit -m "Add CAI research portfolio and analysis platform"
```

Create the public repo (if it does not exist):

```bash
gh auth login   # sign in as sawkrishna-mygit
gh repo create sawkrishna-mygit/cai-research --public --source=. --remote=origin --push
```

Or manually:

1. Go to https://github.com/new while logged in as **sawkrishna-mygit**
2. Repository name: `cai-research`
3. Visibility: **Public**
4. Do not add README (already in project)

```bash
git remote add origin https://github.com/sawkrishna-mygit/cai-research.git
git branch -M main
git push -u origin main
```

**Or use the helper script** (after creating the repo on GitHub):

```bash
./push_to_github.sh
```

If prompted for credentials, use a GitHub Personal Access Token (not password).
Create one at: https://github.com/settings/tokens (scope: `repo`)

---

## Step 3 — Enable GitHub Pages

1. Open https://github.com/sawkrishna-mygit/cai-research/settings/pages
2. Under **Build and deployment** → Source: select **GitHub Actions**
3. Push to `main` triggers the workflow automatically
4. Wait 2–3 minutes; site goes live at https://sawkrishna-mygit.github.io/cai-research/

Verify workflow: https://github.com/sawkrishna-mygit/cai-research/actions

---

## Step 4 — Deploy Streamlit Playground

1. Go to https://share.streamlit.io
2. Sign in with the **sawkrishna-mygit** GitHub account
3. Click **Create app** → **From existing repo**
4. Configure:

| Setting | Value |
|---------|-------|
| Repository | `sawkrishna-mygit/cai-research` |
| Branch | `main` |
| Main file path | `cai_platform/app_streamlit.py` |
| App URL (optional) | `cai-research-playground` |

5. Click **Advanced settings**:
   - Python version: 3.11
   - Requirements file: `cai_platform/requirements-deploy.txt`

6. Under **Secrets**, add:

| Key | Value |
|-----|-------|
| `CAI_PORTFOLIO_URL` | `https://sawkrishna-mygit.github.io/cai-research/` |

7. Click **Deploy**

See [STREAMLIT_CLOUD_SETUP.md](STREAMLIT_CLOUD_SETUP.md) for a printable checklist.

First deploy takes 3–5 minutes. App URL: `https://cai-research-playground.streamlit.app`

**Note:** Free Streamlit apps sleep after inactivity. First visit after sleep may take ~30 seconds to load.

---

## Step 5 — Verify cross-links

- [ ] Portfolio → Playground button opens Streamlit app
- [ ] Streamlit → "Back to Research Portfolio" opens GitHub Pages site
- [ ] Interactive calculator loads all 13 certification presets
- [ ] All 4 figures display on portfolio site
- [ ] "View on GitHub" footer link works

---

## Step 6 — Add to Vaibhavi's main portfolio

See [PORTFOLIO_INTEGRATION.md](PORTFOLIO_INTEGRATION.md) for copy-paste project card text and LinkedIn bullet.

---

## Custom domain (later)

When you buy a domain (e.g. `vaibhavi.com`):

1. GitHub repo → Settings → Pages → Custom domain → `cai.vaibhavi.com`
2. At your registrar, add CNAME: `cai` → `sawkrishna-mygit.github.io`
3. Update Streamlit secret `CAI_PORTFOLIO_URL` to `https://cai.vaibhavi.com/`
4. Update `cai_platform/web/js/config.js` production `portfolioUrl`

No code rewrite required.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| GitHub Pages 404 | Ensure Pages source is **GitHub Actions**, not a branch |
| Workflow failed | Check Actions tab; confirm `cai_platform/web/index.html` exists |
| Streamlit import error | Confirm main file is `cai_platform/app_streamlit.py` |
| Playground links go to localhost | You're viewing locally; production site uses `config.js` auto-detect |
| Figures missing on live site | Run `python3 generate_figures.py` and push again |

---

## Updating the live site

Any push to `main` automatically redeploys the portfolio. Streamlit redeploys on push as well (if auto-redeploy is enabled in Streamlit Cloud settings).

```bash
git add .
git commit -m "Update research findings"
git push
```
