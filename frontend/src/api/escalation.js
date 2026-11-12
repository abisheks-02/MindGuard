import client from './client';

export const triggerAlert = (text, severity) =>
  client.post('/alert', { text, severity }).then(r => r.data);

export const getHelplines = () =>
  client.get('/helplines').then(r => r.data);
