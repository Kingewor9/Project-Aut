import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronRight, Zap, PauseCircle, CheckCircle2 } from 'lucide-react';
import type { Channel } from '@/types/channel';
import { Avatar } from '@/components/ui/Avatar';
import { Badge } from '@/components/ui/Badge';
import { UsageIndicator } from './UsageIndicator';
import { hapticImpact } from '@/lib/telegram';
import './ChannelCard.css';

interface ChannelCardProps {
  channel: Channel;
}

const STATUS_CONFIG = {
  active:   { label: 'Active',   variant: 'success',  icon: <Zap size={11} /> },
  paused:   { label: 'Paused',   variant: 'warning',  icon: <PauseCircle size={11} /> },
  inactive: { label: 'Inactive', variant: 'default',  icon: <CheckCircle2 size={11} /> },
} as const;

export function ChannelCard({ channel }: ChannelCardProps) {
  const navigate = useNavigate();
  const status = STATUS_CONFIG[channel.automation_status];

  const handleClick = () => {
    hapticImpact('light');
    navigate(`/channels/${channel.id}`);
  };

  return (
    <article
      className="channel-card"
      onClick={handleClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && handleClick()}
      aria-label={`Open ${channel.name} settings`}
    >
      <div className="channel-card__left">
        <Avatar src={channel.photo_url} name={channel.name} size={48} />
        <div className="channel-card__info">
          <div className="channel-card__name-row">
            <span className="channel-card__name truncate">{channel.name}</span>
            <Badge variant={status.variant as any}>
              {status.icon}
              {status.label}
            </Badge>
          </div>
          {channel.username && (
            <span className="channel-card__handle truncate">@{channel.username}</span>
          )}
          {channel.usage && (
            <UsageIndicator
              used={channel.usage.posts_generated}
              allowance={channel.usage.posts_allowance}
            />
          )}
        </div>
      </div>
      <ChevronRight size={16} className="channel-card__chevron" />
    </article>
  );
}
