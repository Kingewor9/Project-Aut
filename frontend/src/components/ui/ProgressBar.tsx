import React from 'react';

interface ProgressBarProps {
  value: number; // 0–100
  max?: number;
  showLabel?: boolean;
  height?: number;
  className?: string;
}

function getColor(pct: number): string {
  if (pct < 60) return 'var(--usage-low)';
  if (pct < 85) return 'var(--usage-mid)';
  return 'var(--usage-high)';
}

export function ProgressBar({
  value,
  max = 100,
  showLabel = false,
  height = 6,
  className = '',
}: ProgressBarProps) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  const color = getColor(pct);

  return (
    <div className={`progress-bar-wrap ${className}`} style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      {showLabel && (
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            fontSize: 'var(--text-xs)',
            fontFamily: 'var(--font-mono)',
            color: 'var(--color-text-secondary)',
          }}
        >
          <span>{value}</span>
          <span>{max}</span>
        </div>
      )}
      <div
        style={{
          height,
          borderRadius: 999,
          background: 'var(--color-badge-bg)',
          overflow: 'hidden',
        }}
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={max}
      >
        <div
          style={{
            height: '100%',
            width: `${pct}%`,
            borderRadius: 999,
            background: color,
            transition: 'width 0.5s cubic-bezier(0.4, 0, 0.2, 1)',
          }}
        />
      </div>
    </div>
  );
}
