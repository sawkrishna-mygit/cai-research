# Running CAI Research Portfolio Locally

The CAI platform has two interfaces that run side by side:

1. **Research Portfolio** — static website showcasing findings, figures, and an interactive calculator
2. **Analysis Playground** — Streamlit app for full analysis and optimization

## Prerequisites

- Python 3.9+
- pip

## One-time setup

```bash
cd cai_platform
python3 -m pip install -r requirements.txt
python3 export_web_data.py
python3 generate_figures.py
```

The export and figure scripts regenerate `data/results_comprehensive.csv`, `web/assets/data/systems.json`, and the four publication figures.

## Option A: Run both with start script

```bash
cd cai_platform
chmod +x start.sh
./start.sh
```

Then open:
- Portfolio: http://localhost:8080
- Playground: http://localhost:8501

Press `Ctrl+C` to stop both servers.

## Option B: Run separately (two terminals)

**Terminal 1 — Portfolio site**

```bash
cd cai_platform/web
python3 -m http.server 8080
```

Open http://localhost:8080

**Terminal 2 — Streamlit Playground**

```bash
cd cai_platform
python3 -m streamlit run app_streamlit.py --server.port 8501
```

Open http://localhost:8501

## Production URLs

After deployment (see [DEPLOY.md](../DEPLOY.md) at project root):

- Portfolio: https://sawkrishna-mygit.github.io/cai-research/
- Playground: https://cai-research-playground.streamlit.app
- GitHub: https://github.com/sawkrishna-mygit/cai-research

## Customizing the portfolio

Edit these placeholders in `web/index.html` under the About section:

- Researcher name
- Institution
- Email, LinkedIn, ORCID links
- Bio text

## Project structure

```
cai_platform/
├── data/                          # Certification & occupant data
├── web/                           # Portfolio website
│   ├── index.html
│   ├── css/styles.css
│   ├── js/cai-calculator.js
│   └── assets/
│       ├── data/systems.json
│       └── figures/fig1–fig4.png
├── app_streamlit.py               # Analysis Playground
├── cai_core.py                    # Core analysis engine
├── export_web_data.py             # Regenerate JSON + results CSV
├── generate_figures.py            # Regenerate publication figures
└── start.sh                       # Launch both servers
```
