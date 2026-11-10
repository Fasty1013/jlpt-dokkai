#!/usr/bin/env node
/**
 * PreToolUse hook (Bash, `git commit*`): verification gate before every commit.
 *  1. Refuses to commit a real .env file (rule 7).
 *  2. Runs tools/check_dependency_graph.cjs (0 import cycles).
 *  3. If the commit touches application code (static/, app/, main.py), runs the
 *     full main-parity suite (rule 2): interactive walkthrough, computed styles,
 *     network flow, screenshots + pixel diff. Needs branch on :8000 and main on :8001.
 * Any failure -> permissionDecision "deny" with the reason; success -> silent allow.
 */
const { spawnSync } = require('child_process');
const http = require('http');
const fs = require('fs');
const os = require('os');
const path = require('path');

const ROOT = process.env.CLAUDE_PROJECT_DIR || process.cwd();
const LOG_DIR = path.join(os.tmpdir(), 'dokkai-precommit');

function out(decision, reason, context) {
  const o = { hookSpecificOutput: { hookEventName: 'PreToolUse' } };
  if (decision) {
    o.hookSpecificOutput.permissionDecision = decision;
    o.hookSpecificOutput.permissionDecisionReason = reason;
  }
  if (context) o.hookSpecificOutput.additionalContext = context;
  process.stdout.write(JSON.stringify(o));
  process.exit(0);
}

function git(args) {
  const r = spawnSync('git', args, { cwd: ROOT, encoding: 'utf-8' });
  return (r.stdout || '').split('\n').map((s) => s.trim()).filter(Boolean);
}

function ping(port) {
  return new Promise((resolve) => {
    const req = http.get({ host: '127.0.0.1', port, path: '/', timeout: 3000 }, (res) => {
      res.resume();
      resolve(res.statusCode === 200);
    });
    req.on('error', () => resolve(false));
    req.on('timeout', () => { req.destroy(); resolve(false); });
  });
}

function run(name, cmd, args, timeoutMs) {
  const r = spawnSync(cmd, args, { cwd: ROOT, encoding: 'utf-8', timeout: timeoutMs, maxBuffer: 64 * 1024 * 1024 });
  const text = `${r.stdout || ''}\n${r.stderr || ''}`;
  fs.mkdirSync(LOG_DIR, { recursive: true });
  const logFile = path.join(LOG_DIR, `${name}.log`);
  fs.writeFileSync(logFile, text, 'utf-8');
  return { code: r.status, text, logFile, timedOut: !!(r.error && r.error.code === 'ETIMEDOUT') };
}

function tail(text, n = 12) {
  return text.trim().split('\n').slice(-n).join('\n');
}

let raw = '';
process.stdin.on('data', (c) => (raw += c));
process.stdin.on('end', async () => {
  let cmd = '';
  try { cmd = String((JSON.parse(raw).tool_input || {}).command || ''); } catch { process.exit(0); }
  if (!/\bgit\b[^\n]*\bcommit\b/.test(cmd)) process.exit(0);

  // Files that this commit will contain.
  const files = new Set(git(['diff', '--cached', '--name-only']));
  if (/\scommit\b[^\n]*\s(-a\b|--all\b|-[a-zA-Z]*a[a-zA-Z]*\b)/.test(cmd)) {
    git(['diff', '--name-only']).forEach((f) => files.add(f));
  }

  // 1. Secrets.
  const envFiles = [...files].filter((f) => path.basename(f) === '.env');
  if (envFiles.length) {
    out('deny', `Dokkai rule 7: в коммит попадает ${envFiles.join(', ')} — секреты не коммитятся. Уберите его: git restore --staged .env`);
  }

  // 2. Dependency graph (fast, always).
  const graph = run('dependency_graph', 'node', ['tools/check_dependency_graph.cjs'], 60000);
  if (graph.code !== 0 || !/0 cycles/.test(graph.text)) {
    out('deny', `Граф ES-модулей не прошёл проверку (циклы или ошибка). Лог: ${graph.logFile}\n${tail(graph.text)}`);
  }

  // 3. Full parity only when application code changes.
  const codeChanged = [...files].some((f) => /^(static\/|app\/|main\.py$)/.test(f));
  if (!codeChanged) {
    out(null, null, 'Pre-commit: граф модулей OK (0 циклов); код приложения не менялся — проверка паритета пропущена.');
  }

  const [up8000, up8001] = await Promise.all([ping(8000), ping(8001)]);
  if (!up8000 || !up8001) {
    out('deny', `Проверка паритета требует оба сервера: ветка на :8000 (${up8000 ? 'up' : 'DOWN'}) и main на :8001 (${up8001 ? 'up' : 'DOWN'}). ` +
      'Запустите их ($env:DOKKAI_TEST_MODE="1"; python -m uvicorn main:app --port 8000 / 8001 в Dokkai-main-compare) и повторите коммит.');
  }

  const checks = [
    ['walkthrough', 'node', ['tools/compare_interactive_walkthrough.cjs'], (r) => r.code === 0 && /PARITY CONFIRMED/.test(r.text)],
    ['computed_styles', 'node', ['tools/compare_computed_styles.cjs'], (r) => r.code === 0 && /0 DISCREPANCIES/.test(r.text)],
    ['network_flow', 'node', ['tools/compare_network_flow.cjs'], (r) => r.code === 0 && /0 DISCREPANCIES FOUND/.test(r.text)],
    ['screenshots', 'node', ['tools/compare_screenshots.cjs'], (r) => r.code === 0],
    ['pixel_diff', 'python', ['tools/pixel_diff.py'], (r) => r.code === 0 && !/Файлы не найдены/.test(r.text)]
  ];
  const passed = [];
  for (const [name, bin, args, ok] of checks) {
    const r = run(name, bin, args, 300000);
    if (!ok(r)) {
      out('deny', `Паритет с main нарушен на шаге «${name}»${r.timedOut ? ' (таймаут)' : ''}. Лог: ${r.logFile}\n${tail(r.text)}`);
    }
    passed.push(name);
  }
  out(null, null, `Pre-commit: граф OK, паритет с main подтверждён (${passed.join(', ')}). Логи: ${LOG_DIR}`);
});
