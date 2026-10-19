import React from 'react';
import { openTelegramLink, openExternalLink } from '@/lib/telegram';

interface SocialLink {
  id: string;
  label: string;
  href: string;
  isTelegram?: boolean;
  emoji: string;
}

const SOCIAL_LINKS: SocialLink[] = [
  {
    id: 'tg-channel',
    label: 'Telegram Channel',
    href: 'https://t.me/automata_tg',
    isTelegram: true,
    emoji: '📢',
  },
  {
    id: 'tg-support',
    label: 'Support',
    href: 'https://t.me/automata_support',
    isTelegram: true,
    emoji: '💬',
  },
];

export function SocialLinksRow() {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--space-3)',
      }}
    >
      {SOCIAL_LINKS.map((link) => (
        <button
          key={link.id}
          id={link.id}
          onClick={() =>
            link.isTelegram
              ? openTelegramLink(link.href)
              : openExternalLink(link.href)
          }
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-3)',
            padding: 'var(--space-3) var(--space-4)',
            background: 'var(--color-surface)',
            border: '1px solid var(--color-border)',
            borderRadius: 'var(--radius-md)',
            cursor: 'pointer',
            textAlign: 'left',
            width: '100%',
            transition: 'background var(--transition-fast)',
            fontFamily: 'var(--font-sans)',
          }}
        >
          <span style={{ fontSize: 20 }}>{link.emoji}</span>
          <span
            style={{
              fontSize: 'var(--text-base)',
              fontWeight: 500,
              color: 'var(--color-text-primary)',
            }}
          >
            {link.label}
          </span>
        </button>
      ))}
    </div>
  );
}
