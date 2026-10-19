import { isTelegram, getTelegramUser } from '@/lib/telegram';
import type { TelegramWebAppUser } from '@/types/telegram';

/**
 * Returns whether the app is running inside Telegram and the raw Telegram user.
 * For the full authenticated user model, use `useAuth()` instead.
 */
export function useTelegramAuth(): {
  isTelegramEnv: boolean;
  telegramUser: TelegramWebAppUser | null;
} {
  return {
    isTelegramEnv: isTelegram(),
    telegramUser: getTelegramUser(),
  };
}
