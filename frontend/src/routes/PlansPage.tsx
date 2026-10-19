import React, { useState } from 'react';
import { ArrowLeft, Check, Crown, Sparkles, Zap } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { usePlan } from '@/hooks/usePlan';
import { subscriptionsApi } from '@/api/subscriptions';
import { Badge } from '@/components/ui/Badge';
import { hapticImpact, hapticNotification, openInvoice } from '@/lib/telegram';
import './PlansPage.css';

const icons = { free: Zap, starter: Sparkles, pro: Crown, agency: Crown } as const;

export default function PlansPage() {
  const navigate = useNavigate();
  const { allPlans, isLoading, refetch } = usePlan();
  const [busyPlan, setBusyPlan] = useState<string | null>(null);

  async function selectPlan(planId: string, isCurrent: boolean) {
    if (isCurrent || planId === 'free') return;
    setBusyPlan(planId);
    hapticImpact('medium');
    try {
      const { invoice_link } = await subscriptionsApi.createInvoice(planId);
      openInvoice(invoice_link, (status) => {
        if (status === 'paid') {
          hapticNotification('success');
          refetch();
        } else if (status === 'failed' || status === 'cancelled') {
          hapticNotification('warning');
        }
        setBusyPlan(null);
      });
    } catch {
      hapticNotification('error');
      setBusyPlan(null);
    }
  }

  return (
    <div className="plans-page">
      <header className="plans-page__header">
        <button className="plans-page__back" onClick={() => navigate(-1)} aria-label="Back">
          <ArrowLeft size={19} />
        </button>
        <div>
          <p className="plans-page__eyebrow">Automata TG</p>
          <h1>Choose your plan</h1>
        </div>
      </header>
      <p className="plans-page__intro">Give your channels more room to publish, grow, and stay consistent.</p>

      {isLoading ? <div className="plans-page__loading">Loading plans...</div> : (
        <div className="plans-page__list stagger">
          {allPlans?.plans.map((plan) => {
            const Icon = icons[plan.id];
            const isBusy = busyPlan === plan.id;
            return (
              <article className={`plan-card ${plan.is_current ? 'plan-card--current' : ''} ${plan.id === 'pro' ? 'plan-card--featured' : ''}`} key={plan.id}>
                {plan.id === 'pro' && <span className="plan-card__ribbon">Most popular</span>}
                <div className="plan-card__topline">
                  <span className="plan-card__icon"><Icon size={18} /></span>
                  {plan.is_current && <Badge variant="success">Current</Badge>}
                </div>
                <div className="plan-card__title-row">
                  <h2>{plan.name}</h2>
                  <div className="plan-card__price">
                    <strong>{plan.price_stars === 0 ? 'Free' : plan.price_stars.toLocaleString()}</strong>
                    {plan.price_stars > 0 && <span>Stars / month</span>}
                  </div>
                </div>
                <div className="plan-card__limits">
                  <span>{plan.max_channels} {plan.max_channels === 1 ? 'channel' : 'channels'}</span>
                  <span>{plan.posts_per_channel} posts / channel</span>
                  <span>{plan.max_post_characters.toLocaleString()} characters / post</span>
                </div>
                <ul>{plan.features.map((feature) => <li key={feature}><Check size={15} />{feature}</li>)}</ul>
                <button className="plan-card__button" disabled={plan.is_current || isBusy} onClick={() => selectPlan(plan.id, plan.is_current)}>
                  {plan.is_current ? 'Your current plan' : isBusy ? 'Opening payment...' : `Choose ${plan.name}`}
                </button>
              </article>
            );
          })}
        </div>
      )}
      <p className="plans-page__note">Payments are handled securely through Telegram Stars. Subscriptions renew monthly.</p>
    </div>
  );
}