import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useStore = create(
  persist(
    (set) => ({
      // User Profile
      userId: 'demo_user_001',
      setUserId: (id) => set({ userId: id }),

      // Preferences
      language: 'en', // 'en', 'ta', 'tanglish'
      setLanguage: (lang) => set({ language: lang }),
      
      theme: 'light', // 'light', 'dark'
      toggleTheme: () => set((state) => ({ theme: state.theme === 'light' ? 'dark' : 'light' })),
      
      // Onboarding State
      onboardingComplete: false,
      completeOnboarding: () => set({ onboardingComplete: true }),

      // Consents
      consents: {
        support_messages: false,
        notify_trusted: false,
        research_data: false
      },
      updateConsents: (newConsents) => set((state) => ({ 
        consents: { ...state.consents, ...newConsents } 
      })),

      // Global Crisis State
      crisisModeActive: false,
      setCrisisMode: (active) => set({ crisisModeActive: active })
    }),
    {
      name: 'mindguard-storage',
    }
  )
);
