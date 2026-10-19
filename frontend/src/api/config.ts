import client from './client';

export interface PublicConfig {
  support_username: string;
  announce_channel: string;
  social_twitter: string;
  social_instagram: string;
  social_tiktok: string;
  social_website: string;
}

export const configApi = {
  getPublic: (): Promise<PublicConfig> =>
    client.get<PublicConfig>('/config').then((r) => r.data),
};
