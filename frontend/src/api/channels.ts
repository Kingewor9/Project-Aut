import client from './client';
import type {
  Channel,
  ChannelCreatePayload,
  ChannelResolveResponse,
  ChannelAudience,
  ChannelRules,
  ChannelSchedule,
  CTAConfig,
  ProductOffer,
  WritingDNA,
  ScheduledPost,
  TestGenerationResponse,
  StyleAnalysisResponse,
} from '@/types/channel';

export const channelsApi = {
  list: (): Promise<Channel[]> =>
    client.get<Channel[]>('/channels').then((r) => r.data),

  get: (id: string): Promise<Channel> =>
    client.get<Channel>(`/channels/${id}`).then((r) => r.data),

  create: (payload: ChannelCreatePayload): Promise<Channel> =>
    client.post<Channel>('/channels', payload).then((r) => r.data),

  resolve: (telegram_channel_id: string): Promise<ChannelResolveResponse> =>
    client.post<ChannelResolveResponse>('/channels/resolve', { telegram_channel_id }).then((r) => r.data),

  saveIdentity: (id: string, payload: {
    niches: string[];
    topics: string[];
    audience: ChannelAudience;
    conversion_goals: string[];
    rules: ChannelRules;
    frequency: string;
    schedule: ChannelSchedule;
  }): Promise<Channel> => client.put<Channel>(`/channels/${id}/onboarding/identity`, payload).then((r) => r.data),

  saveBrain: (id: string, payload: { writing_dna: WritingDNA; content_types: string[] }): Promise<Channel> =>
    client.put<Channel>(`/channels/${id}/onboarding/brain`, payload).then((r) => r.data),

  saveCta: (id: string, payload: {
    enabled: boolean;
    products: ProductOffer[];
    ctas: CTAConfig[];
    promotion_style?: string;
    max_promotions_per_week: number;
  }): Promise<Channel> => client.put<Channel>(`/channels/${id}/onboarding/cta`, payload).then((r) => r.data),

  activate: (id: string, publish_mode: 'approval' | 'auto'): Promise<Channel> =>
    client.post<Channel>(`/channels/${id}/onboarding/activate`, { publish_mode }).then((r) => r.data),

  analyzeStyle: (id: string, sample_posts: string[]): Promise<StyleAnalysisResponse> =>
    client.post<StyleAnalysisResponse>(`/channels/${id}/onboarding/analyze-style`, { sample_posts }).then((r) => r.data),

  testGeneration: (id: string, payload: { content_type: string; topic: string; context?: string }): Promise<TestGenerationResponse> =>
    client.post<TestGenerationResponse>(`/channels/${id}/onboarding/test-generation`, payload).then((r) => r.data),

  testGenerationFeedback: (id: string, feedback: string): Promise<void> =>
    client.post(`/channels/${id}/onboarding/test-generation/feedback`, { feedback }).then(() => undefined),

  update: (id: string, payload: Partial<Channel>): Promise<Channel> =>
    client.patch<Channel>(`/channels/${id}`, payload).then((r) => r.data),

  delete: (id: string): Promise<void> =>
    client.delete(`/channels/${id}`).then(() => undefined),
};

export const postsApi = {
  pending: (): Promise<ScheduledPost[]> =>
    client.get<ScheduledPost[]>('/posts/pending').then((r) => r.data),

  approve: (postId: string): Promise<ScheduledPost> =>
    client.post<ScheduledPost>(`/posts/${postId}/approve`).then((r) => r.data),

  decline: (postId: string): Promise<ScheduledPost> =>
    client.post<ScheduledPost>(`/posts/${postId}/decline`).then((r) => r.data),
};
