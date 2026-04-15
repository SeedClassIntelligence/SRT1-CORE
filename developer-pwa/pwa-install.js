/**
 * SRT-1 Universal PWA Install Banner
 * Auto-detects mobile visitors and shows a context-appropriate install prompt.
 * Consumer pages → "Install Seed Reflection"
 * Developer / root pages → "Install SRT-1 Developer Tools"
 */
(function () {
  'use strict';

  // ── Config ────────────────────────────────────────────────────────────────
  const DISMISS_KEY = 'pwa-banner-dismissed';
  const DISMISS_TTL = 7 * 24 * 60 * 60 * 1000; // 7 days

  const CONSUMER_PATHS = ['/seed-reflection'];
  const CONSUMER_CONFIG = {
    name: 'Seed Reflection',
    tagline: 'Capture ideas in one tap — works offline',
    iconSvg: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" width="40" height="40"><rect width="40" height="40" rx="9" fill="#06080f"/><circle cx="20" cy="20" r="11" fill="none" stroke="#10a37f" stroke-width="2.5"/><circle cx="20" cy="20" r="7" fill="none" stroke="#10a37f" stroke-width="2" opacity=".7"/><circle cx="20" cy="20" r="3.5" fill="#10a37f"/></svg>',
    accentColor: '#10a37f',
    manifest: '/manifest.json',
    fallbackUrl: '/seed-reflection/mobile.html',
  };

  const DEVELOPER_CONFIG = {
    name: 'SRT-1 Developer Tools',
    tagline: 'AI codebase intelligence — always available',
    iconSvg: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" width="40" height="40"><rect width="40" height="40" rx="9" fill="#06080f"/><polyline points="12,15 6,20 12,25" fill="none" stroke="#58a6ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><polyline points="28,15 34,20 28,25" fill="none" stroke="#58a6ff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><line x1="22" y1="11" x2="18" y2="29" stroke="#58a6ff" stroke-width="2" stroke-linecap="round"/></svg>',
    accentColor: '#58a6ff',
    manifest: '/manifest.json',
    fallbackUrl: '/srt1_mobile.html',
  };

  // ── Detect context ────────────────────────────────────────────────────────
  function getConfig() {
    const path = location.pathname;
    return CONSUMER_PATHS.some(p => path.startsWith(p)) ? CONSUMER_CONFIG : DEVELOPER_CONFIG;
  }

  // ── Guards ────────────────────────────────────────────────────────────────
  function isMobile() {
    return /Mobile|Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  }

  function isStandalone() {
    return window.matchMedia('(display-mode: standalone)').matches ||
      window.navigator.standalone === true;
  }

  function wasDismissedRecently() {
    try {
      const stored = localStorage.getItem(DISMISS_KEY);
      if (!stored) return false;
      const { ts, path } = JSON.parse(stored);
      // Per-config: consumer dismissal doesn't hide developer banner
      const cfg = getConfig();
      if (path !== cfg.name) return false;
      return Date.now() - ts < DISMISS_TTL;
    } catch { return false; }
  }

  function markDismissed() {
    try {
      localStorage.setItem(DISMISS_KEY, JSON.stringify({ ts: Date.now(), path: getConfig().name }));
    } catch {}
  }

  // ── Styles ────────────────────────────────────────────────────────────────
  function injectStyles(accentColor) {
    const id = 'pwa-banner-styles';
    if (document.getElementById(id)) return;
    const style = document.createElement('style');
    style.id = id;
    style.textContent = `
      #pwa-install-banner {
        display: none;
        position: fixed;
        bottom: max(16px, env(safe-area-inset-bottom, 16px));
        left: 12px;
        right: 12px;
        background: #0d1117;
        border: 1px solid ${accentColor};
        border-radius: 14px;
        padding: 14px 16px;
        z-index: 9999;
        box-shadow: 0 8px 40px rgba(0,0,0,0.6);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        animation: pwa-slide-up 0.3s cubic-bezier(0.34,1.56,0.64,1);
      }
      @keyframes pwa-slide-up {
        from { transform: translateY(20px); opacity: 0; }
        to   { transform: translateY(0);   opacity: 1; }
      }
      #pwa-install-banner .pwa-row {
        display: flex;
        align-items: center;
        gap: 12px;
      }
      #pwa-install-banner .pwa-icon {
        flex-shrink: 0;
        border-radius: 9px;
        overflow: hidden;
        width: 40px;
        height: 40px;
      }
      #pwa-install-banner .pwa-copy {
        flex: 1;
        min-width: 0;
      }
      #pwa-install-banner .pwa-copy strong {
        display: block;
        font-size: 14px;
        font-weight: 700;
        color: #e6edf3;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      #pwa-install-banner .pwa-copy span {
        display: block;
        font-size: 12px;
        color: #8b949e;
        margin-top: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      #pwa-install-banner .pwa-actions {
        display: flex;
        gap: 8px;
        margin-top: 12px;
      }
      #pwa-install-banner .pwa-btn-install {
        flex: 1;
        padding: 10px;
        border-radius: 8px;
        border: none;
        background: ${accentColor};
        color: #fff;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        font-family: inherit;
        transition: opacity 0.15s;
        -webkit-tap-highlight-color: transparent;
      }
      #pwa-install-banner .pwa-btn-install:active { opacity: 0.8; }
      #pwa-install-banner .pwa-btn-dismiss {
        padding: 10px 14px;
        border-radius: 8px;
        border: 1px solid #21262d;
        background: none;
        color: #8b949e;
        font-size: 14px;
        cursor: pointer;
        font-family: inherit;
        -webkit-tap-highlight-color: transparent;
      }
      #pwa-install-banner .pwa-ios-hint {
        font-size: 12px;
        color: #8b949e;
        text-align: center;
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px solid #21262d;
      }
      #pwa-install-banner .pwa-ios-hint svg {
        vertical-align: middle;
        margin: 0 2px;
      }
    `;
    document.head.appendChild(style);
  }

  // ── Build banner DOM ─────────────────────────────────────────────────────
  function buildBanner(cfg, installPrompt) {
    injectStyles(cfg.accentColor);

    const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent) && !window.MSStream;
    const canNativeInstall = !!installPrompt;

    const banner = document.createElement('div');
    banner.id = 'pwa-install-banner';
    banner.setAttribute('role', 'dialog');
    banner.setAttribute('aria-label', 'Install ' + cfg.name);

    banner.innerHTML = `
      <div class="pwa-row">
        <div class="pwa-icon">${cfg.iconSvg}</div>
        <div class="pwa-copy">
          <strong>${cfg.name}</strong>
          <span>${cfg.tagline}</span>
        </div>
      </div>
      <div class="pwa-actions">
        ${canNativeInstall ? `<button class="pwa-btn-install" id="pwa-install-btn">Add to Home Screen</button>` : `<a class="pwa-btn-install" href="${cfg.fallbackUrl}" style="text-decoration:none;text-align:center">Open App</a>`}
        <button class="pwa-btn-dismiss" id="pwa-dismiss-btn">Not now</button>
      </div>
      ${isIOS && !canNativeInstall ? `
        <div class="pwa-ios-hint">
          On iPhone: tap
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#8b949e" stroke-width="2" stroke-linecap="round"><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/><polyline points="16 6 12 2 8 6"/><line x1="12" y1="2" x2="12" y2="15"/></svg>
          then <strong style="color:#e6edf3">Add to Home Screen</strong>
        </div>` : ''}
    `;

    document.body.appendChild(banner);

    // Install button
    const installBtn = document.getElementById('pwa-install-btn');
    if (installBtn && installPrompt) {
      installBtn.addEventListener('click', () => {
        installPrompt.prompt();
        installPrompt.userChoice.then(r => {
          hideBanner();
          if (r.outcome === 'accepted') markDismissed();
        });
      });
    }

    // Dismiss button
    document.getElementById('pwa-dismiss-btn').addEventListener('click', () => {
      hideBanner();
      markDismissed();
    });

    return banner;
  }

  function showBanner(banner) {
    banner.style.display = 'block';
  }

  function hideBanner() {
    const b = document.getElementById('pwa-install-banner');
    if (b) {
      b.style.animation = 'none';
      b.style.transition = 'opacity 0.2s, transform 0.2s';
      b.style.opacity = '0';
      b.style.transform = 'translateY(10px)';
      setTimeout(() => b.remove(), 200);
    }
  }

  // ── Main ─────────────────────────────────────────────────────────────────
  function init() {
    // Skip for desktop, standalone mode, or recently dismissed
    if (!isMobile()) return;
    if (isStandalone()) return;
    if (wasDismissedRecently()) return;

    const cfg = getConfig();
    let deferredPrompt = null;
    let banner = null;

    // Capture native install prompt (Chrome/Android/desktop)
    window.addEventListener('beforeinstallprompt', e => {
      e.preventDefault();
      deferredPrompt = e;
      if (!banner) {
        banner = buildBanner(cfg, deferredPrompt);
        setTimeout(() => showBanner(banner), 1500);
      }
    });

    // iOS Safari: no beforeinstallprompt, show informational banner instead
    const isIOS = /iPhone|iPad|iPod/i.test(navigator.userAgent);
    const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
    if (isIOS && isSafari) {
      setTimeout(() => {
        if (!banner) {
          banner = buildBanner(cfg, null);
          showBanner(banner);
        }
      }, 2000);
    }

    // App installed event
    window.addEventListener('appinstalled', () => {
      hideBanner();
      markDismissed();
    });
  }

  // Run after DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
