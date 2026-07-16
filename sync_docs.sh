#!/usr/bin/env bash
# Sync portfolio site from cai_platform/web to docs/ for GitHub Pages branch deploy.
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
rm -rf docs
cp -R cai_platform/web docs
echo "Synced cai_platform/web → docs/ ($(find docs -type f | wc -l | tr -d ' ') files)"
