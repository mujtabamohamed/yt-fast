// YouTube Fast — Popup Script

(function () {
  'use strict';

  const SPEEDS = [0.25, 0.5, 0.75, 0.9, 0.95, 1, 1.05, 1.1, 1.25, 1.5, 1.75, 2, 3, 4, 5];

  const grid = document.getElementById('speed-grid');
  const currentSpeedEl = document.getElementById('current-speed');
  const statusText = document.getElementById('status-text');

  /**
   * Formats a speed number for display.
   * @param {number} speed
   * @returns {string}
   */
  function formatSpeed(speed) {
    if (Number.isInteger(speed)) return speed + '×';
    return parseFloat(speed.toFixed(2)) + '×';
  }

  /**
   * Categorize a speed for color-coding.
   * @param {number} speed
   * @returns {string}
   */
  function getCategory(speed) {
    if (speed < 1) return 'slow';
    if (speed === 1) return 'normal';
    return 'fast';
  }

  /**
   * Updates the UI to reflect the active speed.
   * @param {number} activeSpeed
   */
  function setActiveButton(activeSpeed) {
    currentSpeedEl.textContent = formatSpeed(activeSpeed);

    // Trigger bump animation
    currentSpeedEl.classList.remove('bump');
    void currentSpeedEl.offsetWidth;
    currentSpeedEl.classList.add('bump');

    const buttons = grid.querySelectorAll('.speed-btn');
    buttons.forEach((btn) => {
      const btnSpeed = parseFloat(btn.dataset.speed);
      btn.classList.toggle('active', btnSpeed === activeSpeed);
    });
  }

  /**
   * Sends a message to the content script in the active YouTube tab.
   * @param {object} message
   * @returns {Promise<object|null>}
   */
  async function sendToContent(message) {
    try {
      const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
      const tab = tabs[0];
      if (!tab || !tab.url || !tab.url.includes('youtube.com')) {
        return null;
      }
      const response = await chrome.tabs.sendMessage(tab.id, message);
      return response;
    } catch (err) {
      console.warn('YouTube Fast: Could not reach content script.', err);
      return null;
    }
  }

  /**
   * Creates a ripple effect inside a button.
   * @param {MouseEvent} e
   * @param {HTMLElement} btn
   */
  function createRipple(e, btn) {
    const rect = btn.getBoundingClientRect();
    const ripple = document.createElement('span');
    ripple.classList.add('ripple');
    ripple.style.left = (e.clientX - rect.left) + 'px';
    ripple.style.top = (e.clientY - rect.top) + 'px';
    btn.appendChild(ripple);
    ripple.addEventListener('animationend', () => ripple.remove());
  }

  // ── Build the speed buttons ────────────────────────────────────────────

  SPEEDS.forEach((speed) => {
    const btn = document.createElement('button');
    btn.classList.add('speed-btn');
    btn.dataset.speed = speed;
    btn.dataset.category = getCategory(speed);
    btn.textContent = formatSpeed(speed);
    btn.setAttribute('aria-label', `Set playback speed to ${speed}x`);

    if (speed === 1) {
      btn.classList.add('normal');
    }

    btn.addEventListener('click', async (e) => {
      createRipple(e, btn);
      setActiveButton(speed);

      const result = await sendToContent({ type: 'SET_SPEED', speed });
      if (!result || !result.success) {
        await chrome.storage.local.set({ ytfast_speed: speed });
      }
    });

    grid.appendChild(btn);
  });

  // ── Initialize ─────────────────────────────────────────────────────────

  document.addEventListener('DOMContentLoaded', async () => {
    const result = await sendToContent({ type: 'GET_SPEED' });

    if (result && result.speed != null) {
      statusText.textContent = 'Connected to video';
      statusText.classList.add('connected');
      setActiveButton(result.speed);
    } else {
      try {
        const stored = await chrome.storage.local.get('ytfast_speed');
        const savedSpeed = stored?.ytfast_speed ?? 1;
        setActiveButton(savedSpeed);
      } catch {
        setActiveButton(1);
      }
      statusText.textContent = 'No video detected';
      statusText.classList.add('error');
    }
  });
})();