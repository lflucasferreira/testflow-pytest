(function () {
  const STORAGE_KEY = 'pt-docs-theme'
  const root = document.documentElement

  function getPreferredTheme() {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored === 'light' || stored === 'dark') return stored
    return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'
  }

  function setHighlightTheme() {
    const link = document.getElementById('hljs-theme')
    if (!link) return
    const base =
      link.dataset.base ||
      'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/styles/'
    link.href = `${base}github-dark.min.css`
  }

  function syncMacLogos(theme) {
    document.querySelectorAll('img.logo-macos[data-logo-dark]').forEach((img) => {
      img.src = theme === 'light' ? img.dataset.logoLight : img.dataset.logoDark
    })
  }

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme)
    localStorage.setItem(STORAGE_KEY, theme)
    setHighlightTheme()
    syncMacLogos(theme)

    document.querySelectorAll('.theme-toggle').forEach((btn) => {
      btn.setAttribute('aria-label', theme === 'light' ? 'Switch to dark theme' : 'Switch to light theme')
      btn.setAttribute('title', theme === 'light' ? 'Dark theme' : 'Light theme')
    })
  }

  function initToggleButtons(onToggle) {
    document.querySelectorAll('.theme-toggle').forEach((btn) => {
      if (btn.dataset.themeBound) return
      btn.dataset.themeBound = 'true'
      btn.addEventListener('click', onToggle)
    })
  }

  applyTheme(getPreferredTheme())

  function bindToggles() {
    initToggleButtons(() => {
      const next = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light'
      applyTheme(next)
      if (window.hljs && typeof window.hljs.highlightAll === 'function') {
        window.hljs.highlightAll()
      }
    })
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bindToggles)
  } else {
    bindToggles()
  }

  window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', (event) => {
    if (!localStorage.getItem(STORAGE_KEY)) {
      applyTheme(event.matches ? 'light' : 'dark')
    }
  })
})()
