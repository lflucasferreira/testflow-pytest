import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const siteDir = path.join(root, 'site')
const docsSrc = path.join(root, 'docs')
const allureReport = path.join(root, 'allure-report')
const fallbackReport = path.join(docsSrc, 'report')

const NO_REPORT_HTML = `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Allure Report</title>
  </head>
  <body>
    <h1>No test report generated</h1>
    <p>Check workflow logs.</p>
  </body>
</html>
`

function copyDir(src, dest) {
  fs.cpSync(src, dest, { recursive: true })
}

function writeLegacyRedirect(destFile, target) {
  fs.mkdirSync(path.dirname(destFile), { recursive: true })
  fs.writeFileSync(
    destFile,
    `<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta http-equiv="refresh" content="0; url=${target}" />
    <link rel="canonical" href="${target}" />
    <title>Redirecting…</title>
    <script>location.replace('${target}')</script>
  </head>
  <body>
    <p>Moved — <a href="${target}">open the guide</a>.</p>
  </body>
</html>
`,
  )
}

function copyPagesVendorAssets() {
  const nodeModules = path.join(root, 'node_modules')
  const revealSrc = path.join(nodeModules, 'reveal.js')
  const hljsSrc = path.join(nodeModules, 'highlight.js')
  const siteModules = path.join(siteDir, 'node_modules')

  if (!fs.existsSync(path.join(revealSrc, 'dist'))) {
    console.warn('Missing reveal.js dist — run npm ci before pages:build (slides may not work on Pages).')
    return
  }
  if (!fs.existsSync(hljsSrc)) {
    console.warn('Missing highlight.js — run npm ci before pages:build.')
    return
  }

  copyDir(path.join(revealSrc, 'dist'), path.join(siteModules, 'reveal.js', 'dist'))
  fs.mkdirSync(path.join(siteModules, 'reveal.js', 'plugin', 'highlight'), { recursive: true })
  fs.copyFileSync(
    path.join(revealSrc, 'plugin', 'highlight', 'highlight.js'),
    path.join(siteModules, 'reveal.js', 'plugin', 'highlight', 'highlight.js'),
  )

  const hlStyles = path.join(siteModules, 'highlight.js', 'styles')
  fs.mkdirSync(hlStyles, { recursive: true })
  for (const style of ['github.css', 'github-dark.css']) {
    fs.copyFileSync(path.join(hljsSrc, 'styles', style), path.join(hlStyles, style))
  }

  console.log('Copied reveal.js + highlight.js assets to site/node_modules/')
}

function patchSlidesForPages(slidesDir) {
  const slidesIndex = path.join(slidesDir, 'index.html')
  if (!fs.existsSync(slidesIndex)) return

  const html = fs
    .readFileSync(slidesIndex, 'utf8')
    .replaceAll('../../node_modules/', '../node_modules/')
  fs.writeFileSync(slidesIndex, html)
  console.log('Patched slides/index.html node_modules paths for GitHub Pages')
}

fs.rmSync(siteDir, { recursive: true, force: true })
fs.mkdirSync(siteDir, { recursive: true })

fs.copyFileSync(path.join(docsSrc, 'index.html'), path.join(siteDir, 'index.html'))
copyDir(path.join(docsSrc, 'slides'), path.join(siteDir, 'slides'))
copyDir(path.join(docsSrc, 'js'), path.join(siteDir, 'js'))
patchSlidesForPages(path.join(siteDir, 'slides'))
copyPagesVendorAssets()

for (const guide of ['guia-completo.html', 'complete-guide.html']) {
  const src = path.join(docsSrc, guide)
  if (fs.existsSync(src)) {
    fs.copyFileSync(src, path.join(siteDir, guide))
  }
}

writeLegacyRedirect(path.join(siteDir, 'slides', 'guia-completo.html'), '../guia-completo.html')

const reportDest = path.join(siteDir, 'report')
if (fs.existsSync(path.join(allureReport, 'index.html'))) {
  copyDir(allureReport, reportDest)
  console.log('Using allure-report/ for site/report/')
} else if (fs.existsSync(path.join(fallbackReport, 'index.html'))) {
  copyDir(fallbackReport, reportDest)
  console.log('Using docs/report/ fallback for site/report/')
} else {
  fs.mkdirSync(reportDest, { recursive: true })
  fs.writeFileSync(path.join(reportDest, 'index.html'), NO_REPORT_HTML)
  console.log('No report found — wrote placeholder at site/report/')
}

fs.writeFileSync(path.join(siteDir, '.nojekyll'), '')
console.log(`GitHub Pages site ready at ${path.relative(root, siteDir)}/`)
