# 📋 MIGRATION NOTES: Временные глобальные мосты (`window.*`), Fallback-резолверы и план их вывода

> Документ создан в рамках Шага 5 (Декомпозиция `app.js`).  
> Фиксирует все временные мосты `window.*`, защитные резолверы и fallback-механизмы, обеспечивающие обратную совместимость между новыми модулями и существующим кодом `app.js`, а также пошаговый план их полного устранения в **Шаге 6** (Делегирование событий и ликвидация инлайн-обработчиков) и последующих шагах.

---

## 1. Контекст и архитектурный переход

В процессе рефакторинга монолита `static/app.js` код постепенно переносится в модули ES6:
- `static/js/api/` — API-клиент с обработкой таймаутов, холодного старта и типизацией ошибок.
- `static/js/utils/` — чистые вспомогательные утилиты (`dom`, `format`, `math`, `time`, `user`).
- `static/js/features/timer/` — логика таймера (обратный отсчёт, пауза, добавление минут, скрытие, запуск в рантайме).
- `static/js/features/settings/` — настройки шрифтов читалки и размера текста.
- `static/js/features/formatting/` — вспомогательное форматирование.
- `static/js/features/pretest/` — модальное окно предстартовых настроек (фуригана, таймер, разбор) и сохранение конфига.
- `static/js/features/stream/` — динамический каталог и слоты заданий, карточки, замещение слотов.
- `static/js/features/solved/` — архив решённых заданий, модальное окно жалоб и дефектов.

Чтобы избежать разрыва связей на промежуточных этапах (zero-breaking changes), новые модули предоставляют:
1. Стандартные ES6-экспорты (`export { ... }`).
2. Пространства имён на объекте `window` (например, `window.DokkaiTimer`).
3. Прямые функции-мосты на `window` (например, `window.stopTimer = stopTimer`).
4. Защитные резолверы (`resolveTimerState`, `resolveElements`), гарантирующие работу при неявном вызове функций без передачи контекста.

---

## 2. Сводная таблица жизненного цикла всех мостов, fallback и резолверов

