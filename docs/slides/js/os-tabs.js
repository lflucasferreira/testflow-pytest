document.querySelectorAll('.os-tabs').forEach((tabs) => {
  const buttons = tabs.querySelectorAll('.os-tab')
  const panels = tabs.querySelectorAll('.os-panel')

  buttons.forEach((button) => {
    button.addEventListener('click', () => {
      const os = button.dataset.os
      buttons.forEach((b) => b.classList.toggle('active', b === button))
      panels.forEach((p) => p.classList.toggle('active', p.dataset.os === os))
    })
  })
})
