import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowUpRight, Sparkles } from 'lucide-react';
import type { Subscription } from '@/types/subscription';
import { Badge } from '@/components/ui/Badge';
import { hapticImpact } from '@/lib/telegram';

interface PlanSummaryCardProps {
  subscription: Subscription;
}

export function PlanSummaryCard({ subscription }: PlanSummaryCardProps) {
  const navigate = useNavigate();
  const isFree = subscription.plan_id === 'free';

  return (
    <div
      style={{
        background: 'var(--color-upgrade-bg)',
        borderRadius: 'var(--radius-lg)',
        padding: 'var(--space-5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 'var(--space-3)',
        cursor: isFree ? 'pointer' : 'default',
        animation: 'fadeIn 0.35s ease forwards',
      }}
      onClick={
        isFree
          ? () => {
              hapticImpact('medium');
              navigate('/settings/plans');
            }
          : undefined
      }
      role={isFree ? 'button' : undefined}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Sparkles size={16} color="#fff" strokeWidth={2} />
          <span
            style={{
              fontSize: 'var(--text-xs)',
              fontWeight: 700,
              color: 'rgba(255,255,255,0.75)',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
            }}
          >
            Current Plan
          </span>
        </div>
        <span
          style={{
            fontSize: 'var(--text-xl)',
            fontWeight: 800,
            color: '#fff',
            letterSpacing: '-0.02em',
          }}
        >
          {subscription.plan_name}
        </span>
        <span style={{ fontSize: 'var(--text-xs)', color: 'rgba(255,255,255,0.65)' }}>
          {subscription.max_channels} channels · {subscription.posts_per_channel} posts/mo
        </span>
      </div>

      {isFree ? (
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'flex-end',
            gap: 6,
            flexShrink: 0,
          }}
        >
          <Badge variant="default">Upgrade</Badge>
          <ArrowUpRight size={18} color="rgba(255,255,255,0.8)" />
        </div>
      ) : (
        <Badge variant="success">{subscription.status}</Badge>
      )}
    </div>
  );
}
