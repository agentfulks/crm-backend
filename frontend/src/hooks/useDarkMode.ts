import { useEffect, useState } from 'react';

const STORAGE_KEY = 'crm-dark-mode';

/**
 * Manages dark mode state, persisted to localStorage.
 * Toggles the `dark` class on <html> so Tailwind's class strategy works.
 * Falls back to the user's OS preference on first visit.
 */
export function useDarkMode() {
  const [isDark, setIsDark] = useState<boolean>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved !== null) return saved === 'true';
      // Fall back to OS preference
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    } catch {
      return false;
    }
  });

  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    try {
      localStorage.setItem(STORAGE_KEY, String(isDark));
    } catch {
      // localStorage unavailable — silently ignore
    }
  }, [isDark]);

  return {
    isDark,
    toggle: () => setIsDark((d) => !d),
  };
}
