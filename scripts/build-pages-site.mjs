import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const siteDir = path.join(root, 'site')
const allureReport = path.join(root, 'allure-report')
const fallbackReport = path.join(root, 'docs', 'report')

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

fs.rmSync(siteDir, { recursive: true, force: true })
fs.mkdirSync(siteDir, { recursive: true })

fs.copyFileSync(path.join(root, 'docs', 'index.html'), path.join(siteDir, 'index.html'))
copyDir(path.join(root, 'docs', 'slides'), path.join(siteDir, 'slides'))

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
