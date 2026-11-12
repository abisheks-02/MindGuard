import client from './client';

export const sendChat = (text, severity, sessionId = 'demo_user_001') =>
  client.post('/chat', { text, severity, session_id: sessionId }).then(r => r.data);
