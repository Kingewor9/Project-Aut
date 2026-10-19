export interface ChannelBrain {
  niche?: string;
  topics: string[];
  audience_description?: string;
  writing_personality?: string;
  post_formats: string[];
  content_strategy?: string;
  products_and_offers?: string;
  cta_library: string[];
  rules_and_restrictions?: string;
  goals?: string;
  extra: Record<string, unknown>;
  niches?: string[];
  audience?: ChannelAudience;
  conversion_goals?: string[];
  rules?: ChannelRules;
  content_types?: string[];
  frequency?: string;
  writing_dna?: WritingDNA;
  products?: ProductOffer[];
  ctas?: CTAConfig[];
  cta_enabled?: boolean;
  promotion_style?: string;
  max_promotions_per_week?: number;
}

export interface ChannelAudience {
  age_range?: string;
  location?: string;
  gender?: string;
  experience_level?: string;
  interests: string[];
  description?: string;
}

export interface ChannelRules {
  always_do: string[];
  never_do: string[];
  forbidden_topics: string[];
  forbidden_words: string[];
  custom_rules?: string;
}

export interface WritingDNA {
  mode: 'manual' | 'samples';
  tone: string[];
  personality: string[];
  vocabulary?: string;
  sentence_style?: string;
  paragraph_structure?: string;
  average_post_length?: string;
  hook_style?: string;
  formatting: string[];
  emoji_usage?: string;
  post_length?: string;
  cta_style?: string;
  advanced_instructions?: string;
  sample_posts: string[];
  style_analysis: Record<string, unknown>;
  style_analysis_status?: string;
}

export interface ProductOffer {
  name: string;
  description?: string;
  problem_solved?: string;
  target_audience?: string;
  price?: string;
  selling_points: string[];
  benefits: string[];
  proof?: string;
}

export interface CTAConfig {
  product_name?: string;
  type: string;
  telegram_username?: string;
  keyword?: string;
  destination_url?: string;
  instruction?: string;
}

export interface ChannelSchedule {
  timezone: string;
  posts_per_day: number;
  posting_times: string[];
  active_days: string[];
  daily_times?: Record<string, string[]>;
}

export type PublishMode = 'approval' | 'auto';
export type AutomationStatus = 'inactive' | 'active' | 'paused';

export interface UsageSummary {
  posts_generated: number;
  posts_published: number;
  posts_allowance: number;
  month_key: string;
}

export interface Channel {
  id: string;
  user_id: string;
  telegram_channel_id: string;
  username?: string;
  name: string;
  photo_url?: string;
  brain: ChannelBrain;
  schedule: ChannelSchedule;
  publish_mode: PublishMode;
  automation_status: AutomationStatus;
  is_bot_admin: boolean;
  is_active: boolean;
  usage?: UsageSummary;
  created_at: string;
  updated_at: string;
}

export interface TestGenerationResponse {
  content: string;
  remaining_tests: number;
}

export interface StyleAnalysisResponse extends WritingDNA {
  remaining_analyses: number;
}

export interface ChannelCreatePayload {
  telegram_channel_id: string;
}

export interface ChannelResolveResponse {
  telegram_channel_id: string;
  username?: string;
  name: string;
  photo_url?: string;
}
