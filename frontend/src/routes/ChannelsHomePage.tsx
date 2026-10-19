import React from 'react';
import { useAuth } from '@/context/AuthContext';
import { useChannels } from '@/hooks/useChannels';
import { ChannelList } from '@/components/channels/ChannelList';
import { ChannelsEmptyState } from '@/components/channels/ChannelsEmptyState';
import { NewChannelButton } from '@/components/channels/NewChannelButton';
import { Bot, RefreshCw } from 'lucide-react';
import './ChannelsHomePage.css';

export default function ChannelsHomePage() {
  const { user } = useAuth();
  const { channels, isLoading, error, refetch } = useChannels();

  return (
    <div className="channels-home">
      {/* Header */}
      <header className="channels-home__header">
        <div>
          <h1 className="channels-home__title">My Channels</h1>
          {user && (
            <p className="channels-home__subtitle">
              Hi {user.first_name} 👋 — {channels.length} channel{channels.length !== 1 ? 's' : ''} connected
            </p>
          )}
        </div>
        {channels.length > 0 && <NewChannelButton compact />}
      </header>

      {/* Content */}
      <div className="channels-home__body">
        {isLoading && (
          <div className="channels-home__loading" aria-label="Loading channels">
            {[1, 2, 3].map((i) => (
              <div key={i} className="channel-skeleton" />
            ))}
          </div>
        )}

        {!isLoading && error && (
          <div className="channels-home__error">
            <Bot size={32} />
            <p>{error}</p>
            <button className="channels-home__retry" onClick={refetch}>
              <RefreshCw size={14} /> Try again
            </button>
          </div>
        )}

        {!isLoading && !error && channels.length === 0 && <ChannelsEmptyState />}

        {!isLoading && !error && channels.length > 0 && (
          <ChannelList channels={channels} />
        )}
      </div>
    </div>
  );
}
