// YouTube Fast — Content Script

(function () {
  'use strict';

  const SPEEDS = [0.25, 0.5, 0.75, 0.9, 0.95, 1, 1.05, 1.1, 1.25, 1.5, 1.75, 2, 3, 4, 5];
  const STORAGE_KEY = 'ytfast_speed';

  /**
   * Finds the active YouTube video element.
   * @returns {HTMLVideoElement|null}
   */
  function getVideo() {
    return document.querySelector('video.html5-main-video') || document.querySelector('video');
  }

  /**
   * Applies a playback rate to the current video and persists it.
   * @param {number} rate
   */
  async function applySpeed(rate) {
    const video = getVideo();
    if (video) {
      video.playbackRate = rate;
    }
    try {
      await chrome.storage.local.set({ [STORAGE_KEY]: rate });
    } catch {
      // Storage may not be available in some edge cases
    }
  }

  /**
   * Reads the persisted speed and applies it to the video.
   */
  async function restoreSpeed() {
    try {
      const result = await chrome.storage.local.get(STORAGE_KEY);
      const saved = result?.[STORAGE_KEY];
      if (saved != null && SPEEDS.includes(saved)) {
        const video = getVideo();
        if (video) {
          video.playbackRate = saved;
        }
      }
    } catch {
      // Ignore
    }
  }

  // ── Listen for messages from the popup ──────────────────────────────────

  chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    if (message.type === 'GET_SPEED') {
      const video = getVideo();
      sendResponse({ speed: video ? video.playbackRate : 1 });
      return true;
    }

    if (message.type === 'SET_SPEED') {
      const rate = Number(message.speed);
      if (!isNaN(rate) && rate > 0) {
        applySpeed(rate);
        sendResponse({ success: true, speed: rate });
      } else {
        sendResponse({ success: false, error: 'Invalid speed' });
      }
      return true;
    }

    return false;
  });

  // ── Auto-apply saved speed when a new video element appears ─────────────

  function onVideoReady() {
    restoreSpeed();
  }

  // YouTube is an SPA — watch for the video element appearing / changing
  const observer = new MutationObserver(() => {
    const video = getVideo();
    if (video && !video.dataset.ytfastBound) {
      video.dataset.ytfastBound = 'true';
      video.addEventListener('loadedmetadata', onVideoReady);
      restoreSpeed();
    }
  });

  observer.observe(document.documentElement, { childList: true, subtree: true });

  // Initial run
  const initVideo = getVideo();
  if (initVideo) {
    initVideo.dataset.ytfastBound = 'true';
    initVideo.addEventListener('loadedmetadata', onVideoReady);
    restoreSpeed();
  }
})();
