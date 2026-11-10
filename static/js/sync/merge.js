/** Pure lossless union-merge rules for local vs Firestore state (Step 7c-2). No I/O. */

export function mergeSolvedTasks(remoteData, localSolved) {
    // A. Solved Tasks: union by text_id; higher score wins, or newer solved_at
    const mergedSolvedMap = {};
    if (remoteData && remoteData.solved_tasks) {
        Object.values(remoteData.solved_tasks).forEach(task => {
            if (task && task.text_id) mergedSolvedMap[task.text_id] = task;
        });
    }
    localSolved.forEach(localTask => {
        const existing = mergedSolvedMap[localTask.text_id];
        if (!existing) {
            mergedSolvedMap[localTask.text_id] = localTask;
        } else {
            const localScore = Number(localTask.score || 0);
            const existScore = Number(existing.score || 0);
            if (localScore > existScore) {
                mergedSolvedMap[localTask.text_id] = localTask;
            } else if (localScore === existScore) {
                const localTime = new Date(localTask.solved_at || 0).getTime();
                const remTime = new Date(existing.solved_at || 0).getTime();
                if (localTime >= remTime) {
                    mergedSolvedMap[localTask.text_id] = localTask;
                }
            }
        }
    });

    return mergedSolvedMap;
}

export function mergeNotebook(remoteData, localWords) {
    // B. Notebook Glossary: union by word; mastered is sticky, newest updated_at wins
    const mergedWordsMap = {};
    if (remoteData && remoteData.notebook) {
        Object.values(remoteData.notebook).forEach(w => {
            if (w && w.word) mergedWordsMap[w.word] = w;
        });
    }
    localWords.forEach(localW => {
        const existing = mergedWordsMap[localW.word];
        if (!existing) {
            mergedWordsMap[localW.word] = localW;
        } else {
            const isMastered = Boolean(localW.mastered || existing.mastered);
            const newestUpdate = Math.max(localW.updated_at || 0, existing.updated_at || 0);
            mergedWordsMap[localW.word] = {
                ...existing,
                ...localW,
                mastered: isMastered,
                updated_at: newestUpdate
            };
        }
    });

    return mergedWordsMap;
}
