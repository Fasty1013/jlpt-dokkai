/**
 * Server messages (HTTP `detail`, report `message`) are Russian strings produced by the backend.
 * The API contract is unchanged; the client maps the known messages to localized text by exact match.
 * Unknown messages are shown as received.
 */
import { ru } from './locales/ru.js';
import { t } from './index.js';

const EXACT = new Map(
  ['srv.taskNotFound', 'srv.draftNotFound', 'srv.pdfOnly', 'srv.notSolved', 'srv.reportOk', 'srv.reportHidden', 'srv.adminRequired']
    .map((key) => [ru[key], key])
);
const COMMIT_FAILED_PREFIX = 'Ошибка фиксации задания: ';

export function localizeServerMessage(msg) {
  if (typeof msg !== 'string') return msg;
  const key = EXACT.get(msg);
  if (key) return t(key);
  if (msg.startsWith(COMMIT_FAILED_PREFIX)) {
    return t('srv.commitFailed', { detail: msg.slice(COMMIT_FAILED_PREFIX.length) });
  }
  return msg;
}
