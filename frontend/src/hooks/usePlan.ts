import { useCallback, useEffect, useState } from 'react';
import { subscriptionsApi } from '@/api/subscriptions';
import type { Subscription, AllPlans } from '@/types/subscription';

interface UsePlanResult {
  subscription: Subscription | null;
  allPlans: AllPlans | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function usePlan(): UsePlanResult {
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [allPlans, setAllPlans] = useState<AllPlans | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPlan = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [sub, plans] = await Promise.all([
        subscriptionsApi.getMy(),
        subscriptionsApi.getPlans(),
      ]);
      setSubscription(sub);
      setAllPlans(plans);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load plan info');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPlan();
  }, [fetchPlan]);

  return { subscription, allPlans, isLoading, error, refetch: fetchPlan };
}
