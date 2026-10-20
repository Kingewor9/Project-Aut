/** Application-wide constants. */
const configuredApiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? '').replace(
  /\/+$/,
  ''
);

export const API_BASE_URL = configuredApiBaseUrl.endsWith('/api/v1')
  ? configuredApiBaseUrl
  : `${configuredApiBaseUrl}/api/v1`;

/** Plan metadata (mirrors backend config/plans.py — used for display only). */
export const PLAN_LABELS: Record<string, string> = {
  free: 'Free',
  starter: 'Starter',
  pro: 'Pro',
  agency: 'Agency',
};

/** Supported languages (extend as new translations are added). */
export const SUPPORTED_LANGUAGES = [
  { code: 'en', label: 'English' },
  // { code: 'fr', label: 'Français' },
  // { code: 'es', label: 'Español' },
] as const;
