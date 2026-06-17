import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const resultsDir = path.join(root, process.env.ALLURE_RESULTS_DIR ?? 'allure-results')
const stagingDir = path.join(root, process.env.ALLURE_STAGING_DIR ?? 'allure-results-staging')

function listResultFiles(dir) {
  if (!fs.existsSync(dir)) return []
  return fs
    .readdirSync(dir)
    .filter((name) => name.endsWith('-result.json'))
    .map((name) => path.join(dir, name))
}

function copyDirFiles(sourceDir, targetDir, browserHint) {
  if (!fs.existsSync(sourceDir)) return 0

  fs.mkdirSync(targetDir, { recursive: true })
  let copied = 0

  for (const entry of fs.readdirSync(sourceDir, { withFileTypes: true })) {
    if (!entry.isFile()) continue
    if (entry.name === 'environment.properties' || entry.name === 'executor.json') continue

    const sourcePath = path.join(sourceDir, entry.name)
    const targetPath = path.join(targetDir, entry.name)

    if (entry.name.endsWith('-result.json')) {
      const result = JSON.parse(fs.readFileSync(sourcePath, 'utf8'))
      ensureBrowserLabel(result, browserHint)
      fs.writeFileSync(targetPath, `${JSON.stringify(result)}\n`)
    } else {
      fs.copyFileSync(sourcePath, targetPath)
    }

    copied += 1
  }

  return copied
}

function ensureBrowserLabel(result, browserHint) {
  const labels = Array.isArray(result.labels) ? result.labels : []
  const hasBrowserLabel = labels.some((label) => label.name === 'browser')
  if (hasBrowserLabel) return

  const fromParameter = result.parameters?.find((param) => param.name === 'browser_name')?.value
  const browser = browserHint ?? normalizeValue(fromParameter) ?? 'unknown'

  labels.push({ name: 'browser', value: browser })
  result.labels = labels
}

function normalizeValue(value) {
  if (typeof value !== 'string') return value ?? null
  return value.replace(/^'+|'+$/g, '')
}

function browserFromResult(result) {
  const label = result.labels?.find((entry) => entry.name === 'browser')?.value
  if (label) return label

  const parameter = result.parameters?.find((entry) => entry.name === 'browser_name')?.value
  return normalizeValue(parameter) ?? 'unknown'
}

function browserFromStagingDir(dirName) {
  const match = dirName.match(/^allure-results-(.+)$/)
  return match?.[1] ?? dirName
}

function mergeFromStaging() {
  if (!fs.existsSync(stagingDir)) return false

  const browserDirs = fs
    .readdirSync(stagingDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort()

  if (browserDirs.length === 0) return false

  fs.rmSync(resultsDir, { recursive: true, force: true })
  fs.mkdirSync(resultsDir, { recursive: true })

  let copied = 0
  for (const dirName of browserDirs) {
    const browser = browserFromStagingDir(dirName)
    copied += copyDirFiles(path.join(stagingDir, dirName), resultsDir, browser)
  }

  console.log(`Merged ${copied} file(s) from ${browserDirs.length} browser artifact(s)`)
  return copied > 0
}

function summarizeResults() {
  const resultFiles = listResultFiles(resultsDir)
  const browsers = new Map()

  for (const filePath of resultFiles) {
    const result = JSON.parse(fs.readFileSync(filePath, 'utf8'))
    const browser = browserFromResult(result)
    browsers.set(browser, (browsers.get(browser) ?? 0) + 1)
  }

  return { total: resultFiles.length, browsers }
}

function writeEnvironment({ total, browsers }) {
  const lines = [
    'Project=testflow-pytest',
    `Total.tests=${total}`,
    `Browsers=${[...browsers.keys()].sort().join(', ')}`,
  ]

  for (const [browser, count] of [...browsers.entries()].sort(([a], [b]) => a.localeCompare(b))) {
    lines.push(`Tests.${browser}=${count}`)
  }

  const githubSha = process.env.GITHUB_SHA
  if (githubSha) lines.push(`GitHub.SHA=${githubSha.slice(0, 7)}`)

  const githubRef = process.env.GITHUB_REF_NAME
  if (githubRef) lines.push(`GitHub.Ref=${githubRef}`)

  fs.writeFileSync(path.join(resultsDir, 'environment.properties'), `${lines.join('\n')}\n`)
}

function main() {
  const mergedFromStaging = mergeFromStaging()
  if (!mergedFromStaging && !fs.existsSync(resultsDir)) {
    console.log('No allure-results to merge')
    process.exit(0)
  }

  const summary = summarizeResults()
  if (summary.total === 0) {
    console.log('No Allure result files found after merge')
    process.exit(0)
  }

  writeEnvironment(summary)
  console.log(
    `Allure merge summary: ${summary.total} test(s) across ${summary.browsers.size} browser(s)`,
  )
  for (const [browser, count] of [...summary.browsers.entries()].sort(([a], [b]) => a.localeCompare(b))) {
    console.log(`  - ${browser}: ${count}`)
  }
}

main()
