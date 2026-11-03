import { Page } from '@playwright/test';

export interface SafetyGuardOptions {
  isProd: boolean;
  prodHost: string;
  minDelayBetweenNavigationsMs?: number;
  maxPageLoads?: number;
}

export class SafetyGuard {
  private pageLoadCount = 0;
  private lastNavTime = 0;
  private isProd: boolean;
  private prodHost: string;
  private minDelayMs: number;
  private maxPageLoads: number;

  constructor(options: SafetyGuardOptions) {
    this.isProd = options.isProd;
    this.prodHost = options.prodHost;
    this.minDelayMs = options.minDelayBetweenNavigationsMs || 2000;
    this.maxPageLoads = options.maxPageLoads || 200;
  }

  /**
   * Устанавливает перехватчик сети, блокирующий любые модифицирующие запросы на Prod
   */
  async attach(page: Page): Promise<void> {
    await page.route('**/*', async (route) => {
      const request = route.request();
      const method = request.method().toUpperCase();
      const url = request.url();

      if (this.isProd && (url.includes(this.prodHost) || url.includes('.onrender.com'))) {
        if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(method)) {
          console.error(`🚨 [SAFETY GUARD VIOLATION] Заблокирована попытка записи на Prod: ${method} ${url}`);
          await route.abort('blockedbyclient');
          throw new Error(`CRITICAL: writes_on_prod violation. Blocked ${method} request to ${url}`);
        }
      }

      await route.continue();
    });
  }

  /**
   * Контролирует задержку между навигациями для защиты от исчерпания ресурсов бесплатного тарифа
   */
  async paceNavigation(): Promise<void> {
    this.pageLoadCount++;
    if (this.isProd && this.pageLoadCount > this.maxPageLoads) {
      throw new Error(`Exceeded max_page_loads_per_pass (${this.maxPageLoads}) on Prod environment`);
    }

    const now = Date.now();
    const elapsed = now - this.lastNavTime;
    if (this.isProd && this.lastNavTime > 0 && elapsed < this.minDelayMs) {
      await new Promise((r) => setTimeout(r, this.minDelayMs - elapsed));
    }
    this.lastNavTime = Date.now();
  }
}

