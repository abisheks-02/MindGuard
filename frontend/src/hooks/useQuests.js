import { useState, useEffect, useCallback } from 'react';
import { generateQuest, getQuests, completeQuest } from '../api/quest';

export function useQuests(sessionId) {
  const [quests, setQuests] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);

  const fetchQuests = useCallback(async () => {
    try {
      const data = await getQuests(sessionId);
      setQuests(data);
    } catch (e) {
      console.error(e);
    }
  }, [sessionId]);

  useEffect(() => {
    fetchQuests();
  }, [fetchQuests]);

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      await generateQuest(sessionId);
      await fetchQuests();
    } catch (e) {
      console.error(e);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleComplete = async (questId) => {
    try {
      await completeQuest(questId);
      await fetchQuests();
    } catch (e) {
      console.error(e);
    }
  };

  const pendingQuests = quests.filter(q => q.status === 'pending');
  const completedQuests = quests.filter(q => q.status === 'completed');

  return { pendingQuests, completedQuests, isGenerating, handleGenerate, handleComplete };
}
