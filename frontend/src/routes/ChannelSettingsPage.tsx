import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, BookOpen, Trash2, Zap, PauseCircle, Info } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Avatar } from '@/components/ui/Avatar';
import { UsageIndicator } from '@/components/channels/UsageIndicator';
import { channelsApi } from '@/api/channels';
import { hapticImpact, hapticNotification } from '@/lib/telegram';
import { useChannels } from '@/hooks/useChannels';
import './ChannelSettingsPage.css';

export default function ChannelSettingsPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { channels, isLoading } = useChannels();
  const [isDeleting, setIsDeleting] = React.useState(false);

  const channel = channels.find((c) => c.id === id);

  const handleDelete = async () => {
    if (!id) return;
    if (!window.confirm('Remove this channel from Automata?')) return;
    setIsDeleting(true);
    hapticImpact('heavy');
    try {
      await channelsApi.delete(id);
      hapticNotification('success');
      navigate('/', { replace: true });
    } catch {
      hapticNotification('error');
      setIsDeleting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="channel-settings channel-settings--loading" aria-label="Loading">
        <div className="channel-settings__skeleton-header" />
        <div className="channel-settings__skeleton-body" />
      </div>
    );
  }

  if (!channel) {
    return (
      <div className="channel-settings channel-settings--not-found">
        <Info size={40} />
        <p>Channel not found</p>
        <Button variant="ghost" onClick={() => navigate('/')}>Go Back</Button>
      </div>
    );
  }

  const statusBadgeVariant =
    channel.automation_status === 'active'
      ? 'success'
      : channel.automation_status === 'paused'
      ? 'warning'
      : 'default';

  return (
    <div className="channel-settings">
      {/* Header */}
      <header className="channel-settings__header">
        <button
          className="channel-settings__back"
          onClick={() => { hapticImpact('light'); navigate(-1); }}
          aria-label="Go back"
        >
          <ArrowLeft size={20} />
        </button>
        <h1 className="channel-settings__title">Channel Settings</h1>
        <div style={{ width: 36 }} />
      </header>

      <div className="channel-settings__body">
        {/* Identity card */}
        <div className="channel-settings__identity">
          <Avatar src={channel.photo_url} name={channel.name} size={64} />
          <div>
            <h2 className="channel-settings__name">{channel.name}</h2>
            {channel.username && (
              <p className="channel-settings__handle">@{channel.username}</p>
            )}
            <div style={{ marginTop: 8 }}>
              <Badge variant={statusBadgeVariant as any}>
                {channel.automation_status === 'active' ? (
                  <Zap size={11} />
                ) : (
                  <PauseCircle size={11} />
                )}
                {channel.automation_status}
              </Badge>
            </div>
          </div>
        </div>

        <section className="channel-settings__section">
          <div className="channel-settings__teaching-card">
            <div className="channel-settings__teaching-icon" aria-hidden="true">
              <BookOpen size={20} />
            </div>
            <div className="channel-settings__teaching-copy">
              <strong>{channel.is_active ? 'Edit how your AI writes' : 'Continue teaching your AI'}</strong>
              <span>{channel.is_active ? 'Update your channel identity, writing style, CTAs, or publishing settings.' : 'Finish the four setup steps to activate your channel manager.'}</span>
            </div>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => navigate(`/channels/${channel.id}/onboarding`)}
              id="edit-ai-teaching-btn"
            >
              {channel.is_active ? 'Edit' : 'Continue'}
            </Button>
          </div>
        </section>

        {/* Usage */}
        {channel.usage && (
          <section className="channel-settings__section">
            <h3 className="channel-settings__section-title">Monthly Usage</h3>
            <div className="channel-settings__card">
              <UsageIndicator
                used={channel.usage.posts_generated}
                allowance={channel.usage.posts_allowance}
              />
              <p className="channel-settings__usage-note">
                {channel.usage.posts_published} posts published this month
              </p>
            </div>
          </section>
        )}

        {/* Info */}
        <section className="channel-settings__section">
          <h3 className="channel-settings__section-title">Details</h3>
          <div className="channel-settings__card channel-settings__details">
            <div className="detail-row">
              <span className="detail-label">Channel ID</span>
              <span className="detail-value">{channel.telegram_channel_id}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Publish Mode</span>
              <span className="detail-value">{channel.publish_mode}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Bot Admin</span>
              <span className="detail-value">{channel.is_bot_admin ? '✅ Yes' : '❌ No'}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Connected Since</span>
              <span className="detail-value">
                {new Date(channel.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        </section>

        {/* Danger zone */}
        <section className="channel-settings__section">
          <Button
            variant="danger"
            size="md"
            fullWidth
            leftIcon={<Trash2 size={16} />}
            isLoading={isDeleting}
            onClick={handleDelete}
            id="delete-channel-btn"
          >
            Remove Channel
          </Button>
        </section>
      </div>
    </div>
  );
}
