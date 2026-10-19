/**
 * Telegram WebApp helpers.
 * Always access the WebApp through these helpers so the app doesn't break
 * when running outside Telegram (e.g. in a browser for dev).
 */
import type { TelegramWebApp, TelegramWebAppUser } from '@/types/telegram';

export function getTelegramWebApp(): TelegramWebApp | null {
  return window.Telegram?.WebApp ?? null;
}

export function isTelegram(): boolean {
  return Boolean(window.Telegram?.WebApp?.initData);
}

export function getInitData(): string {
  return window.Telegram?.WebApp?.initData ?? '';
}

export function getTelegramUser(): TelegramWebAppUser | null {
  return window.Telegram?.WebApp?.initDataUnsafe?.user ?? null;
}

export function getColorScheme(): 'light' | 'dark' {
  return window.Telegram?.WebApp?.colorScheme ?? 'light';
}

export function expandWebApp(): void {
  window.Telegram?.WebApp?.expand();
}

export function readyWebApp(): void {
  window.Telegram?.WebApp?.ready();
}

export function openExternalLink(url: string): void {
  const tg = getTelegramWebApp();
  if (tg) {
    tg.openLink(url);
  } else {
    window.open(url, '_blank', 'noopener noreferrer');
  }
}

export function openTelegramLink(url: string): void {
  const tg = getTelegramWebApp();
  if (tg) {
    tg.openTelegramLink(url);
  } else {
    window.open(url, '_blank', 'noopener noreferrer');
  }
}

export function openInvoice(url: string, callback: (status: string) => void): void {
  const tg = getTelegramWebApp();
  if (tg?.openInvoice) {
    tg.openInvoice(url, callback);
    return;
  }
  openExternalLink(url);
}

export function hapticImpact(style: 'light' | 'medium' | 'heavy' = 'light'): void {
  window.Telegram?.WebApp?.HapticFeedback?.impactOccurred(style);
}

export function hapticNotification(type: 'success' | 'error' | 'warning' = 'success'): void {
  window.Telegram?.WebApp?.HapticFeedback?.notificationOccurred(type);
}
