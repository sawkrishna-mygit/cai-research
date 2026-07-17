# Streamlit Community Cloud — Quick Setup Checklist

Complete these steps at https://share.streamlit.io while logged in as **sawkrishna-mygit**.

## App configuration

| Field | Value |
|-------|-------|
| Repository | `sawkrishna-mygit/cai-research` |
| Branch | `main` |
| Main file path | `streamlit_app.py` |
| App URL (custom subdomain) | `cai-research-playground` |

## Advanced settings

| Field | Value |
|-------|-------|
| Python version | 3.11 |
| Requirements file | `requirements.txt` (auto-detected at repo root) |

## Secrets (required)

Go to App settings → Secrets and paste:

```toml
CAI_PORTFOLIO_URL = "https://sawkrishna-mygit.github.io/cai-research/"
```

(See also `cai_platform/.streamlit/secrets.toml.example`)

## After deploy

- Live URL: https://cai-research-playground.streamlit.app
- Test "Back to Research Portfolio" link points to GitHub Pages
- Test portfolio Playground buttons point to this URL

## If the app fails to start

1. Check logs in Streamlit Cloud dashboard
2. Confirm `cai_platform/data/certification_points.csv` exists in repo
3. Confirm requirements file path is `cai_platform/requirements-deploy.txt`
4. Redeploy from the Streamlit dashboard
