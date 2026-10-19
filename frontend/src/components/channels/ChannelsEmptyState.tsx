import React from 'react';
import { Bot } from 'lucide-react';
import { EmptyState } from '@/components/ui/EmptyState';
import { NewChannelButton } from './NewChannelButton';

export function ChannelsEmptyState() {
  return (
    <EmptyState
      icon={<Bot size={32} />}
      title="No channels yet"
      description="Connect your first Telegram channel and let Automata handle your content on autopilot."
      action={<NewChannelButton />}
    />
  );
}
