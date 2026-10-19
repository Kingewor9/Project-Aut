export type PlanId = 'free' | 'starter' | 'pro' | 'agency';
export type SubscriptionStatus = 'active' | 'expired' | 'cancelled' | 'pending';

export interface Subscription {
  plan_id: PlanId;
  plan_name: string;
  status: SubscriptionStatus;
  max_channels: number;
  posts_per_channel: number;
  max_post_characters: number;
  price_stars: number;
  price_label: string;
  features: string[];
  renews_at?: string;
  expires_at?: string;
}

export interface Plan {
  id: PlanId;
  name: string;
  max_channels: number;
  posts_per_channel: number;
  max_post_characters: number;
  price_stars: number;
  price_label: string;
  features: string[];
  is_current: boolean;
}

export interface AllPlans {
  plans: Plan[];
  current_plan_id: PlanId;
}
