/** Human-readable (ru) translation of Firebase Auth/Firestore errors (Step 7c-2). */

export function translateFirebaseError(err) {
    if (!err) return 'Неизвестная ошибка';
    const code = err.code || '';
    const msg = err.message || '';

    switch (code) {
        case 'auth/popup-blocked':
            return 'Всплывающее окно входа заблокировано браузером. Перенаправляем на страницу авторизации Google...';
        case 'auth/popup-closed-by-user':
            return 'Окно входа было закрыто до завершения авторизации.';
        case 'auth/cancelled-popup-request':
            return 'Запрос авторизации был заменён новым окном.';
        case 'auth/unauthorized-domain':
            return 'Домен сайта не авторизован в настройках безопасности Firebase.';
        case 'auth/network-request-failed':
            return 'Нет подключения к интернету. Прогресс сохраняется локально на устройстве.';
        case 'auth/credential-already-in-use':
            return 'Этот Google-аккаунт уже привязан к другому пользователю. Выполняется объединение данных...';
        case 'permission-denied':
            return 'Ошибка прав доступа (permission-denied) к базе Firestore.';
        case 'auth/user-disabled':
            return 'Данный аккаунт отключён администратором.';
        case 'auth/operation-not-allowed':
            return 'Этот метод входа отключён в панели управления Firebase.';
        default:
            if (msg.includes('network') || msg.includes('Failed to fetch')) {
                return 'Нет подключения к сети. Прогресс сохраняется на устройстве.';
            }
            return msg || 'Ошибка облачной синхронизации.';
    }
}
