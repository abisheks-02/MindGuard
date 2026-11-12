import client from './client';

export const analyzeText = (text) =>
  client.post('/analyze', { text }).then(r => r.data);

export const analyzeVoice = (formData) =>
  client.post('/analyze/voice', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(r => r.data);
