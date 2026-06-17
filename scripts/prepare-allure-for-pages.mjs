import { execSync } from 'node:child_process'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const stagingDir = path.join(root, process.env.ALLURE_PAGES_DIR ?? 'pages-allure-staging')
const allureReport = path.join(root, 'allure-report')
const allureResults = path.join(root, 'allure-results')

function stageReport(sourceDir) {
  fs.rmSync(stagingDir, { recursive: true, force: true })
  fs.cpSync(sourceDir, stagingDir, { recursive: true })
  console.log(`Staged for Pages at ${path.relative(root, stagingDir)}/index.html`)
}

if (fs.existsSync(path.join(allureReport, 'index.html'))) {
  console.log('Using existing allure-report/index.html')
  stageReport(allureReport)
  process.exit(0)
}

if (!fs.existsSync(allureResults)) {
  console.log('No allure-results — skipping report generation')
  process.exit(0)
}

function countFiles(dir) {
  let count = 0
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name)
    if (entry.isDirectory()) count += countFiles(fullPath)
    else if (entry.isFile()) count += 1
  }
  return count
}

const fileCount = countFiles(allureResults)

if (fileCount === 0) {
  console.log('allure-results is empty — skipping report generation')
  process.exit(0)
}

console.log(`Found ${fileCount} file(s) in allure-results — merging and generating report`)
execSync('node scripts/merge-allure-results.mjs', { cwd: root, stdio: 'inherit' })
execSync('npm run report:allure', { cwd: root, stdio: 'inherit' })

if (!fs.existsSync(path.join(allureReport, 'index.html'))) {
  console.log('Allure report generation did not produce index.html — continuing without report')
  process.exit(0)
}

stageReport(allureReport)
console.log(`Allure report ready at ${path.relative(root, allureReport)}/index.html`)
