import client from './client';

export const generateQuest = (sessionId) =>
  client.post('/quest', { session_id: sessionId }).then(r => r.data);

export const getQuests = (sessionId) =>
  client.get(`/quests/${sessionId}`).then(r => r.data);

export const completeQuest = (questId) =>
  client.post('/quests/complete', { quest_id: questId }).then(r => r.data);
