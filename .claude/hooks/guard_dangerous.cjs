#!/usr/bin/env node
/**
 * PreToolUse hook (Bash | PowerShell): rule 7 of CLAUDE.md.
 * - Destructive commands -> "ask" (the user must explicitly approve in the prompt).
 * - Staging/committing a real .env file -> "deny".
 */
let raw = '';
process.stdin.on('data', (c) => (raw += c));
process.stdin.on('end', () => {
  let cmd = '';
  try {
    cmd = String((JSON.parse(raw).tool_input || {}).command || '');
  } catch {
    process.exit(0);
  }

  const decide = (decision, reason) => {
    process.stdout.write(JSON.stringify({
      hookSpecificOutput: {
        hookEventName: 'PreToolUse',
        permissionDecision: decision,
        permissionDecisionReason: reason
      }
    }));
    process.exit(0);
  };

  // Secrets: a real .env (not .env.example / .env.sample) must never reach git.
  const envFile = /(^|[\s"'\/\\])\.env(?![.\w-])/;
  if (/\bgit\b[^\n;&|]*\b(add|commit|stash)\b/i.test(cmd) && envFile.test(cmd)) {
    decide('deny', 'Dokkai rule 7: .env содержит секреты и не должен попадать в git.');
  }

  const dangerous = [
    [/\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r|--recursive\s+--force|--force\s+--recursive)\b/, 'rm -rf'],
    [/\bRemove-Item\b(?=.*-Recurse)(?=.*-Force)/i, 'Remove-Item -Recurse -Force'],
    [/\b(rmdir|rd)\s+\/s\b/i, 'rmdir /s'],
    [/\bDROP\s+(TABLE|DATABASE|SCHEMA)\b/i, 'DROP TABLE/DATABASE'],
    [/\bTRUNCATE\s+TABLE\b/i, 'TRUNCATE TABLE'],
    [/\bgit\s+push\b.*(\s--force\b|\s-f\b|\s--force-with-lease\b|\s\+\S)/, 'git push --force'],
    [/\bgit\s+reset\s+--hard\b/, 'git reset --hard'],
    [/\bgit\s+clean\s+-[a-zA-Z]*f/, 'git clean -f'],
    [/\bgit\s+(checkout|restore)\s+(--\s+)?\.(\s|$)/, 'git checkout/restore . (discard all changes)'],
    [/\bgit\s+branch\s+-D\b/, 'git branch -D']
  ];
  for (const [re, name] of dangerous) {
    if (re.test(cmd)) {
      decide('ask', `Dokkai rule 7: деструктивная команда (${name}) требует явного разрешения пользователя.`);
    }
  }
  process.exit(0);
});
