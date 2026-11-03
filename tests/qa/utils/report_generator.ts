import * as fs from 'fs';
import * as path from 'path';

export interface BugRecord {
  id: string;
  title: string;
  severity: 'blocker' | 'critical' | 'major' | 'minor' | 'cosmetic';
  category: 'functional' | 'visual' | 'a11y' | 'performance' | 'console_network' | 'privacy_security' | 'content' | 'external' | 'environment';
  env: {
    where: 'prod' | 'local';
    url: string;
    viewport: string;
    engine: string;
    theme: string;
    network: string;
    build?: string;
  };
  steps: string[];
  expected: string;
  actual: string;
  evidence: string[];
  reproduced: string;
  suspected_cause: string;
  status: 'new' | 'confirmed' | 'flaky' | 'fixed' | 'verified' | 'wontfix';
}

export class QAReportGenerator {
  private static bugs: Map<string, BugRecord> = new Map();
  private static qaDir = path.resolve(__dirname, '../../../docs/qa');
  private static evidenceDir = path.resolve(__dirname, '../../../docs/qa/evidence');

  static registerBug(bug: Omit<BugRecord, 'id'> & { id?: string }): void {
    if (!fs.existsSync(this.qaDir)) {
      fs.mkdirSync(this.qaDir, { recursive: true });
    }
    if (!fs.existsSync(this.evidenceDir)) {
      fs.mkdirSync(this.evidenceDir, { recursive: true });
    }

    // Дедупликация по ключу title + category + where
    const dedupKey = `${bug.category}:${bug.title}:${bug.env.where}`;
    const existing = this.bugs.get(dedupKey);

    if (existing) {
      existing.reproduced = '2/2';
      existing.evidence.push(...bug.evidence.filter((e) => !existing.evidence.includes(e)));
      existing.status = 'confirmed';
    } else {
      const bugId = bug.id || `QA-${String(this.bugs.size + 1).padStart(3, '0')}`;
      const record: BugRecord = {
        ...bug,
        id: bugId,
      };
      this.bugs.set(dedupKey, record);
    }
  }

  static getBugs(): BugRecord[] {
    return Array.from(this.bugs.values());
  }

  static saveReport(coldStartTimeMs?: number, buildInfo?: any): { jsonPath: string; mdPath: string } {
    if (!fs.existsSync(this.qaDir)) {
      fs.mkdirSync(this.qaDir, { recursive: true });
    }

    const bugList = Array.from(this.bugs.values());
    const jsonPath = path.join(this.qaDir, 'bugs.json');
    fs.writeFileSync(jsonPath, JSON.stringify(bugList, null, 2), 'utf-8');

    // Формирование Markdown отчета
    const dateStr = new Date().toISOString().split('T')[0];
    const mdPath = path.join(this.qaDir, `REPORT-${dateStr}.md`);

    const counts = {
      blocker: bugList.filter((b) => b.severity === 'blocker').length,
      critical: bugList.filter((b) => b.severity === 'critical').length,
      major: bugList.filter((b) => b.severity === 'major').length,
      minor: bugList.filter((b) => b.severity === 'minor').length,
      cosmetic: bugList.filter((b) => b.severity === 'cosmetic').length,
    };

    let md = `# 📊 QA Test Execution Report (${dateStr})\n\n`;
    md += `## 📌 Сводка по дефектам\n\n`;
    md += `| Уровень серьёзности | Найдено |\n| :--- | :---: |\n`;
    md += `| 🔴 **Blocker** | **${counts.blocker}** |\n`;
    md += `| 🟠 **Critical** | **${counts.critical}** |\n`;
    md += `| 🟡 **Major** | **${counts.major}** |\n`;
    md += `| 🔵 **Minor** | **${counts.minor}** |\n`;
    md += `| ⚪ **Cosmetic** | **${counts.cosmetic}** |\n\n`;

    if (coldStartTimeMs) {
      md += `⏱️ **Время холодного старта Render:** ${(coldStartTimeMs / 1000).toFixed(1)} с\n\n`;
    }
    if (buildInfo) {
      md += `🏷️ **Версия сборки:** \`${buildInfo.version || '2.0.2'}\` (Commit: \`${buildInfo.commit || 'unknown'}\`, Env: \`${buildInfo.env || 'local'}\`)\n\n`;
    }

    md += `## 🐛 Детальный реестр дефектов\n\n`;
    if (bugList.length === 0) {
      md += `🎉 **Дефектов не обнаружено! Все проверки пройдены со 100% успехом.**\n\n`;
    } else {
      bugList.forEach((bug) => {
        md += `### [${bug.id}] ${bug.title}\n`;
        md += `- **Серьёзность:** \`${bug.severity}\` | **Категория:** \`${bug.category}\` | **Статус:** \`${bug.status}\` (Воспроизведено: ${bug.reproduced})\n`;
        md += `- **Окружение:** ${bug.env.where} (${bug.env.viewport}, ${bug.env.engine}, тема: ${bug.env.theme})\n`;
        md += `- **Шаги для воспроизведения:**\n`;
        bug.steps.forEach((s) => (md += `  ${s}\n`));
        md += `- **Ожидаемый результат:** ${bug.expected}\n`;
        md += `- **Фактический результат:** ${bug.actual}\n`;
        if (bug.suspected_cause) {
          md += `- **Предполагаемая причина:** *${bug.suspected_cause}*\n`;
        }
        if (bug.evidence && bug.evidence.length > 0) {
          md += `- **Доказательства:** ${bug.evidence.join(', ')}\n`;
        }
        md += `\n---\n\n`;
      });
    }

    fs.writeFileSync(mdPath, md, 'utf-8');
    return { jsonPath, mdPath };
  }
}

