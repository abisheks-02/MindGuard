/**
 * Encapsulates the full analyze → chat → alert flow.
 */
import { useState } from 'react';
import { analyzeText } from '../api/analyze';
import { sendChat } from '../api/chat';
import { triggerAlert } from '../api/escalation';

export function useAnalysis() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [chatResponse, setChatResponse] = useState('');
  const [alertMessage, setAlertMessage] = useState(null);

  const runAnalysis = async (text) => {
    if (!text.trim()) return;
    setIsAnalyzing(true);
    setResult(null);
    setChatResponse('');
    setAlertMessage(null);

    try {
      const data = await analyzeText(text);

      // Slight delay for UX
      setTimeout(async () => {
        setResult(data);
        setIsAnalyzing(false);

        try {
          const chatRes = await sendChat(text, data.predicted_class);
          setChatResponse(chatRes.response);
        } catch (e) {
          console.error(e);
        }

        if (data.predicted_class === 'Severe') {
          try {
            const alertRes = await triggerAlert(text, 'Severe');
            setAlertMessage(alertRes.dispatched_message);
          } catch (e) {
            console.error(e);
          }
        }
      }, 800);
    } catch (e) {
      console.error(e);
      setIsAnalyzing(false);
    }
  };

  return { isAnalyzing, result, chatResponse, alertMessage, runAnalysis, setResult };
}
