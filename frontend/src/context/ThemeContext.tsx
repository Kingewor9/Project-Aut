import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { getColorScheme } from '@/lib/telegram';

type Theme = 'light' | 'dark';

interface ThemeContextValue {
  theme: Theme;
  setTheme: (t: Theme) => void;
}

const ThemeContext = createContext<ThemeContextValue>({
  theme: 'light',
  setTheme: () => undefined,
});

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(() => getColorScheme());

  const setTheme = (t: Theme) => {
    setThemeState(t);
    document.documentElement.setAttribute('data-theme', t);
  };

  useEffect(() => {
    // Apply initial theme from Telegram
    const initial = getColorScheme();
    document.documentElement.setAttribute('data-theme', initial);
    setThemeState(initial);

    // Listen for Telegram theme changes (if available)
    const tg = window.Telegram?.WebApp;
    if (!tg) return;

    // Poll for theme changes (Telegram doesn't expose a theme change event)
    const interval = setInterval(() => {
      const current = tg.colorScheme;
      setThemeState((prev) => {
        if (prev !== current) {
          document.documentElement.setAttribute('data-theme', current);
          return current;
        }
        return prev;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme(): ThemeContextValue {
  return useContext(ThemeContext);
}