| № | Идентификатор моста / Fallback | Где объявлен | Где используется | Причина сохранения | Этап полного удаления |
| :-: | :--- | :--- | :--- | :--- | :-: |
| 1 | **`resolveTimerState(timerState)`** | `static/js/features/timer/timer.js` | Все методы таймера (`stopTimer`, `startUntimedMode`, `startCountdownTimer`, etc.) | Fallback на `window.state?.timer` при вызовах без аргументов из старых участков `app.js` | **Шаг 6** (при переходе на явную передачу контекста) |
| 2 | **`resolveElements(elements)`** | `static/js/features/timer/timer.js` | Манипуляции таймера с DOM (`#reading-timer-container`, `#timer-display`, etc.) | Fallback на `window.elements` при вызовах без DOM-ссылок | **Шаг 6** (переход на data-атрибуты и селекторы) |
| 3 | **`window.DokkaiTimer`** | `static/js/features/timer/index.js` | `app.js:347-372` (обёртки таймера в монолите) | Пространство имён таймера для монолитного скрипта | **Шаг 6** (замена на прямой `import` в модули) |
| 4 | **`window.stopTimer`**, `startUntimedMode`, `startCountdownTimer`, `toggleTimerPause`, `addTimerMinute`, `dismissTimer`, `enableTimerAtRuntime` | `static/js/features/timer/index.js` | Обратная совместимость для внешних/глобальных вызовов | Сохранение глобальной сигнатуры функций таймера | **Шаг 6** |
| 5 | **`window.DokkaiSettings`** | `static/js/features/settings/index.js` | `app.js:380-388` (обёртки настроек шрифта) | Пространство имён настроек читалки | **Шаг 6** |
| 6 | **`window.saveUserSettings`**, `setReaderFont`, `adjustFontSize` | `static/js/features/settings/index.js` | Обратная совместимость для глобальных вызовов настроек | Поддержка вызовов без префикса модуля | **Шаг 6** |
| 7 | **`window.DokkaiFormatting`** | `static/js/features/formatting/index.js` | `app.js:20-25` (`loadStoredConfig`, `saveStoredConfig`) | Пространство имён предстартовых настроек | **Шаг 6** (интеграция в модуль предстарта) |
| 8 | **`window.loadStoredConfig`**, `saveStoredConfig` | `static/js/features/formatting/index.js` | Инициализация конфигурации в начале `app.js` | Обратная совместимость | **Шаг 6** |
| 9 | **`window.DokkaiUtils`** | `static/js/utils/index.js` | `app.js:14-17`, модули API, тесты Playwright | Единый фасад чистых утилит (`user`, `dom`, `time`, `math`, `format`) | **Шаг 9** (в финале модули импортируют утилиты напрямую) |
| 10 | **`window.getUserId`**, `escapeHtml`, `formatTime`, `formatLocaleDate`, `calculateScorePercent`, `formatFileSize` | `static/js/utils/index.js` | Старые вызовы без префикса, динамические строки верстки | Совместимость с незатронутым кодом монолита | **Шаг 6** |
| 11 | **`window.DokkaiApi`** | `static/js/api/index.js` | `app.js:424, 539, 627, 660, 720, 871, 1150, 1642` | Все сетевые операции до их декомпозиции | **Шаг 9** (замена на прямые ES-импорты в фичах) |
| 12 | **`window.state`** | `static/app.js:310` | Резолверы `timer.js`, DevTools, тесты Playwright | Глобальный доступ к состоянию монолита | **Шаг 7** (выделение локальных сторов / Storage) |
| 13 | **`window.elements`** | `static/app.js:311` | Резолверы `timer.js`, тесты Playwright | Кэш DOM-элементов монолита | **Шаг 6** (переход на делегирование событий) |
| 14 | **`window.openPretestModal`** | `app.js:776` | `renderStreamSlots()` (`app.js:474, 487`) | Вызов из инлайн `onclick="openPretestModal(...)"` | **Шаг 6** (перевод на `data-action="open-pretest"`) |
| 15 | **`window.fetchAndRenderSlots`** | `app.js:419` | `renderStreamSlots()` (`app.js:499`) | Вызов из инлайн `onclick="fetchAndRenderSlots()"` | **Шаг 6** (перевод на `data-action="reload-slots"`) |
| 16 | **`window.reviewSolvedTask`** | `app.js:624` | `renderSolvedTasks()` (`app.js:601`) | Вызов из инлайн `onclick="reviewSolvedTask(...)"` | **Шаг 6** (перевод на `data-action="review-solved"`) |
| 17 | **`window.retrySolvedTask`** | `app.js:657` | `renderSolvedTasks()` (`app.js:604`) | Вызов из инлайн `onclick="retrySolvedTask(...)"` | **Шаг 6** (перевод на `data-action="retry-solved"`) |
| 18 | **`window.openReportModal`** | `app.js:698` | `renderSolvedTasks()` (`app.js:607`) | Вызов из инлайн `onclick="openReportModal(...)"` | **Шаг 6** (перевод на `data-action="open-report"`) |
| 19 | **`window.switchAnalysisTab`** | `app.js:1298` | `renderAnalysisView()` (`app.js:1300`) | Вызов из инлайн `onclick="switchAnalysisTab(...)"` | **Шаг 6** (перевод на `data-action="switch-tab"`) |
| 20 | **`window.locateEvidenceInText`** | `app.js:1376` | `renderAnalysisView()` (`app.js:1379`) | Вызов из инлайн `onclick="locateEvidenceInText(...)"` | **Шаг 6** (перевод на `data-action="locate-evidence"`) |
| 21 | **`window.saveDraft`** | `app.js:2045` | `renderDrafts()` (`app.js:2048`) | Вызов из инлайн `onclick="saveDraft(...)"` | **Шаг 6** (перевод на `data-action="save-draft"`) |
| 22 | **`window.deleteDraft`** | `app.js:2049` | `renderDrafts()` (`app.js:2051`) | Вызов из инлайн `onclick="deleteDraft(...)"` | **Шаг 6** (перевод на `data-action="delete-draft"`) |
| 23 | **`window.publishDraft`** | `app.js:2053` | `renderDrafts()` (`app.js:2055`) | Вызов из инлайн `onclick="publishDraft(...)"` | **Шаг 6** (перевод на `data-action="publish-draft"`) |
| 24 | **`window.markDraftCorrectOption`** | `app.js:2140` | `renderDraftQuestions()` (`app.js:2143`) | Вызов из инлайн `onclick="markDraftCorrectOption(...)"` | **Шаг 6** (перевод на `data-action="mark-option"`) |

---

## 3. Детализация защитных резолверов в `timer.js`

В модуле `static/js/features/timer/timer.js` реализованы два защитных резолвера:

```javascript
function resolveTimerState(timerState) {
  if (timerState) return timerState;
  if (typeof window !== 'undefined' && window.state && window.state.timer) {
    return window.state.timer;
  }
  return null;
}

function resolveElements(elements) {
  if (elements) return elements;
  if (typeof window !== 'undefined' && window.elements) {
    return window.elements;
  }
  return {};
}
```

