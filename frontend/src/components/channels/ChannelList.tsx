import React from 'react';
import type { Channel } from '@/types/channel';
import { ChannelCard } from './ChannelCard';

interface ChannelListProps {
  channels: Channel[];
  className?: string;
}

export function ChannelList({ channels, className = '' }: ChannelListProps) {
  return (
    <div
      className={`channel-list stagger ${className}`}
      style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}
    >
      {channels.map((ch) => (
        <ChannelCard key={ch.id} channel={ch} />
      ))}
    </div>
  );
}
