import client from './client';
import type { Subscription, AllPlans } from '@/types/subscription';

export const subscriptionsApi = {
  getMy: (): Promise<Subscription> =>
    client.get<Subscription>('/subscriptions/me').then((r) => r.data),

  getPlans: (): Promise<AllPlans> =>
    client.get<AllPlans>('/subscriptions/plans').then((r) => r.data),

  changePlan: (plan_id: string, stars_invoice_id?: string): Promise<Subscription> =>
    client
      .post<Subscription>('/subscriptions/change-plan', { plan_id, stars_invoice_id })
      .then((r) => r.data),

  createInvoice: (plan_id: string): Promise<{ invoice_link: string; plan_id: string }> =>
    client.post('/subscriptions/invoice', { plan_id }).then((r) => r.data),

  createUsageCreditInvoice: (channel_id: string, usage_type: 'test_generation' | 'style_analysis'):
    Promise<{ invoice_link: string; usage_type: string; credits: number }> =>
    client.post('/subscriptions/usage-credit-invoice', { channel_id, usage_type }).then((r) => r.data),
};
