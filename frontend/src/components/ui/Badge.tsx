import React from 'react';

type BadgeVariant = 'default' | 'success' | 'warning' | 'danger' | 'accent';

interface BadgeProps {
  variant?: BadgeVariant;
  children: React.ReactNode;
  className?: string;
}

const variantStyles: Record<BadgeVariant, React.CSSProperties> = {
  default: {
    background: 'var(--color-badge-bg)',
    color: 'var(--color-badge-text)',
  },
  success: {
    background: 'rgba(52, 199, 89, 0.14)',
    color: '#34C759',
  },
  warning: {
    background: 'rgba(255, 159, 10, 0.14)',
    color: '#FF9F0A',
  },
  danger: {
    background: 'rgba(255, 59, 48, 0.14)',
    color: '#FF3B30',
  },
  accent: {
    background: 'var(--color-accent-subtle)',
    color: 'var(--color-accent)',
  },
};

export function Badge({ variant = 'default', children, className = '' }: BadgeProps) {
  return (
    <span
      className={`badge ${className}`}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '4px',
        padding: '3px 8px',
        borderRadius: 'var(--radius-full)',
        fontSize: 'var(--text-xs)',
        fontWeight: 600,
        letterSpacing: '0.02em',
        lineHeight: 1.4,
        ...variantStyles[variant],
      }}
    >
      {children}
    </span>
  );
}
