import React from 'react';
import { ChevronRight } from 'lucide-react';
import { hapticImpact } from '@/lib/telegram';

interface SettingsListItemProps {
  icon: React.ReactNode;
  label: string;
  value?: string;
  onClick?: () => void;
  danger?: boolean;
  rightElement?: React.ReactNode;
  id?: string;
}

export function SettingsListItem({
  icon,
  label,
  value,
  onClick,
  danger = false,
  rightElement,
  id,
}: SettingsListItemProps) {
  const handleClick = onClick
    ? () => {
        hapticImpact('light');
        onClick();
      }
    : undefined;

  return (
    <div
      id={id}
      className="settings-list-item"
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onClick={handleClick}
      onKeyDown={handleClick ? (e) => e.key === 'Enter' && handleClick() : undefined}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--space-3)',
        padding: 'var(--space-4)',
        background: 'var(--color-surface)',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'background var(--transition-fast)',
        WebkitTapHighlightColor: 'transparent',
      }}
    >
      <span
        style={{
          width: 32,
          height: 32,
          borderRadius: 'var(--radius-sm)',
          background: danger ? 'rgba(255, 59, 48, 0.12)' : 'var(--color-accent-subtle)',
          color: danger ? 'var(--color-danger)' : 'var(--color-accent)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        }}
      >
        {icon}
      </span>

      <span
        style={{
          flex: 1,
          fontSize: 'var(--text-base)',
          fontWeight: 500,
          color: danger ? 'var(--color-danger)' : 'var(--color-text-primary)',
        }}
      >
        {label}
      </span>

      {value && (
        <span
          style={{
            fontSize: 'var(--text-sm)',
            color: 'var(--color-text-tertiary)',
            fontFamily: 'var(--font-mono)',
          }}
        >
          {value}
        </span>
      )}

      {rightElement ?? (onClick ? (
        <ChevronRight size={16} style={{ color: 'var(--color-text-tertiary)', flexShrink: 0 }} />
      ) : null)}
    </div>
  );
}
