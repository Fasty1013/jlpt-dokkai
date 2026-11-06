# 📋 MIGRATION NOTES: Временные глобальные мосты (`window.*`) и план их вывода

> Документ создан в рамках Шага 5 (Декомпозиция `app.js`).  
> Фиксирует все временные мосты `window.*`, обеспечивающие обратную совместимость между модулями и существующим кодом `app.js`, а также пошаговый план их полного устранения в **Шаге 6** (Делегирование событий и ликвидация инлайн-обработчиков).

---

## 1. Контекст и архитектурный переход

В процессе рефакторинга монолита `static/app.js` код постепенно переносится в модули ES6:
- `static/js/api/` — API-клиент с обработкой таймаутов, холодного старта и типизацией ошибок.
- `static/js/utils/` — чистые вспомогательные утилиты (`dom`, `math`, `time`, `user`).
- `static/js/features/timer/` — логика таймера (обратный отсчёт, пауза, добавление минут, скрытие, запуск в рантайме).
- `static/js/features/settings/` — настройки шрифтов читалки и размера текста.
- `static/js/features/formatting/` — форматирование байт, сохранение/загрузка предстартовой конфигурации.

Чтобы избежать разрыва связей на промежуточных этапах (zero-breaking changes), новые модули предоставляют:
1. Стандартные ES6-экспорты (`export { ... }`).
2. Пространства имён на объекте `window` (например, `window.DokkaiTimer`).
3. Прямые функции-мосты на `window` (например, `window.stopTimer = stopTimer`), позволяющие коду `app.js` и HTML-шаблонам бесшовно продолжать работу до этапа полной перевязки событий.

---

## 2. Полный реестр временных мостов на объекте `window`

### 2.1. Глобальные пространства имён модулей

| Объект | Файл-источник | Назначение |
| :--- | :--- | :--- |
| `window.DokkaiApi` | `static/js/api/index.js` | Все методы сетевого взаимодействия с бэкендом Dokkai |
| `window.DokkaiTimer` | `static/js/features/timer/index.js` | Логика и управление таймером тренировки |
| `window.DokkaiSettings` | `static/js/features/settings/index.js` | Управление стилями шрифта читалки и сохранение в localStorage |
| `window.DokkaiFormatting` | `static/js/features/formatting/index.js` | Форматирование размеров файлов и хранение настроек предстарта |
| `window.DokkaiUtils` | `static/js/utils/index.js` | Единый источник истины для чистых утилит (id пользователя, экранирование HTML, форматирование дат/времени, расчёт баллов) |

---

### 2.2. Прямые функции-мосты на `window`

Для обеспечения вызовов старыми участками `app.js` и шаблонами:

#### Модуль `DokkaiTimer`:
- `window.stopTimer`
- `window.startUntimedMode`
- `window.startCountdownTimer`
- `window.toggleTimerPause`
- `window.addTimerMinute`
- `window.dismissTimer`
- `window.enableTimerAtRuntime`

#### Модуль `DokkaiSettings`:
- `window.saveUserSettings`
- `window.setReaderFont`
- `window.adjustFontSize`

#### Модуль `DokkaiFormatting`:
- `window.formatFileSize`
- `window.escapeHtml`
- `window.loadStoredConfig`
- `window.saveStoredConfig`

#### Модуль `DokkaiUtils`:
- `window.getUserId`
- `window.escapeHtml`
- `window.formatTime`
- `window.formatLocaleDate`
- `window.calculateScorePercent`

---

### 2.3. Мосты состояния монолита (`app.js`)

| Переменная | Назначение | Причина сохранения |
| :--- | :--- | :--- |
| `window.state` | Глобальное состояние приложения | Обеспечивает доступ модулей к объектам `state.timer`, `state.settings` в качестве fallback при неявной передаче аргументов |
| `window.elements` | Кэш DOM-элементов | Обеспечивает fallback для манипуляций с DOM внутри вынесенных модулей |

---

### 2.4. Устаревшие мосты для динамических HTML-шаблонов (`app.js`)

Следующие функции в настоящее время экспортируются на `window` внутри `app.js` исключительно потому, что вызываются через строковые `onclick="..."` в генерируемой HTML-верстке:

| Функция на `window` | Место генерации в HTML | Назначение |
| :--- | :--- | :--- |
| `openPretestModal` | `renderStreamSlots()` (`app.js:474, 487`) | Открытие предстартового окна по клику на карточку задания или кнопку |
| `fetchAndRenderSlots` | `renderStreamSlots()` (`app.js:499`) | Кнопка «Повторить» при пустых слотах или ошибке |
| `reviewSolvedTask` | `renderSolvedTasks()` (`app.js:601`) | Просмотр детального разбора решённого задания |
| `retrySolvedTask` | `renderSolvedTasks()` (`app.js:604`) | Повторное прохождение задания |
| `openReportModal` | `renderSolvedTasks()` (`app.js:607`) | Модальное окно отправки жалобы на опечатку/ошибку |
| `switchAnalysisTab` | `renderAnalysisView()` (`app.js:1300`) | Переключение табов вопросов на экране разбора |
| `locateEvidenceInText` | `renderAnalysisView()` (`app.js:1379`) | Подсветка доказательства в тексте по `evidence_span_id` |
| `saveDraft` | `renderDrafts()` (`app.js:2048`) | Сохранение черновика админки |
| `deleteDraft` | `renderDrafts()` (`app.js:2051`) | Удаление черновика админки |
| `publishDraft` | `renderDrafts()` (`app.js:2055`) | Публикация черновика админки |
| `markDraftCorrectOption` | `renderDraftQuestions()` (`app.js:2143`) | Выбор верного варианта ответа в редакторе черновика |

---

## 3. План ликвидации мостов в Шаге 6 (Event Delegation)

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

## 4. Контроль целостности и безопасность

1. **Anti-Cheat:**  
   Удаление функций с `window` гарантирует невозможность вызова внутренних управляющих методов напрямую из DevTools-консоли браузера или сторонними скриптами.
2. **Кэш Service Worker:**  
   Все модули, участвующие в декомпозиции, проверяются тестом графа импортов (`12_service_worker_integrity.spec.ts`) и автоматически синхронизируются со списком предкэширования.
3. **Регрессионное тестирование:**  
   Автоматизированные тесты Playwright (28/28 сьютов) проверяют все сценарии кликов и навигации, гарантируя отсутствие регрессий при переходе от inline `onclick` к `data-action`.
