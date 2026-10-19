import React from 'react';
import { ProgressBar } from '@/components/ui/ProgressBar';

interface UsageIndicatorProps {
  used: number;
  allowance: number;
  className?: string;
}

export function UsageIndicator({ used, allowance, className = '' }: UsageIndicatorProps) {
  const pct = allowance > 0 ? Math.round((used / allowance) * 100) : 0;

  return (
    <div className={className} style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: 'var(--text-xs)',
          color: 'var(--color-text-tertiary)',
        }}
      >
        <span style={{ fontFamily: 'var(--font-mono)' }}>
          {used} / {allowance} posts
        </span>
        <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{pct}%</span>
      </div>
      <ProgressBar value={used} max={allowance} height={4} />
    </div>
  );
}