### Зачем они нужны:
1. До рефакторинга вызовы `startUntimedMode()`, `stopTimer()`, `toggleTimerPause()` внутри `app.js` производились без аргументов и неявно читали переменные из замыкания `state` и `elements`.
2. После выноса таймера в отдельный модуль функция экспортируется на `window`. Если любой старый обработчик вызывает её без аргументов, резолвер безопасно подхватывает объект `window.state.timer` и `window.elements`, предотвращая ошибки `TypeError: Cannot set properties of undefined`.

### План ликвидации на Шаге 6:
- При переводе обработчиков на единый `initEventListeners` вызовы методов таймера будут производиться либо с явной передачей `(timerState, elements)`, либо через выделенный `TimerService` с собственным инкапсулированным состоянием.
- Защитные резолверы будут удалены из `timer.js`, сделав модуль полностью чистым и независимым от глобального `window`.

---

## 4. План ликвидации мостов в Шаге 6 (Event Delegation)

В соответствии с согласованным 9-шаговым планом, **Шаг 6** целиком посвящён рефакторингу обработчиков событий:
> «Шаг 6. Обработчики событий (initEventListeners, 525 строк), замена динамических onclick на делегирование через data-action и data-id».

### Этапы вывода из эксплуатации:

1. **Замена динамических `onclick` атрибутов на декларативные data-атрибуты:**
   - Вместо `<button onclick="reviewSolvedTask(${id})">`:  
     `<button data-action="review-solved" data-task-id="${id}">`
   - Вместо `<button onclick="retrySolvedTask(${id})">`:  
     `<button data-action="retry-solved" data-task-id="${id}">`
   - Вместо `<button onclick="openReportModal(${id}, '${title}')">`:  
     `<button data-action="open-report" data-task-id="${id}" data-task-title="${escapeHtml(title)}">`
   - Вместо `<button onclick="openPretestModal(${id})">`:  
     `<div class="stream-slot-card" data-action="open-pretest" data-text-id="${id}">`
   - Вместо `<button onclick="switchAnalysisTab(${idx})">`:  
     `<button class="analysis-tab-btn" data-action="switch-tab" data-tab-index="${idx}">`
   - Вместо `<button onclick="locateEvidenceInText('${spanId}')">`:  
     `<button class="btn-locate-evidence" data-action="locate-evidence" data-span-id="${spanId}">`
   - Вместо кнопок черновиков админки:  
     `data-action="save-draft"`, `data-action="delete-draft"`, `data-action="publish-draft"` с `data-slug="${slug}"`.

2. **Централизованное делегирование событий в `initEventListeners`:**
   - На контейнерах списков (или на уровне стабильных родительских блоков/`document`):
     ```javascript
     document.addEventListener('click', (event) => {
       const actionBtn = event.target.closest('[data-action]');
       if (!actionBtn) return;
       
       const action = actionBtn.dataset.action;
       switch (action) {
         case 'review-solved':
           reviewSolvedTask(Number(actionBtn.dataset.taskId));
           break;
         case 'retry-solved':
           retrySolvedTask(Number(actionBtn.dataset.taskId));
           break;
         // ... остальные действия
       }
     });
     ```

3. **Ликвидация прямых функций на `window`:**
   - Удаление строк `window.reviewSolvedTask = ...`, `window.openReportModal = ...` из `app.js`.
   - Удаление прямых функций-мостов `window.stopTimer`, `window.formatTime` и др., так как модули будут импортировать их напрямую через стандартный синтаксис ES6 модулей `import { stopTimer } from './features/timer/index.js'`.

4. **Инкапсуляция состояния (`state` и `elements`):**
   - Перевод передачи зависимостей на явные аргументы и сторы/сервисы.
   - Удаление `window.state = state` и `window.elements = elements` после завершения модульной миграции всех областей в Шагах 5–7.

---

## 5. Контроль целостности и безопасность

1. **Anti-Cheat:**  
   Удаление функций с `window` гарантирует невозможность вызова внутренних управляющих методов напрямую из DevTools-консоли браузера или сторонними скриптами.
2. **Кэш Service Worker:**  
   Все модули, участвующие в декомпозиции, проверяются тестом графа импортов (`12_service_worker_integrity.spec.ts`) и автоматически синхронизируются со списком предкэширования.
3. **Регрессионное тестирование:**  
   Автоматизированные тесты Playwright (30 сьютов) проверяют все сценарии кликов и навигации, гарантируя отсутствие регрессий при переходе от inline `onclick` к `data-action`.
