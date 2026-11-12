import { useState, useEffect } from 'react';

/**
 * 4-7-8 breathing state machine.
 */
export function useBreathing() {
  const [breathPhase, setBreathPhase] = useState('Inhale');

  useEffect(() => {
    const breathCycle = () => {
      setBreathPhase('Inhale');
      setTimeout(() => {
        setBreathPhase('Hold');
        setTimeout(() => {
          setBreathPhase('Exhale');
        }, 7000);
      }, 4000);
    };
    breathCycle();
    const interval = setInterval(breathCycle, 19000);
    return () => clearInterval(interval);
  }, []);

  return breathPhase;
}
