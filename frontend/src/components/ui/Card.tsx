import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
  onClick?: () => void;
  hoverable?: boolean;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

const paddingMap = {
  none: '0',
  sm: 'var(--space-3) var(--space-4)',
  md: 'var(--space-4) var(--space-5)',
  lg: 'var(--space-6)',
};

export function Card({
  children,
  className = '',
  style,
  onClick,
  hoverable = false,
  padding = 'md',
}: CardProps) {
  return (
    <div
      className={['card', hoverable ? 'card--hoverable' : '', className].filter(Boolean).join(' ')}
      style={{
        background: 'var(--color-surface)',
        borderRadius: 'var(--radius-lg)',
        border: '1px solid var(--color-border)',
        boxShadow: 'var(--shadow-card)',
        padding: paddingMap[padding],
        transition: 'box-shadow var(--transition-fast), transform var(--transition-fast)',
        cursor: onClick ? 'pointer' : 'default',
        ...(hoverable && {
          '--hover-transform': 'translateY(-2px)',
        } as React.CSSProperties),
        ...style,
      }}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={onClick ? (e) => e.key === 'Enter' && onClick() : undefined}
    >
      {children}
    </div>
  );
}
