import { useState, useEffect, useCallback } from 'react';
import { getMoodHistory, getWellnessPlan, logMood, syncSocialMedia } from '../api/mood';
import { analyzeText } from '../api/analyze';

export function useMoodHistory(sessionId) {
  const [history, setHistory] = useState([]);
  const [wellnessPlan, setWellnessPlan] = useState('');
  const [isLogging, setIsLogging] = useState(false);
  const [isLoadingPlan, setIsLoadingPlan] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);

  const fetchHistory = useCallback(async () => {
    try {
      const data = await getMoodHistory(sessionId);
      setHistory(data);
    } catch (e) {
      console.error(e);
    }
  }, [sessionId]);

  const fetchPlan = useCallback(async () => {
    setIsLoadingPlan(true);
    try {
      const data = await getWellnessPlan(sessionId);
      setWellnessPlan(data.plan);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoadingPlan(false);
    }
  }, [sessionId]);

  useEffect(() => {
    fetchHistory();
    fetchPlan();
  }, [fetchHistory, fetchPlan]);

  const handleLogMood = async (text) => {
    if (!text.trim()) return;
    setIsLogging(true);
    try {
      const analyzeRes = await analyzeText(text);
      await logMood(sessionId, text, analyzeRes.predicted_class);
      await fetchHistory();
      fetchPlan();
    } catch (e) {
      console.error(e);
    } finally {
      setIsLogging(false);
    }
  };

  const handleSync = async (username, platform = 'Twitter') => {
    if (!username) return;
    setIsSyncing(true);
    try {
      await syncSocialMedia(sessionId, username, platform);
      await fetchHistory();
    } catch (e) {
      console.error(e);
    } finally {
      setIsSyncing(false);
    }
  };

  return {
    history, wellnessPlan, isLogging, isLoadingPlan, isSyncing,
    handleLogMood, handleSync, fetchHistory,
  };
}
