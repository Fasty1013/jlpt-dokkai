import { Page, Response } from '@playwright/test';

export interface TelemetryIssue {
  type: 'console_error' | 'console_warn' | 'page_error' | 'http_error' | 'anti_cheat_leak' | 'csp_violation';
  message: string;
  url?: string;
  status?: number;
  details?: any;
}

export class TelemetryCollector {
  public issues: TelemetryIssue[] = [];
  public antiCheatLeaks: TelemetryIssue[] = [];

  attach(page: Page): void {
    // 1. Консольные ошибки и предупреждения
    page.on('console', (msg) => {
      const type = msg.type();
      const text = msg.text();
      if (type === 'error') {
        this.issues.push({
          type: 'console_error',
          message: text,
          url: page.url(),
        });
      } else if (type === 'warning') {
        // Игнорируем стандартные внешние предупреждения шрифтов / deprecations
        if (!text.includes('Third-party cookie') && !text.includes('DevTools')) {
          this.issues.push({
            type: 'console_warn',
            message: text,
            url: page.url(),
          });
        }
      }
    });

    // 2. Необработанные исключения JS
    page.on('pageerror', (err) => {
      this.issues.push({
        type: 'page_error',
        message: err.message,
        url: page.url(),
        details: err.stack,
      });
    });

    // 3. Сетевые ошибки (упавшие запросы)
    page.on('requestfailed', (req) => {
      // Игнорируем намеренно заблокированные расширениями или telemetry
      const failure = req.failure();
      this.issues.push({
        type: 'http_error',
        message: `Failed request: ${req.method()} ${req.url()} (${failure?.errorText || 'Unknown'})`,
        url: req.url(),
      });
    });

    // 4. Анализ ответов и Anti-Cheat Sniffer
    page.on('response', async (res: Response) => {
      const status = res.status();
      const url = res.url();

      if (status >= 400 && !url.includes('/favicon.ico')) {
        this.issues.push({
          type: 'http_error',
          status,
          message: `HTTP ${status} on ${res.request().method()} ${url}`,
          url,
        });
      }

      // Anti-Cheat Sniffer: Проверка эндпоинтов выдачи заданий на утечки ответов
      if (
        (url.includes('/api/texts/') || url.includes('/api/stream/slots')) &&
        !url.includes('/submit') &&
        !url.includes('/complete') &&
        !url.includes('/solved') &&
        res.request().method() === 'GET' &&
        status === 200
      ) {
        try {
          const body = await res.json();
          this.auditAntiCheatObject(body, url);
        } catch {
          // Игнорируем не-JSON ответы
        }
      }
    });
  }

  private auditAntiCheatObject(obj: any, url: string): void {
    if (!obj || typeof obj !== 'object') return;

    const forbiddenKeys = ['is_correct', 'explanation', 'trap_type', 'evidence_span_id'];

    const checkKeys = (target: any) => {
      if (Array.isArray(target)) {
        for (const item of target) checkKeys(item);
      } else if (target && typeof target === 'object') {
        for (const k of Object.keys(target)) {
          if (forbiddenKeys.includes(k) && target[k] !== undefined && target[k] !== null) {
            const leak: TelemetryIssue = {
              type: 'anti_cheat_leak',
              message: `ANTI-CHEAT LEAK DETECTED: field '${k}' present in reading API response`,
              url,
              details: { leakedKey: k, value: target[k] },
            };
            this.issues.push(leak);
            this.antiCheatLeaks.push(leak);
          }
          checkKeys(target[k]);
        }
      }
    };

    checkKeys(obj);
  }

  hasCriticalIssues(): boolean {
    return this.antiCheatLeaks.length > 0 || this.issues.some((i) => i.type === 'page_error');
  }

  clear(): void {
    this.issues = [];
    this.antiCheatLeaks = [];
  }
}

