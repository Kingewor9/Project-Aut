import { useCallback, useEffect, useState } from 'react';
import { channelsApi } from '@/api/channels';
import type { Channel } from '@/types/channel';

interface UseChannelsResult {
  channels: Channel[];
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useChannels(): UseChannelsResult {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchChannels = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await channelsApi.list();
      setChannels(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load channels');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchChannels();
  }, [fetchChannels]);

  return { channels, isLoading, error, refetch: fetchChannels };
}
