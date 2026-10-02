# YouTube Fast ⏩

A minimal browser extension to control YouTube video playback speed. Choose from 15 speed presets from 0.25× slow-motion to 5× fast-forward.

![YouTube Fast popup](icons/icon-128.png)

## Features

- **15 speed presets** — 0.25×, 0.5×, 0.75×, 0.9×, 0.95×, 1×, 1.05×, 1.1×, 1.25×, 1.5×, 1.75×, 2×, 3×, 4× and 5×
- **Speed persists** across videos and YouTube SPA navigations
- **Works on Chrome and Firefox**
- **Minimal UI** — clean dark interface, zero clutter

## Installation

### Chrome / Chromium-based browsers (Edge, Brave, Arc, etc.)

1. Download or clone this repo
2. Open `chrome://extensions` in your browser
3. Enable **Developer mode** (toggle in the top-right)
4. Click **Load unpacked**
5. Select the `yt-fast` project folder (the one containing `manifest.json`)
6. The extension icon appears in your toolbar — click it on any YouTube video

### Firefox

Firefox requires a separate manifest. Use the build script to generate it:

1. Download or clone this repo

2. Run the build script:
   ```bash
   chmod +x build.sh
   ./build.sh
   ```

3. This creates `dist/firefox/` with the correct Firefox manifest

#### Permanent install (unsigned)

4. Open `about:config`
5. Set `xpinstall.signatures.required` to `false`
6. Open `about:addons` → ⚙️ gear icon → **Install Add-on From File…**
7. Select `dist/yt-speed-firefox.zip` (rename to `.xpi` first if needed)

> **Note:** Disabling signature enforcement only works on Firefox Developer Edition, Firefox Nightly and Firefox ESR. Regular Firefox does not allow it.

#### Permanent install (signed via Mozilla)

4. Create a free account at [addons.mozilla.org](https://addons.mozilla.org)
5. Go to [API Keys](https://addons.mozilla.org/developers/addon/api/key/) and generate credentials
6. Sign the extension:
   ```bash
   npx -y web-ext sign \
     --source-dir dist/firefox \
     --artifacts-dir dist/signed \
     --api-key="YOUR_JWT_ISSUER" \
     --api-secret="YOUR_JWT_SECRET" \
     --channel=unlisted
   ```
7. Install the signed `.xpi` from `dist/signed/` via `about:addons`

## Project Structure

```
yt-fast/
├── manifest.json            # Chrome (Manifest V3)
├── manifest-firefox.json    # Firefox (Manifest V2)
├── background/
│   ├── service-worker.js    # Chrome background
│   └── background-firefox.js# Firefox background
├── content/
│   └── content.js           # Injected into YouTube pages
├── popup/
│   ├── popup.html           # Extension popup UI
│   ├── popup.css            # Styles
│   └── popup.js             # Popup logic
├── icons/
│   ├── icon-16.png
│   ├── icon-48.png
│   └── icon-128.png
├── build.sh                 # Packages Chrome & Firefox zips
├── generate_icons.py        # Regenerate icons (pure Python, no deps)
└── .gitignore
```

## Building

```bash
./build.sh
```

Outputs:
- `dist/yt-speed-chrome.zip` — ready to upload to Chrome Web Store
- `dist/yt-speed-firefox.zip` — ready to sign or side-load on Firefox

## How It Works

- A **content script** is injected into all YouTube pages
- It listens for messages from the popup and sets `video.playbackRate`
- A `MutationObserver` watches for new video elements (YouTube is a SPA) and auto-applies the saved speed
- The selected speed is persisted to `browser.storage.local` so it carries across videos and sessions

## License

MIT
