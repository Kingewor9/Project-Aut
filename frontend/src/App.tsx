import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '@/context/ThemeContext';
import { AuthProvider } from '@/context/AuthContext';
import { AppRoutes } from '@/routes/index';
import { useAuth } from '@/context/AuthContext';
import { AlertCircle, RefreshCw } from 'lucide-react';

/** Inner component so we can read the auth context. */
function AppInner() {
  const { isLoading, error } = useAuth();

  if (isLoading) {
    return (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100dvh',
          gap: 16,
          color: 'var(--color-text-secondary)',
          background: 'var(--color-bg)',
        }}
      >
        <div
          style={{
            width: 40,
            height: 40,
            borderRadius: '50%',
            border: '3px solid var(--color-border)',
            borderTopColor: 'var(--color-accent)',
            animation: 'spin 0.7s linear infinite',
          }}
        />
        <p style={{ fontSize: 'var(--text-sm)' }}>Initializing Automata…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100dvh',
          gap: 16,
          padding: 24,
          textAlign: 'center',
          background: 'var(--color-bg)',
          color: 'var(--color-text-secondary)',
        }}
      >
        <AlertCircle size={40} color="var(--color-danger)" />
        <p style={{ fontSize: 'var(--text-base)', fontWeight: 600 }}>
          {error}
        </p>
        <button
          onClick={() => window.location.reload()}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 8,
            padding: '10px 20px',
            background: 'var(--color-accent)',
            color: '#fff',
            border: 'none',
            borderRadius: 'var(--radius-full)',
            fontSize: 'var(--text-sm)',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          <RefreshCw size={14} />
          Try again
        </button>
      </div>
    );
  }

  return <AppRoutes />;
}

export default function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <AppInner />
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}
