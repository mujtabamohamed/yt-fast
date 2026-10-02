# YouTube Fast ⏩

A minimal Chrome extension to control YouTube video playback speed. Choose from 15 speed presets from 0.25× slow-motion to 5× fast-forward.

![YouTube Fast popup](icons/icon-128.png)

## Features

- **16 speed presets** — 0.25×, 0.5×, 0.75×, 1×, 1.25×, 1.5×, 1.75×, 2×, 2.25×, 2.5×, 2.75×, 3×, 3.5×, 4×, 4.5× and 5×
- **Speed persists** across videos and YouTube SPA navigations
- **Minimal UI** — clean dark interface, zero clutter

## Installation

### Chrome / Chromium-based browsers (Edge, Brave, Arc, etc.)

1. Download or clone this repo
2. Open `chrome://extensions` in your browser
3. Enable **Developer mode** (toggle in the top-right)
4. Click **Load unpacked**
5. Select the `yt-fast` project folder (the one containing `manifest.json`)
6. The extension icon appears in your toolbar — click it on any YouTube video

## Project Structure

```
yt-fast/
├── manifest.json         # Chrome Manifest V3
├── content/
│   └── content.js        # Injected into YouTube pages
├── popup/
│   ├── popup.html        # Extension popup UI
│   ├── popup.css         # Styles
│   └── popup.js          # Popup logic
├── icons/
│   ├── icon-16.png
│   ├── icon-48.png
│   └── icon-128.png
├── .gitignore
├── LICENSE
└── README.md
```

## How It Works

- A **content script** is injected into all YouTube pages
- It listens for messages from the popup and sets `video.playbackRate`
- A `MutationObserver` watches for new video elements (YouTube is a SPA) and auto-applies the saved speed
- The selected speed is persisted to `chrome.storage.local` so it carries across videos and sessions

## License

MIT