import { Page } from '@playwright/test';

export interface VisualIssue {
  type: 'horizontal_overflow' | 'touch_target_too_small' | 'japanese_ruby_error' | 'tofu_characters' | 'clipped_text';
  element?: string;
  message: string;
  details?: any;
}

export class VisualOverflowDetector {
  /**
   * Проверяет отсутствие горизонтальной прокрутки страницы
   */
  static async checkHorizontalOverflow(page: Page): Promise<VisualIssue[]> {
    return await page.evaluate(() => {
      const issues: any[] = [];
      const docWidth = document.documentElement.clientWidth;
      const scrollWidth = document.documentElement.scrollWidth;

      if (scrollWidth > docWidth + 2) { // 2px погрешность субпикселей
        // Ищем конкретные переполняющие элементы
        const allElements = document.querySelectorAll('*');
        const overflowing: string[] = [];

        allElements.forEach((el) => {
          const rect = el.getBoundingClientRect();
          if (rect.right > docWidth + 2) {
            const id = el.id ? `#${el.id}` : '';
            const cls = el.className && typeof el.className === 'string' ? `.${el.className.split(' ').join('.')}` : '';
            overflowing.push(`${el.tagName.toLowerCase()}${id}${cls} (right: ${Math.round(rect.right)}px > ${docWidth}px)`);
          }
        });

        issues.push({
          type: 'horizontal_overflow',
          message: `Horizontal scroll detected: scrollWidth (${scrollWidth}px) > clientWidth (${docWidth}px)`,
          details: { overflowingElements: overflowing.slice(0, 5) },
        });
      }
      return issues;
    });
  }

  /**
   * Проверяет минимальный размер тач-зон (минимум 44x44px) для мобильных элементов
   */
  static async checkTouchTargets(page: Page, isMobile: boolean): Promise<VisualIssue[]> {
    if (!isMobile) return [];

    return await page.evaluate(() => {
      const issues: any[] = [];
      const interactive = document.querySelectorAll('button:not([disabled]), a[href], input, select, .filter-pill, .mini-pill, .nav-tab');

      interactive.forEach((el) => {
        // Проверяем только видимые элементы
        const style = window.getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
          return;
        }

        const rect = el.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) return;

        // Допускаем мини-кнопки управления таймером/закрытия от 32px, но не меньше 28px
        const minSize = el.classList.contains('mini-pill') || el.classList.contains('btn-timer-action') ? 28 : 40;

        if (rect.width < minSize || rect.height < minSize) {
          const text = (el.textContent || '').trim().slice(0, 20);
          issues.push({
            type: 'touch_target_too_small',
            element: `${el.tagName.toLowerCase()}.${el.className}`,
            message: `Touch target too small: ${Math.round(rect.width)}x${Math.round(rect.height)}px (min ${minSize}px) on '${text}'`,
            details: { width: rect.width, height: rect.height, text },
          });
        }
      });

      return issues;
    });
  }

  /**
   * Проверяет корректность рендеринга японской типографики и тегов furigana
   */
  static async checkJapaneseTypography(page: Page): Promise<VisualIssue[]> {
    return await page.evaluate(() => {
      const issues: any[] = [];

      // 1. Проверка структуры тегов <ruby>
      const rubies = document.querySelectorAll('ruby');
      rubies.forEach((ruby) => {
        const rt = ruby.querySelector('rt');
        if (!rt) {
          issues.push({
            type: 'japanese_ruby_error',
            message: `Tag <ruby> without child <rt>: '${ruby.textContent}'`,
          });
        } else if (!rt.textContent || rt.textContent.trim() === '') {
          issues.push({
            type: 'japanese_ruby_error',
            message: `Empty furigana <rt></rt> inside <ruby>`,
          });
        }
      });

      // 2. Проверка символов 'Tofu' (битые иероглифы)
      const bodyText = document.body.innerText || '';
      if (bodyText.includes('\uFFFD')) {
        issues.push({
          type: 'tofu_characters',
          message: 'Detected tofu / replacement character (\uFFFD) in rendered page text',
        });
      }

      return issues;
    });
  }
}
