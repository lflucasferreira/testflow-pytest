import { createHash } from 'node:crypto'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const resultsDir = path.join(root, process.env.ALLURE_RESULTS_DIR ?? 'allure-results')
const stagingDir = path.join(root, process.env.ALLURE_STAGING_DIR ?? 'allure-results-staging')
const projectName = process.env.ALLURE_PROJECT_NAME ?? 'testflow-pytest'

const SKIP_FILES = new Set(['environment.properties', 'executor.json'])

function walkFiles(dir) {
  if (!fs.existsSync(dir)) return []

  const files = []
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const fullPath = path.join(dir, entry.name)
    if (entry.isDirectory()) {
      files.push(...walkFiles(fullPath))
    } else if (entry.isFile()) {
      files.push(fullPath)
    }
  }
  return files
}

function resolveArtifactRoot(dir) {
  const nested = path.join(dir, 'allure-results')
  if (fs.existsSync(nested) && fs.statSync(nested).isDirectory()) {
    return nested
  }
  return dir
}

function browserFromStagingDir(dirName) {
  const match = dirName.match(/^allure-results-(.+)$/)
  return match?.[1] ?? dirName
}

function normalizeValue(value) {
  if (typeof value !== 'string') return value ?? null
  return value.replace(/^'+|'+$/g, '')
}

function ensureBrowserParameter(result, browser) {
  if (!Array.isArray(result.parameters)) {
    result.parameters = []
  }

  const existing = result.parameters.find((param) => param.name === 'browser')
  if (existing) {
    existing.value = `'${browser}'`
    return
  }

  result.parameters.push({ name: 'browser', value: `'${browser}'` })
}

function ensureBrowserLabel(result, browser) {
  const labels = Array.isArray(result.labels) ? result.labels : []
  const existing = labels.find((label) => label.name === 'browser')
  if (existing) {
    existing.value = browser
  } else {
    labels.push({ name: 'browser', value: browser })
  }
  result.labels = labels
}

function scopeResultToBrowser(result, browser) {
  ensureBrowserLabel(result, browser)
  ensureBrowserParameter(result, browser)

  const identity = [
    result.historyId ?? '',
    result.testCaseId ?? '',
    result.fullName ?? '',
    result.name ?? '',
    browser,
  ].join('::')

  result.historyId = createHash('md5').update(identity).digest('hex')
  result.testCaseId = createHash('md5').update(`${result.testCaseId ?? result.uuid ?? identity}::${browser}`).digest('hex')

  if (result.name && !result.name.includes(`[${browser}]`)) {
    result.name = `${result.name} [${browser}]`
  }
}

function browserFromResult(result) {
  const label = result.labels?.find((entry) => entry.name === 'browser')?.value
  if (label) return label

  const parameter = result.parameters?.find((entry) => entry.name === 'browser')?.value
  return normalizeValue(parameter) ?? 'unknown'
}

function uniqueTargetPath(targetPath) {
  if (!fs.existsSync(targetPath)) return targetPath

  const dir = path.dirname(targetPath)
  const ext = path.extname(targetPath)
  const base = path.basename(targetPath, ext)
  let index = 1

  while (fs.existsSync(path.join(dir, `${base}-${index}${ext}`))) {
    index += 1
  }

  return path.join(dir, `${base}-${index}${ext}`)
}

function copyArtifactTree(sourceDir, targetDir, browser) {
  const artifactRoot = resolveArtifactRoot(sourceDir)
  if (!fs.existsSync(artifactRoot)) return 0

  let copied = 0
  for (const filePath of walkFiles(artifactRoot)) {
    const rel = path.relative(artifactRoot, filePath)
    const fileName = path.basename(filePath)
    if (SKIP_FILES.has(fileName)) continue

    const targetPath = uniqueTargetPath(path.join(targetDir, rel))
    fs.mkdirSync(path.dirname(targetPath), { recursive: true })

    if (fileName.endsWith('-result.json')) {
      const result = JSON.parse(fs.readFileSync(filePath, 'utf8'))
      scopeResultToBrowser(result, browser)
      fs.writeFileSync(targetPath, `${JSON.stringify(result)}\n`)
    } else {
      fs.copyFileSync(filePath, targetPath)
    }

    copied += 1
  }

  return copied
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
    const count = copyArtifactTree(path.join(stagingDir, dirName), resultsDir, browser)
    console.log(`  ${dirName}: ${count} file(s) tagged as ${browser}`)
    copied += count
  }

  console.log(`Merged ${copied} file(s) from ${browserDirs.length} browser artifact(s)`)
  return copied > 0
}

function summarizeResults() {
  const resultFiles = walkFiles(resultsDir).filter((filePath) => filePath.endsWith('-result.json'))
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
    `Project=${projectName}`,
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
    process.exit(1)
  }

  writeEnvironment(summary)
  console.log(
    `Allure merge summary: ${summary.total} test(s) across ${summary.browsers.size} browser(s)`,
  )
  for (const [browser, count] of [...summary.browsers.entries()].sort(([a], [b]) => a.localeCompare(b))) {
    console.log(`  - ${browser}: ${count}`)
  }

  if (summary.browsers.size < 2 && process.env.CI === 'true') {
    console.warn(
      'Warning: expected multiple browsers in merged Allure results; check artifact downloads.',
    )
  }
}

main()
