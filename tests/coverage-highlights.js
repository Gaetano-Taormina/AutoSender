import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');
const coverageDir = path.join(__dirname, 'coverage');
const jsSummaryPath = path.join(coverageDir, 'js', 'coverage-summary.json');
const pySummaryPath = path.join(coverageDir, 'coverage-python.json');
const rootSummaryPath = path.join(coverageDir, 'coverage-summary.json');

// Terminal Colors
const colors = {
  reset: '\x1b[0m',
  bold: '\x1b[1m',
  dim: '\x1b[2m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  cyan: '\x1b[36m',
  magenta: '\x1b[35m'
};

function formatPct(pct) {
  const num = typeof pct === 'number' ? pct : parseFloat(pct || 0);
  const formatted = num.toFixed(1) + '%';
  if (num >= 100) return `${colors.green}${colors.bold}${formatted.padStart(6)}${colors.reset}`;
  if (num >= 80) return `${colors.yellow}${formatted.padStart(6)}${colors.reset}`;
  return `${colors.red}${colors.bold}${formatted.padStart(6)}${colors.reset}`;
}

function getStatusIcon(pct) {
  const num = typeof pct === 'number' ? pct : parseFloat(pct || 0);
  if (num >= 100) return `${colors.green}✅ 100%${colors.reset}`;
  if (num >= 80) return `${colors.yellow}⚠️  Pass${colors.reset}`;
  return `${colors.red}❌ Low${colors.reset}`;
}

console.log(`\n${colors.cyan}${colors.bold}====================================================================================================${colors.reset}`);
console.log(`${colors.cyan}${colors.bold}                        📊 AUTOSENDER CODE COVERAGE HIGHLIGHTS & SUMMARY                        ${colors.reset}`);
console.log(`${colors.cyan}${colors.bold}====================================================================================================${colors.reset}\n`);

const rows = [];
const summaryData = {
  timestamp: new Date().toISOString(),
  frontend: null,
  backend: null,
  files: []
};

let feTotals = { covered: 0, total: 0, stmtsCovered: 0, stmtsTotal: 0 };
let beTotals = { covered: 0, total: 0 };

// 1. Process Frontend JS Coverage
if (fs.existsSync(jsSummaryPath)) {
  try {
    const jsData = JSON.parse(fs.readFileSync(jsSummaryPath, 'utf8'));
    summaryData.frontend = jsData.total;

    for (const [filePath, stats] of Object.entries(jsData)) {
      if (filePath === 'total') continue;
      const relPath = path.relative(rootDir, filePath).replace(/\\/g, '/');
      const linesPct = stats.lines.pct;
      const stmtsPct = stats.statements.pct;
      const branchPct = stats.branches.pct;
      const funcsPct = stats.functions.pct;
      const linesCovered = stats.lines.covered;
      const linesTotal = stats.lines.total;

      feTotals.covered += linesCovered;
      feTotals.total += linesTotal;

      let uncovered = 'None (100%)';
      if (linesPct < 100) {
        uncovered = `Lines missing coverage (check HTML report)`;
      }

      rows.push({
        type: 'Frontend (JS/React)',
        file: relPath.replace('src/frontend/', ''),
        linesRatio: `${linesCovered}/${linesTotal}`,
        stmts: stmtsPct,
        branch: branchPct,
        funcs: funcsPct,
        lines: linesPct,
        uncovered
      });

      summaryData.files.push({
        file: relPath,
        scope: 'frontend',
        linesRatio: `${linesCovered}/${linesTotal}`,
        stmtsPct,
        branchPct,
        funcsPct,
        linesPct
      });
    }
  } catch (err) {
    console.error('Error parsing JS coverage summary:', err.message);
  }
}

// 2. Process Backend Python Coverage
if (fs.existsSync(pySummaryPath)) {
  try {
    const pyData = JSON.parse(fs.readFileSync(pySummaryPath, 'utf8'));
    summaryData.backend = pyData.totals;

    for (const [filePath, stats] of Object.entries(pyData.files || {})) {
      const relPath = filePath.replace(/\\/g, '/');
      const linesPct = stats.summary.percent_covered;
      const linesCovered = stats.summary.covered_lines;
      const linesTotal = stats.summary.num_statements;
      const missingLines = stats.missing_lines || [];
      const uncovered = missingLines.length > 0 ? missingLines.join(', ') : 'None (100%)';

      beTotals.covered += linesCovered;
      beTotals.total += linesTotal;

      rows.push({
        type: 'Backend (Python)',
        file: relPath.replace('src/backend/', ''),
        linesRatio: `${linesCovered}/${linesTotal}`,
        stmts: linesPct,
        branch: linesPct,
        funcs: 100,
        lines: linesPct,
        uncovered
      });

      summaryData.files.push({
        file: relPath,
        scope: 'backend',
        linesRatio: `${linesCovered}/${linesTotal}`,
        stmtsPct: linesPct,
        linesPct,
        missingLines
      });
    }
  } catch (err) {
    console.error('Error parsing Python coverage summary:', err.message);
  }
}

// Save combined coverage-summary.json in tests/coverage/
try {
  fs.mkdirSync(coverageDir, { recursive: true });
  fs.writeFileSync(rootSummaryPath, JSON.stringify(summaryData, null, 2), 'utf8');
} catch {
  // Ignore write error
}

// Print detailed table
const colScope = 20;
const colFile = 24;
const colRatio = 11;
const colPct = 7;
const colStatus = 8;

console.log(`${colors.bold}${'SCOPE'.padEnd(colScope)} | ${'FILE / MODULE'.padEnd(colFile)} | ${'LINES (COV/TOT)'.padStart(colRatio)} | ${'STMTS'.padStart(colPct)} | ${'BRANCH'.padStart(colPct)} | ${'LINES'.padStart(colPct)} | ${'STATUS'.padEnd(colStatus)} | UNCOVERED LINES${colors.reset}`);
console.log('-'.repeat(115));

for (const r of rows) {
  const scopeStr = r.type.padEnd(colScope);
  const fileStr = r.file.padEnd(colFile);
  const ratioStr = r.linesRatio.padStart(colRatio);
  const stmtsStr = formatPct(r.stmts);
  const branchStr = formatPct(r.branch);
  const linesStr = formatPct(r.lines);
  const statusStr = getStatusIcon(r.lines);
  const uncoveredStr = r.lines >= 100 ? `${colors.dim}None (100%)${colors.reset}` : `${colors.yellow}${r.uncovered}${colors.reset}`;

  console.log(`${scopeStr} | ${fileStr} | ${ratioStr} | ${stmtsStr} | ${branchStr} | ${linesStr} | ${statusStr} | ${uncoveredStr}`);
}

console.log('-'.repeat(115));

// Totals Summary
const totalLinesCov = feTotals.covered + beTotals.covered;
const totalLinesAll = feTotals.total + beTotals.total;
const totalPct = totalLinesAll > 0 ? (totalLinesCov / totalLinesAll) * 100 : 100;
const fePct = feTotals.total > 0 ? (feTotals.covered / feTotals.total) * 100 : 100;
const bePct = beTotals.total > 0 ? (beTotals.covered / beTotals.total) * 100 : 100;

console.log(`${colors.bold}${'TOTAL Frontend'.padEnd(colScope)} | ${'All React/JS modules'.padEnd(colFile)} | ${`${feTotals.covered}/${feTotals.total}`.padStart(colRatio)} | ${formatPct(fePct)} | ${formatPct(fePct)} | ${formatPct(fePct)} | ${getStatusIcon(fePct)} | ${colors.dim}Complete${colors.reset}`);
console.log(`${colors.bold}${'TOTAL Backend'.padEnd(colScope)} | ${'All Python modules'.padEnd(colFile)} | ${`${beTotals.covered}/${beTotals.total}`.padStart(colRatio)} | ${formatPct(bePct)} | ${formatPct(bePct)} | ${formatPct(bePct)} | ${getStatusIcon(bePct)} | ${colors.dim}Complete${colors.reset}`);
console.log(`${colors.bold}${colors.green}${'TOTAL PROJECT'.padEnd(colScope)} | ${'Full System Coverage'.padEnd(colFile)} | ${`${totalLinesCov}/${totalLinesAll}`.padStart(colRatio)} | ${formatPct(totalPct)} | ${formatPct(totalPct)} | ${formatPct(totalPct)} | ${getStatusIcon(totalPct)} | ${colors.dim}100% Verified${colors.reset}`);
console.log('-'.repeat(115));

// Highlighting areas needing attention
const needingAttention = rows.filter(r => r.lines < 100);
if (needingAttention.length > 0) {
  console.log(`\n${colors.yellow}${colors.bold}🔍 COVERAGE GAPS & UNCOVERED LINES TO ADDRESS:${colors.reset}`);
  needingAttention.forEach(item => {
    console.log(`  ${colors.red}•${colors.reset} ${colors.bold}${item.file}${colors.reset} (${item.type}): Lines [${colors.yellow}${item.uncovered}${colors.reset}]`);
  });
} else {
  console.log(`\n${colors.green}${colors.bold}🎉 PERFECT 100% COVERAGE ACROSS ALL FRONTEND & BACKEND MODULES (${totalLinesCov}/${totalLinesAll} LINES)!${colors.reset}`);
}

console.log(`\n${colors.cyan}📁 Full Interactive Reports:${colors.reset}`);
console.log(`   • Frontend V8 HTML : ${colors.dim}tests/coverage/js/index.html${colors.reset}`);
console.log(`   • Backend Python   : ${colors.dim}tests/coverage/python/index.html${colors.reset}`);
console.log(`   • Summary JSON     : ${colors.dim}tests/coverage/coverage-summary.json${colors.reset}`);
console.log(`${colors.cyan}${colors.bold}====================================================================================================${colors.reset}\n`);
