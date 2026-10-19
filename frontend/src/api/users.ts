import client from './client';
import type { User } from '@/types/user';

export const usersApi = {
  getMe: (): Promise<User> =>
    client.get<User>('/users/me').then((r) => r.data),

  updateLanguage: (language_code: string): Promise<User> =>
    client.patch<User>('/users/me/language', { language_code }).then((r) => r.data),
};
