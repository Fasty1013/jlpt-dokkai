/**
 * JLPT Dokkai Master - i18n event wiring: header language <select data-action="set-language">.
 */
import { registerAction } from '../features/events/action_dispatcher.js';
import { setLang } from './index.js';

export function initI18nEvents() {
  registerAction('set-language', (el) => {
    setLang(el.value);
  });
}
