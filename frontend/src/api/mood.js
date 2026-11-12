import client from './client';

export const logMood = (sessionId, text, severity) =>
  client.post('/mood/log', { session_id: sessionId, text, severity }).then(r => r.data);

export const getMoodHistory = (sessionId) =>
  client.get(`/mood/history/${sessionId}`).then(r => r.data);

export const getWellnessPlan = (sessionId) =>
  client.get(`/mood/plan/${sessionId}`).then(r => r.data);

export const syncSocialMedia = (sessionId, username, platform) =>
  client.post('/mood/social/sync', { session_id: sessionId, username, platform }).then(r => r.data);
