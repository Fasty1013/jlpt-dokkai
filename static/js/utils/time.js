/**
 * JLPT Dokkai Master - Time & Date Formatting Utilities
 */

export function formatTime(totalSeconds) {
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

export function formatLocaleDate(dateInput) {
    if (!dateInput) return '';
    try {
        const d = new Date(dateInput);
        return d.toLocaleDateString('ru-RU', {
            day: 'numeric',
            month: 'short',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (e) {
        return '';
    }
}
