#!/usr/bin/env bash
# Push CAI research project to sawkrishna-mygit/cai-research on GitHub.
# Run this after creating the public repo at https://github.com/new

set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

REPO_URL="https://github.com/sawkrishna-mygit/cai-research.git"

echo "=== CAI Research — GitHub Push ==="
echo ""
echo "Prerequisites:"
echo "  1. Logged into GitHub as sawkrishna-mygit"
echo "  2. Public repo 'cai-research' created at https://github.com/new"
echo ""

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  git init
  git add .
  git commit -m "Add CAI research portfolio and analysis platform"
fi

git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL"
git branch -M main

echo "Pushing to $REPO_URL ..."
git push -u origin main

echo ""
echo "Done! Next steps:"
echo "  1. Enable GitHub Pages: repo Settings → Pages → Source: GitHub Actions"
echo "  2. Wait 2-3 min, then open: https://sawkrishna-mygit.github.io/cai-research/"
echo "  3. Deploy Streamlit: see DEPLOY.md Step 4"
echo ""
