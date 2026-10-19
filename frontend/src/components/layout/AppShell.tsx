import React from 'react';
import { BottomNav } from './BottomNav';

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div
      className="app-shell"
      style={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100dvh',
        background: 'var(--color-bg)',
      }}
    >
      <main
        className="app-shell__content"
        style={{
          flex: 1,
          overflowY: 'auto',
          paddingBottom: 'calc(var(--nav-height) + var(--nav-safe-area) + 8px)',
        }}
      >
        {children}
      </main>
      <BottomNav />
    </div>
  );
}
