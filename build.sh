#!/bin/bash
# ─────────────────────────────────────────────────────
# build.sh — Package YT Speed Controller for Chrome & Firefox
#
# Usage:
#   chmod +x build.sh
#   ./build.sh
#
# Outputs:
#   dist/yt-speed-chrome.zip
#   dist/yt-speed-firefox.zip
# ─────────────────────────────────────────────────────

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
DIST="$ROOT/dist"

# Clean previous builds
rm -rf "$DIST"
mkdir -p "$DIST/chrome" "$DIST/firefox"

# Shared files
SHARED_FILES=(
  "popup/popup.html"
  "popup/popup.css"
  "popup/popup.js"
  "content/content.js"
)

# ── Chrome Build ──────────────────────────────────────

echo "📦 Building Chrome extension…"

cp "$ROOT/manifest.json" "$DIST/chrome/manifest.json"
cp "$ROOT/background/service-worker.js" "$DIST/chrome/"
mkdir -p "$DIST/chrome/background"
cp "$ROOT/background/service-worker.js" "$DIST/chrome/background/service-worker.js"

for f in "${SHARED_FILES[@]}"; do
  mkdir -p "$DIST/chrome/$(dirname "$f")"
  cp "$ROOT/$f" "$DIST/chrome/$f"
done

# Copy icons if they exist
if [ -d "$ROOT/icons" ]; then
  cp -r "$ROOT/icons" "$DIST/chrome/icons"
fi

cd "$DIST/chrome"
zip -r "$DIST/yt-speed-chrome.zip" . -x ".*"
echo "  ✅ dist/yt-speed-chrome.zip"

# ── Firefox Build ─────────────────────────────────────

echo "📦 Building Firefox extension…"

cp "$ROOT/manifest-firefox.json" "$DIST/firefox/manifest.json"
mkdir -p "$DIST/firefox/background"
cp "$ROOT/background/background-firefox.js" "$DIST/firefox/background/background-firefox.js"

for f in "${SHARED_FILES[@]}"; do
  mkdir -p "$DIST/firefox/$(dirname "$f")"
  cp "$ROOT/$f" "$DIST/firefox/$f"
done

# Copy icons if they exist
if [ -d "$ROOT/icons" ]; then
  cp -r "$ROOT/icons" "$DIST/firefox/icons"
fi

cd "$DIST/firefox"
zip -r "$DIST/yt-speed-firefox.zip" . -x ".*"
echo "  ✅ dist/yt-speed-firefox.zip"

echo ""
echo "🎉 Done! Both packages are in dist/"
