import React from 'react';
import { Avatar } from '@/components/ui/Avatar';
import type { User } from '@/types/user';

interface ProfileHeaderProps {
  user: User;
}

export function ProfileHeader({ user }: ProfileHeaderProps) {
  return (
    <div
      className="profile-header"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 'var(--space-3)',
        padding: 'var(--space-6) var(--space-4) var(--space-4)',
        textAlign: 'center',
        animation: 'scaleIn 0.3s ease forwards',
      }}
    >
      <Avatar src={user.photo_url} name={user.display_name} size={72} />
      <div>
        <h2
          style={{
            fontSize: 'var(--text-xl)',
            fontWeight: 800,
            color: 'var(--color-text-primary)',
            letterSpacing: '-0.02em',
            lineHeight: 1.2,
          }}
        >
          {user.display_name}
        </h2>
        {user.username && (
          <p
            style={{
              fontSize: 'var(--text-sm)',
              color: 'var(--color-text-tertiary)',
              fontFamily: 'var(--font-mono)',
              marginTop: 4,
            }}
          >
            @{user.username}
          </p>
        )}
      </div>
    </div>
  );
}
