import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Plus, AlertCircle, CheckCircle2, Search } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Avatar } from '@/components/ui/Avatar';
import { channelsApi } from '@/api/channels';
import type { ChannelResolveResponse } from '@/types/channel';
import { hapticImpact, hapticNotification } from '@/lib/telegram';
import './NewChannelPage.css';

export default function NewChannelPage() {
  const navigate = useNavigate();
  const [channelId, setChannelId] = useState('');
  const [resolvedChannel, setResolvedChannel] = useState<ChannelResolveResponse | null>(null);
  const [isResolving, setIsResolving] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const resolveChannel = async () => {
    const value = channelId.trim();
    if (!value || isResolving) return null;

    setIsResolving(true);
    setError(null);
    try {
      const channel = await channelsApi.resolve(value);
      setResolvedChannel(channel);
      return channel;
    } catch (err) {
      setResolvedChannel(null);
      setError(err instanceof Error ? err.message : 'Could not find that Telegram channel');
      return null;
    } finally {
      setIsResolving(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!channelId.trim()) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const channel = resolvedChannel ?? await resolveChannel();
      if (!channel) {
        setIsSubmitting(false);
        return;
      }
      const ch = await channelsApi.create({
        telegram_channel_id: channel.telegram_channel_id,
      });
      hapticNotification('success');
      navigate(`/channels/${ch.id}/onboarding`, { replace: true });
    } catch (err) {
      hapticNotification('error');
      setError(err instanceof Error ? err.message : 'Failed to connect channel');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="new-channel-page">
      <header className="new-channel-page__header">
        <button
          className="new-channel-page__back"
          onClick={() => {
            hapticImpact('light');
            navigate(-1);
          }}
          aria-label="Go back"
        >
          <ArrowLeft size={20} />
        </button>
        <h1 className="new-channel-page__title">Connect Channel</h1>
        <div style={{ width: 36 }} />
      </header>

      <div className="new-channel-page__body">
        <div className="new-channel-page__instructions">
          <p className="new-channel-page__step">
            <span className="step-num">1</span>
            Add <strong>@AutomataTGBot</strong> as an admin of your Telegram channel.
          </p>
          <p className="new-channel-page__step">
            <span className="step-num">2</span>
            Enter your channel ID (e.g. <code>-100123456789</code>) or username below.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="new-channel-page__form">
          <div className="form-group">
            <label htmlFor="channel-id" className="form-label">Channel ID or Username</label>
            <input
              id="channel-id"
              type="text"
              className="form-input"
              placeholder="-100123456789 or @mychannel"
              value={channelId}
              onChange={(e) => {
                setChannelId(e.target.value);
                setResolvedChannel(null);
                setError(null);
              }}
              onBlur={() => void resolveChannel()}
              required
              autoComplete="off"
            />
          </div>

          {isResolving && (
            <div className="channel-preview channel-preview--loading">
              <span className="channel-preview__spinner" />
              <span>Finding your channel...</span>
            </div>
          )}

          {resolvedChannel && !isResolving && (
            <div className="channel-preview">
              <Avatar src={resolvedChannel.photo_url} name={resolvedChannel.name} size={52} />
              <div className="channel-preview__details">
                <strong>{resolvedChannel.name}</strong>
                <span>{resolvedChannel.username ? `@${resolvedChannel.username.replace(/^@/, '')}` : resolvedChannel.telegram_channel_id}</span>
              </div>
              <CheckCircle2 className="channel-preview__check" size={20} aria-label="Channel found" />
            </div>
          )}

          {error && (
            <div className="form-error">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          <Button
            type="submit"
            variant="primary"
            size="lg"
            fullWidth
            isLoading={isSubmitting}
            leftIcon={resolvedChannel ? <Plus size={18} /> : <Search size={18} />}
            id="submit-new-channel"
          >
            {resolvedChannel ? 'Continue setup' : 'Find channel'}
          </Button>
        </form>
      </div>
    </div>
  );
}
