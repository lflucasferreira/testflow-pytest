import { execSync } from 'node:child_process'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const resultsDir = path.join(root, 'allure-results')
const reportDir = path.join(root, 'allure-report')

if (!fs.existsSync(resultsDir) || fs.readdirSync(resultsDir).length === 0) {
  console.error('No allure-results found. Run tests first: pytest')
  process.exit(1)
}

fs.rmSync(reportDir, { recursive: true, force: true })
execSync('npx allure generate allure-results --output allure-report', {
  cwd: root,
  stdio: 'inherit',
})

console.log(`Allure report ready at ${path.relative(root, reportDir)}/`)
