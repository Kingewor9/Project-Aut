import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Globe, CreditCard, HelpCircle, LogOut, Info } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { usePlan } from '@/hooks/usePlan';
import { ProfileHeader } from '@/components/settings/ProfileHeader';
import { PlanSummaryCard } from '@/components/settings/PlanSummaryCard';
import { SettingsListItem } from '@/components/settings/SettingsListItem';
import { SocialLinksRow } from '@/components/settings/SocialLinksRow';
import './SettingsPage.css';

export default function SettingsPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { subscription, isLoading: planLoading } = usePlan();

  return (
    <div className="settings-page">
      {/* Profile */}
      {user && <ProfileHeader user={user} />}

      {/* Plan */}
      <section className="settings-page__section">
        {planLoading ? (
          <div className="settings-page__plan-skeleton" aria-label="Loading plan" />
        ) : subscription ? (
          <PlanSummaryCard subscription={subscription} />
        ) : null}
      </section>

      {/* General settings */}
      <section className="settings-page__section">
        <h2 className="settings-page__section-label">General</h2>
        <div className="settings-page__group">
          <SettingsListItem
            id="settings-language"
            icon={<Globe size={16} />}
            label="Language"
            value="English"
          />
          <SettingsListItem
            id="settings-subscription"
            icon={<CreditCard size={16} />}
            label="Subscription"
            value={subscription?.plan_name ?? '—'}
            onClick={() => navigate('/settings/plans')}
          />
        </div>
      </section>

      {/* Support */}
      <section className="settings-page__section">
        <h2 className="settings-page__section-label">Support</h2>
        <SocialLinksRow />
      </section>

      {/* About */}
      <section className="settings-page__section">
        <h2 className="settings-page__section-label">About</h2>
        <div className="settings-page__group">
          <SettingsListItem
            id="settings-about"
            icon={<Info size={16} />}
            label="Version"
            value="1.0.0"
          />
          <SettingsListItem
            id="settings-help"
            icon={<HelpCircle size={16} />}
            label="Help & FAQ"
            onClick={() => {}}
          />
        </div>
      </section>

      <p className="settings-page__footer">
        Automata TG · AI-Powered Telegram Channel Manager
      </p>
    </div>
  );
}
