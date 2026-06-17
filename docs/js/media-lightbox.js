(function () {
  const EXPANDABLE_IMG_SELECTOR = [
    'img.card-logo',
    'img.card-icon',
    '.logo-wrap img',
    '.hero-logo img',
    'header.brand img',
    '.hero-logo-wrap img',
  ].join(', ')

  const overlay = document.createElement('div')
  overlay.className = 'media-lightbox'
  overlay.hidden = true
  overlay.setAttribute('role', 'dialog')
  overlay.setAttribute('aria-modal', 'true')
  overlay.setAttribute('aria-label', 'Expanded view')
  overlay.innerHTML =
    '<button type="button" class="media-lightbox__close" aria-label="Close">✕</button>' +
    '<div class="media-lightbox__content"></div>'
  document.body.appendChild(overlay)

  const content = overlay.querySelector('.media-lightbox__content')
  const closeBtn = overlay.querySelector('.media-lightbox__close')

  function markExpandable() {
    document.querySelectorAll('main pre, .reveal pre, article pre').forEach((pre) => {
      if (pre.closest('.media-lightbox')) return
      pre.classList.add('is-expandable')
      pre.setAttribute('title', 'Click to expand')
    })

    document
      .querySelectorAll(`${EXPANDABLE_IMG_SELECTOR}, h2.icon-heading img, h3.icon-heading img`)
      .forEach((img) => {
        img.classList.add('is-expandable')
        img.setAttribute('title', 'Click to enlarge')
      })
  }

  function openLightbox(node) {
    content.innerHTML = ''
    const clone = node.cloneNode(true)
    clone.removeAttribute('title')
    clone.classList.remove('is-expandable')
    content.appendChild(clone)
    overlay.hidden = false
    document.body.classList.add('media-lightbox-open')
    closeBtn.focus()
  }

  function closeLightbox() {
    overlay.hidden = true
    content.innerHTML = ''
    document.body.classList.remove('media-lightbox-open')
  }

  function isExpandableImage(img) {
    if (!(img instanceof HTMLImageElement)) return false
    if (img.closest('.tool-chip, .tool-inline, .tool-list, .platform-tools, .install-step-tools')) {
      return false
    }
    if (img.matches(EXPANDABLE_IMG_SELECTOR)) return true
    if (img.closest('h2.icon-heading, h3.icon-heading')) return true
    return false
  }

  document.addEventListener('click', (event) => {
    if (!overlay.hidden) {
      if (event.target === overlay || event.target.closest('.media-lightbox__close')) {
        closeLightbox()
      }
      return
    }

    const pre = event.target.closest('pre')
    if (pre && pre.classList.contains('is-expandable')) {
      event.preventDefault()
      openLightbox(pre)
      return
    }

    const img = event.target.closest('img')
    if (img && isExpandableImage(img)) {
      event.preventDefault()
      openLightbox(img)
    }
  })

  closeBtn.addEventListener('click', closeLightbox)

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && !overlay.hidden) {
      closeLightbox()
    }
  })

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', markExpandable)
  } else {
    markExpandable()
  }
})()
