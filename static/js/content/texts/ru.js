/**
 * JLPT Dokkai Master - Localized UI Texts (Russian)
 */

export const UI_TEXTS = {
    common: {
        loading: 'Загрузка...',
        retry: 'Повторить попытку',
        error: 'Произошла ошибка',
        close: 'Закрыть',
        done: 'Готово',
        cancel: 'Отмена',
        serverWaking: 'Сервер просыпается, подождите до минуты…'
    },
    catalog: {
        slotTitlePlaceholder: 'Готовится новое задание...',
        slotDescPlaceholder: (profileKey) => `Для профиля ${profileKey} генерируется или подбирается оригинальный учебный материал.`,
        loadSlotsError: 'Не удалось загрузить активные задания.',
        retryCatalog: '🔄 Повторить попытку',
        startSolving: 'Начать решение →',
        minutesShort: (min) => `${min} мин`,
        questionsShort: (count) => `${count} вопр.`,
        emptySolvedTitle: 'Здесь будут сохраняться решённые вами задания.',
        emptySolvedHint: 'Выберите любое задание из левой колонки «Задания», чтобы начать!',
        loadSolvedError: 'Не удалось загрузить архив решённых заданий.',
        reviewBreakdown: '🔍 Обзор разбора',
        retryTask: '🔁 Пройти заново',
        reportIssue: '⚠️ Сообщить об ошибке',
        badgePerfect: '100% ★ Идеально',
        badgeErrors: (score) => `${score}% с ошибками`
    },
    timer: {
        freeReadingMode: 'Свободное чтение (без таймера)',
        timeSpent: 'Затрачено времени: ',
        timerPaused: 'Пауза',
        timerRunning: 'Таймер идёт'
    },
    wizard: {
        nextQuestion: 'Следующий вопрос →',
        prevQuestion: '← Предыдущий',
        finishTest: 'Завершить тест и проверить →',
        finishFreeReading: 'Завершить чтение и проверить →',
        interruptTest: 'Прервать тест',
        interruptConfirm: 'Вы уверены, что хотите прервать решение? Незавершённые ответы будут сброшены.',
        questionOf: (curr, total) => `Вопрос ${curr} из ${total}`
    },
    analysis: {
        title: 'Результаты и подробный разбор',
        perfectSummary: 'Великолепно! Все ответы верны. Вы уверенно понимаете структуру текста и логику вопросов.',
        errorsSummary: 'Есть над чем поработать. Изучите подсвеченные доказательства в тексте и ловушки в неверных вариантах.',
        yourAnswer: 'Ваш ответ',
        correctAnswer: 'Правильный ответ',
        evidenceBtn: '🔍 Показать доказательство в тексте',
        tabQuestion: (num) => `Вопрос ${num}`
    },
    sync: {
        localTitle: 'Сохранение на этом устройстве',
        localDesc: 'Все данные надёжно сохраняются на этом устройстве (IndexedDB). Они не пропадут при закрытии вкладки или перезапуске сервера Render.',
        syncedTitle: 'В облаке',
        syncedDesc: 'Все решённые задания, личный словарь и настройки синхронизированы с Google Firebase ($0 бесплатно).',
        syncingTitle: 'Синхронизация...',
        syncingDesc: 'Идёт синхронизация данных с облаком...',
        offlineTitle: 'Офлайн',
        offlineDesc: 'Сеть недоступна. Все данные сохраняются на вашем устройстве (IndexedDB) и синхронизируются при включении интернета.',
        errorTitle: 'Ошибка синхронизации',
        errorDesc: (err) => err ? `Ошибка синхронизации: ${err}` : 'Ошибка соединения с облаком. Данные надёжно сохранены на устройстве.',
        connectGoogle: 'Подключение к Google...',
        createAnon: 'Создание анонимного облачного профиля...',
        signoutConfirm: 'Выйти из облачного аккаунта? Все локальные данные на этом устройстве сохранятся.',
        signoutSuccess: 'Вы вышли из облачного аккаунта. Локальные данные сохранены.',
        importSuccess: (solvedCount, wordsCount) => `Успешно импортировано: ${solvedCount} решённых заданий, ${wordsCount} слов в словаре!`,
        importError: (err) => `Ошибка при импорте файла: ${err || 'неверный формат'}`
    },
    notebook: {
        emptyList: 'Ваш личный словарь пока пуст.',
        emptyHint: 'Выделяйте незнакомые слова прямо в тексте или нажимайте на них для перевода и сохранения в словарь.',
        tabAll: 'Все слова',
        tabLearning: 'Изучаю',
        tabMastered: 'Выучено',
        deleteWordConfirm: (word) => `Удалить слово «${word}» из словаря?`
    }
};
