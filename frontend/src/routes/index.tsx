import React, { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AppShell } from '@/components/layout/AppShell';

const ChannelsHomePage     = lazy(() => import('./ChannelsHomePage'));
const ChannelSettingsPage  = lazy(() => import('./ChannelSettingsPage'));
const NewChannelPage       = lazy(() => import('./NewChannelPage'));
const ChannelOnboardingPage = lazy(() => import('./ChannelOnboardingPage'));
const SettingsPage         = lazy(() => import('./SettingsPage'));
const PlansPage            = lazy(() => import('./PlansPage'));

function PageLoader() {
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '60dvh',
        color: 'var(--color-text-tertiary)',
        fontSize: 'var(--text-sm)',
      }}
    >
      <span style={{ opacity: 0.5 }}>Loading…</span>
    </div>
  );
}

export function AppRoutes() {
  return (
    <AppShell>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          {/* Channels */}
          <Route path="/"               element={<ChannelsHomePage />} />
          <Route path="/channels/new"   element={<NewChannelPage />} />
          <Route path="/channels/:id/onboarding" element={<ChannelOnboardingPage />} />
          <Route path="/channels/:id"   element={<ChannelSettingsPage />} />

          {/* Settings */}
          <Route path="/settings"       element={<SettingsPage />} />
          <Route path="/settings/plans" element={<PlansPage />} />

          {/* Catch-all */}
          <Route path="*"               element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </AppShell>
  );
}
