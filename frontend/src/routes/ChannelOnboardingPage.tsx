import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  ArrowLeft, ArrowRight, Check, CheckCircle2, Info, Plus, Sparkles, Trash2,
} from 'lucide-react';
import { channelsApi } from '@/api/channels';
import { subscriptionsApi } from '@/api/subscriptions';
import { Avatar } from '@/components/ui/Avatar';
import { Button } from '@/components/ui/Button';
import type {
  Channel, ChannelAudience, ChannelRules, ChannelSchedule, CTAConfig,
  ProductOffer, WritingDNA,
} from '@/types/channel';
import { hapticImpact, hapticNotification, openInvoice } from '@/lib/telegram';
import './ChannelOnboardingPage.css';

const NICHES = ['Sports', 'Finance', 'Education', 'Relationships', 'Marketing', 'Entertainment', 'Technology', 'Gaming', 'Lifestyle', 'Products / Services'];
const GOALS = ['Grow the channel', 'Increase engagement', 'Get link clicks', 'Get Telegram DMs', 'Generate leads', 'Sell products / services', 'Promote another channel', 'Get subscribers', 'Drive traffic'];
const TONES = ['Casual', 'Professional', 'Friendly', 'Funny', 'Bold', 'Authoritative', 'Motivational', 'Conversational', 'Educational', 'Opinionated'];
const WRITING_STYLES = ['Short and punchy', 'Detailed and educational', 'Storytelling', 'News-style', 'Conversational', 'Opinionated', 'Inspirational'];
const FORMATTING = ['Short paragraphs', 'Headings', 'Bullet points', 'Numbered lists', 'Bold text', 'Quotes', 'Questions', 'Separators'];
const CONTENT_TYPES = ['Educational', 'Tips', 'News / update', 'Story', 'Engagement', 'Question', 'Poll', 'Promotional', 'Announcement'];
const DAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'];

const emptyAudience: ChannelAudience = { interests: [] };
const emptyRules: ChannelRules = { always_do: [], never_do: [], forbidden_topics: [], forbidden_words: [] };
const emptySchedule: ChannelSchedule = { timezone: 'UTC', posts_per_day: 1, posting_times: ['09:00'], active_days: DAYS, daily_times: {} };
const emptyWritingDNA: WritingDNA = { mode: 'manual', tone: [], personality: [], formatting: [], sample_posts: [], style_analysis: {} };

function toggleValue(values: string[], value: string) {
  return values.includes(value) ? values.filter((item) => item !== value) : [...values, value];
}

function csvToList(value: string) {
  return value.split(',').map((item) => item.trim()).filter(Boolean);
}

function listToCsv(value: string[]) {
  return value.join(', ');
}

export default function ChannelOnboardingPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [channel, setChannel] = React.useState<Channel | null>(null);
  const [step, setStep] = React.useState(0);
  const [isLoading, setIsLoading] = React.useState(true);
  const [isSaving, setIsSaving] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [customTopic, setCustomTopic] = React.useState('');
  const [identity, setIdentity] = React.useState({
    niches: [] as string[], topics: [] as string[], audience: emptyAudience,
    conversion_goals: [] as string[], rules: emptyRules, frequency: 'daily', schedule: emptySchedule,
  });
  const [brain, setBrain] = React.useState({ writing_dna: emptyWritingDNA, content_types: ['Educational', 'Tips', 'Engagement'] });
  const [cta, setCta] = React.useState({ enabled: false, products: [] as ProductOffer[], ctas: [] as CTAConfig[], promotion_style: 'Soft sell', max_promotions_per_week: 2 });
  const [publishMode, setPublishMode] = React.useState<'approval' | 'auto'>('approval');
  const [testPost, setTestPost] = React.useState('');
  const [testTopic, setTestTopic] = React.useState('');
  const [testContext, setTestContext] = React.useState('');
  const [testType, setTestType] = React.useState('Educational');
  const [remainingTests, setRemainingTests] = React.useState<number | null>(null);
  const [remainingAnalyses, setRemainingAnalyses] = React.useState<number | null>(null);
  const [purchasingCredits, setPurchasingCredits] = React.useState<'test_generation' | 'style_analysis' | null>(null);
  const [isTesting, setIsTesting] = React.useState(false);
  const [feedbackStatus, setFeedbackStatus] = React.useState<string | null>(null);
  const [isSendingFeedback, setIsSendingFeedback] = React.useState(false);
  const [isAnalyzingStyle, setIsAnalyzingStyle] = React.useState(false);
  const [analysisStatus, setAnalysisStatus] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!id) return;
    channelsApi.get(id)
      .then((result) => {
        setChannel(result);
        const savedBrain = result.brain;
        setIdentity({
          niches: savedBrain.niches ?? (savedBrain.niche ? [savedBrain.niche] : []),
          topics: savedBrain.topics ?? [],
          audience: savedBrain.audience ?? { ...emptyAudience, description: savedBrain.audience_description },
          conversion_goals: savedBrain.conversion_goals ?? (savedBrain.goals ? [savedBrain.goals] : []),
          rules: savedBrain.rules ?? emptyRules,
          frequency: savedBrain.frequency ?? 'daily',
          schedule: result.schedule ?? emptySchedule,
        });
        setBrain({ writing_dna: savedBrain.writing_dna ?? emptyWritingDNA, content_types: savedBrain.content_types ?? ['Educational', 'Tips', 'Engagement'] });
        setCta({ enabled: savedBrain.cta_enabled ?? false, products: savedBrain.products ?? [], ctas: savedBrain.ctas ?? [], promotion_style: savedBrain.promotion_style ?? 'Soft sell', max_promotions_per_week: savedBrain.max_promotions_per_week ?? 2 });
        setPublishMode(result.publish_mode);
      })
      .catch((err) => setError(err instanceof Error ? err.message : 'Could not load channel'))
      .finally(() => setIsLoading(false));
  }, [id]);

  const updateAudience = (patch: Partial<ChannelAudience>) => setIdentity((current) => ({ ...current, audience: { ...current.audience, ...patch } }));
  const updateRules = (patch: Partial<ChannelRules>) => setIdentity((current) => ({ ...current, rules: { ...current.rules, ...patch } }));
  const updateDNA = (patch: Partial<WritingDNA>) => setBrain((current) => ({ ...current, writing_dna: { ...current.writing_dna, ...patch } }));

  const saveStep = async (nextStep: number) => {
    if (!id) return;
    setIsSaving(true);
    setError(null);
    try {
      if (step === 0) {
        if (!identity.niches.length || !identity.topics.length || !identity.audience.description?.trim()) {
          setError('Choose at least one niche and topic, then describe your audience.');
          return;
        }
        const updated = await channelsApi.saveIdentity(id, identity);
        setChannel(updated);
      } else if (step === 1) {
        const writingDNA = brain.writing_dna;
        const sampleCount = writingDNA.sample_posts.filter((sample) => sample.trim()).length;
        if (writingDNA.mode === 'samples' && (sampleCount < 3 || !['analyzed', 'approved'].includes(writingDNA.style_analysis_status ?? ''))) {
          setError('Analyze at least 3 real posts and review the voice profile before continuing.');
          return;
        }
        if (writingDNA.mode === 'manual' && !writingDNA.tone.length) {
          setError('Choose a tone or add writing samples so your AI has a clear voice.');
          return;
        }
        const approvedDNA = writingDNA.style_analysis_status === 'analyzed'
          ? { ...writingDNA, style_analysis_status: 'approved' as const }
          : writingDNA;
        const updated = await channelsApi.saveBrain(id, { ...brain, writing_dna: approvedDNA });
        setBrain((current) => ({ ...current, writing_dna: approvedDNA }));
        setChannel(updated);
      } else if (step === 2) {
        const updated = await channelsApi.saveCta(id, cta);
        setChannel(updated);
      }
      setStep(nextStep);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not save this step');
    } finally {
      setIsSaving(false);
    }
  };

  const activate = async () => {
    if (!id) return;
    setIsSaving(true);
    setError(null);
    try {
      const updated = await channelsApi.activate(id, publishMode);
      setChannel(updated);
      hapticNotification('success');
      navigate(`/channels/${id}`, { replace: true });
    } catch (err) {
      hapticNotification('error');
      setError(err instanceof Error ? err.message : 'Could not activate AI');
    } finally {
      setIsSaving(false);
    }
  };

  const generateTest = async () => {
    if (!id || !testTopic.trim()) return;
    setIsTesting(true);
    setError(null);
    try {
      const result = await channelsApi.testGeneration(id, { content_type: testType, topic: testTopic.trim(), context: testContext.trim() || undefined });
      setTestPost(result.content);
      setRemainingTests(result.remaining_tests);
    } catch (err) {
      if (err instanceof Error && err.message.toLowerCase().includes('allowance')) setRemainingTests(0);
      setError(err instanceof Error ? err.message : 'Could not generate a test post');
    } finally {
      setIsTesting(false);
    }
  };

  const sendFeedback = async (feedback: string) => {
    if (!id) return;
    setIsSendingFeedback(true);
    setFeedbackStatus(null);
    try {
      await channelsApi.testGenerationFeedback(id, feedback);
      setFeedbackStatus('Feedback saved');
    } catch {
      setFeedbackStatus('Could not save feedback');
    } finally {
      setIsSendingFeedback(false);
    }
  };

  const analyzeStyle = async () => {
    if (!id) return;
    const samples = brain.writing_dna.sample_posts.filter((sample) => sample.trim());
    if (samples.length < 3) {
      setError('Add at least 3 real posts before analyzing your writing style.');
      return;
    }
    setIsAnalyzingStyle(true);
    setAnalysisStatus(null);
    setError(null);
    try {
      const analyzedDNA = await channelsApi.analyzeStyle(id, samples);
      setBrain((current) => ({ ...current, writing_dna: { ...analyzedDNA, sample_posts: samples } }));
      setRemainingAnalyses(analyzedDNA.remaining_analyses);
      setAnalysisStatus('Analysis ready. Review and edit the profile below.');
    } catch (err) {
      if (err instanceof Error && err.message.toLowerCase().includes('allowance')) setRemainingAnalyses(0);
      setError(err instanceof Error ? err.message : 'Could not analyze your posts');
    } finally {
      setIsAnalyzingStyle(false);
    }
  };

  const purchaseCredits = async (usageType: 'test_generation' | 'style_analysis') => {
    if (!id) return;
    setPurchasingCredits(usageType);
    setError(null);
    try {
      const invoice = await subscriptionsApi.createUsageCreditInvoice(id, usageType);
      openInvoice(invoice.invoice_link, (status) => {
        if (status === 'paid') {
          if (usageType === 'test_generation') setRemainingTests(5);
          else setRemainingAnalyses(5);
          hapticNotification('success');
        } else if (status === 'failed') {
          setError('The payment could not be completed.');
          hapticNotification('error');
        }
        setPurchasingCredits(null);
      });
    } catch (err) {
      setPurchasingCredits(null);
      setError(err instanceof Error ? err.message : 'Could not open the payment');
    }
  };

  if (isLoading) return <div className="onboarding-page onboarding-page--loading">Loading your channel...</div>;
  if (!channel) return <div className="onboarding-page"><div className="onboarding-error">{error ?? 'Channel not found'}</div></div>;

  return (
    <div className="onboarding-page">
      <header className="onboarding-header">
        <button className="onboarding-back" onClick={() => { hapticImpact('light'); navigate(-1); }} aria-label="Go back"><ArrowLeft size={20} /></button>
        <div className="onboarding-header__identity"><Avatar src={channel.photo_url} name={channel.name} size={34} /><span>{channel.name}</span></div>
        <span className="onboarding-header__count">{step + 1} / 4</span>
      </header>

      <div className="onboarding-progress" aria-label="Onboarding progress">
        {['Channel Identity', 'Channel Brain', 'CTA Library', 'Setup & Activate'].map((label, index) => (
          <button key={label} className={`onboarding-progress__item ${index === step ? 'is-current' : ''} ${index < step ? 'is-complete' : ''}`} onClick={() => index < step && setStep(index)} disabled={index > step}>
            <span>{index < step ? <Check size={14} /> : index + 1}</span><small>{label}</small>
          </button>
        ))}
      </div>

      <main className="onboarding-body">
        {step === 0 && <IdentityStep channel={channel} identity={identity} updateAudience={updateAudience} updateRules={updateRules} setIdentity={setIdentity} customTopic={customTopic} setCustomTopic={setCustomTopic} />}
        {step === 1 && <BrainStepWithAnalysis brain={brain} updateDNA={updateDNA} setBrain={setBrain} analyzeStyle={analyzeStyle} isAnalyzingStyle={isAnalyzingStyle} analysisStatus={analysisStatus} remainingAnalyses={remainingAnalyses} purchaseCredits={purchaseCredits} purchasingCredits={purchasingCredits} />}
        {step === 2 && <CtaStep cta={cta} setCta={setCta} />}
        {step === 3 && <ActivateStep channel={channel} identity={identity} brain={brain} cta={cta} publishMode={publishMode} setPublishMode={setPublishMode} testPost={testPost} testTopic={testTopic} setTestTopic={setTestTopic} testContext={testContext} setTestContext={setTestContext} testType={testType} setTestType={setTestType} remainingTests={remainingTests} isTesting={isTesting} generateTest={generateTest} sendFeedback={sendFeedback} feedbackStatus={feedbackStatus} isSendingFeedback={isSendingFeedback} purchaseCredits={purchaseCredits} purchasingCredits={purchasingCredits} />}

        {error && <div className="onboarding-error"><Info size={17} />{error}</div>}
        <div className="onboarding-actions">
          {step > 0 && <Button variant="ghost" onClick={() => setStep(step - 1)} leftIcon={<ArrowLeft size={17} />}>Back</Button>}
          {step < 3 ? <Button variant="primary" isLoading={isSaving} onClick={() => void saveStep(step + 1)} rightIcon={<ArrowRight size={17} />}>{step === 2 && !cta.enabled ? 'Skip for now' : 'Save & continue'}</Button> : <Button variant="primary" isLoading={isSaving} onClick={() => void activate()} leftIcon={<Sparkles size={17} />}>Activate AI</Button>}
        </div>
      </main>
    </div>
  );
}

type IdentityProps = { channel: Channel; identity: { niches: string[]; topics: string[]; audience: ChannelAudience; conversion_goals: string[]; rules: ChannelRules; frequency: string; schedule: ChannelSchedule }; updateAudience: (patch: Partial<ChannelAudience>) => void; updateRules: (patch: Partial<ChannelRules>) => void; setIdentity: React.Dispatch<React.SetStateAction<IdentityProps['identity']>>; customTopic: string; setCustomTopic: React.Dispatch<React.SetStateAction<string>> };
function IdentityStep({ channel, identity, updateAudience, updateRules, setIdentity, customTopic, setCustomTopic }: IdentityProps) {
  const addTopic = () => { if (customTopic.trim()) { setIdentity((current) => ({ ...current, topics: [...new Set([...current.topics, customTopic.trim()])] })); setCustomTopic(''); } };
  return <section className="onboarding-section">
    <div className="section-intro"><span className="eyebrow">Part A</span><h1>Teach your AI what this channel is about</h1><p>Set the audience, content boundaries, goals, and schedule your AI manager should follow.</p></div>
    <div className="channel-confirmation"><Avatar src={channel.photo_url} name={channel.name} size={56} /><div><strong>{channel.name}</strong><span>{channel.username ? `@${channel.username}` : channel.telegram_channel_id}</span></div><CheckCircle2 size={19} /></div>
    <FieldGroup title="What is your channel about?" hint="Choose one or more niches."><div className="chip-grid">{NICHES.map((item) => <Chip key={item} label={item} selected={identity.niches.includes(item)} onClick={() => setIdentity((current) => ({ ...current, niches: toggleValue(current.niches, item) }))} />)}</div></FieldGroup>
    <FieldGroup title="What should your AI regularly create content about?" hint="Add focused topics so your content stays useful."><div className="chip-grid">{identity.niches.flatMap((niche) => ({ Marketing: ['Facebook Ads', 'Sales', 'Lead Generation', 'Copywriting'], Sports: ['News', 'Analysis', 'Tips'], Finance: ['Investing', 'Money habits', 'Business'], Education: ['How-to guides', 'Study tips'] }[niche] ?? [])).map((item) => <Chip key={item} label={item} selected={identity.topics.includes(item)} onClick={() => setIdentity((current) => ({ ...current, topics: toggleValue(current.topics, item) }))} />)}</div><div className="inline-input"><input value={customTopic} onChange={(event) => setCustomTopic(event.target.value)} onKeyDown={(event) => event.key === 'Enter' && (event.preventDefault(), addTopic())} placeholder="Add a custom topic" /><button type="button" onClick={addTopic} aria-label="Add topic"><Plus size={18} /></button></div><div className="selected-list">{identity.topics.map((topic) => <span key={topic}>{topic}<button type="button" onClick={() => setIdentity((current) => ({ ...current, topics: current.topics.filter((item) => item !== topic) }))}>×</button></span>)}</div></FieldGroup>
    <FieldGroup title="Who is this content for?" hint="A specific audience helps the AI choose the right examples and language."><div className="form-grid"><label>Age range<input value={identity.audience.age_range ?? ''} onChange={(e) => updateAudience({ age_range: e.target.value })} placeholder="18–35" /></label><label>Location<input value={identity.audience.location ?? ''} onChange={(e) => updateAudience({ location: e.target.value })} placeholder="Nigeria, global" /></label><label>Experience level<select value={identity.audience.experience_level ?? ''} onChange={(e) => updateAudience({ experience_level: e.target.value })}><option value="">Select one</option><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select></label><label>Interests<input value={listToCsv(identity.audience.interests)} onChange={(e) => updateAudience({ interests: csvToList(e.target.value) })} placeholder="Business, growth, technology" /></label></div><label>Describe your ideal audience<textarea value={identity.audience.description ?? ''} onChange={(e) => updateAudience({ description: e.target.value })} placeholder="Young Nigerian entrepreneurs who want practical ways to grow their businesses." /></label></FieldGroup>
    <FieldGroup title="What should your content help achieve?"><div className="chip-grid">{GOALS.map((item) => <Chip key={item} label={item} selected={identity.conversion_goals.includes(item)} onClick={() => setIdentity((current) => ({ ...current, conversion_goals: toggleValue(current.conversion_goals, item) }))} />)}</div></FieldGroup>
    <FieldGroup title="Rules & restrictions" hint="These are high-priority instructions for every generated post."><label>Always do<textarea value={identity.rules.always_do.join('\n')} onChange={(e) => updateRules({ always_do: e.target.value.split('\n').filter(Boolean) })} placeholder="Use Nigerian English\nKeep paragraphs short" /></label><label>Never do<textarea value={identity.rules.never_do.join('\n')} onChange={(e) => updateRules({ never_do: e.target.value.split('\n').filter(Boolean) })} placeholder="Do not use profanity\nDo not make financial promises" /></label><label>Custom rules<textarea value={identity.rules.custom_rules ?? ''} onChange={(e) => updateRules({ custom_rules: e.target.value })} placeholder="Any other important guardrails" /></label></FieldGroup>
    <FieldGroup title="When should your AI post?" hint="Your plan allowance is enforced by the backend."><div className="form-grid"><label>Posts per day<input type="number" min="1" max="10" value={identity.schedule.posts_per_day} onChange={(e) => setIdentity((current) => ({ ...current, schedule: { ...current.schedule, posts_per_day: Number(e.target.value) } }))} /></label><label>Timezone<input value={identity.schedule.timezone} onChange={(e) => setIdentity((current) => ({ ...current, schedule: { ...current.schedule, timezone: e.target.value } }))} placeholder="Africa/Lagos" /></label><label>Posting times<input value={identity.schedule.posting_times.join(', ')} onChange={(e) => setIdentity((current) => ({ ...current, schedule: { ...current.schedule, posting_times: csvToList(e.target.value) } }))} placeholder="08:00, 13:00, 19:00" /></label></div><div className="day-row">{DAYS.map((day) => <Chip key={day} label={day.toUpperCase()} selected={identity.schedule.active_days.includes(day)} onClick={() => setIdentity((current) => ({ ...current, schedule: { ...current.schedule, active_days: toggleValue(current.schedule.active_days, day) } }))} />)}</div></FieldGroup>
  </section>;
}

function BrainStepWithAnalysis({ brain, updateDNA, setBrain, analyzeStyle, isAnalyzingStyle, analysisStatus, remainingAnalyses, purchaseCredits, purchasingCredits }: { brain: { writing_dna: WritingDNA; content_types: string[] }; updateDNA: (patch: Partial<WritingDNA>) => void; setBrain: React.Dispatch<React.SetStateAction<{ writing_dna: WritingDNA; content_types: string[] }>>; analyzeStyle: () => Promise<void>; isAnalyzingStyle: boolean; analysisStatus: string | null; remainingAnalyses: number | null; purchaseCredits: (usageType: 'test_generation' | 'style_analysis') => Promise<void>; purchasingCredits: 'test_generation' | 'style_analysis' | null }) {
  const dna = brain.writing_dna;
  return <>
    <BrainStep brain={brain} updateDNA={updateDNA} setBrain={setBrain} />
    {dna.mode === 'samples' && <section className="style-analysis-panel">
      <div className="style-analysis-panel__heading"><div><span className="eyebrow">Voice profile</span><h2>Analyze my posts</h2><p>We will turn the patterns in your examples into direct writing instructions. You can edit every result before saving.</p></div><Sparkles size={22} /></div>
      <div className="credit-actions">
        <Button variant="secondary" isLoading={isAnalyzingStyle} onClick={() => void analyzeStyle()} disabled={remainingAnalyses === 0} leftIcon={<Sparkles size={16} />}>Analyze my posts</Button>
        {remainingAnalyses === 0 && <Button variant="primary" isLoading={purchasingCredits === 'style_analysis'} onClick={() => void purchaseCredits('style_analysis')}>Get 5 more for 150 Stars</Button>}
      </div>
      {remainingAnalyses !== null && <div className="credit-balance">{remainingAnalyses} analysis credit{remainingAnalyses === 1 ? '' : 's'} remaining</div>}
      {analysisStatus && <div className="analysis-status" role="status"><CheckCircle2 size={16} />{analysisStatus}</div>}
      {['analyzed', 'approved'].includes(dna.style_analysis_status ?? '') && <div className="analysis-fields">
        <label>Overall voice<textarea value={String(dna.style_analysis.overall_voice ?? '')} onChange={(e) => updateDNA({ style_analysis: { ...dna.style_analysis, overall_voice: e.target.value } })} /></label>
        <label>Vocabulary and language<textarea value={dna.vocabulary ?? ''} onChange={(e) => updateDNA({ vocabulary: e.target.value })} /></label>
        <label>Sentence rhythm<textarea value={dna.sentence_style ?? ''} onChange={(e) => updateDNA({ sentence_style: e.target.value })} /></label>
        <label>Paragraph spacing<textarea value={dna.paragraph_structure ?? ''} onChange={(e) => updateDNA({ paragraph_structure: e.target.value })} /></label>
        <label>Hooks and storytelling<textarea value={`${dna.hook_style ?? ''}${dna.style_analysis.storytelling_pattern ? `\n${String(dna.style_analysis.storytelling_pattern)}` : ''}`} onChange={(e) => updateDNA({ hook_style: e.target.value })} /></label>
        <label>Emoji and formatting<textarea value={`${dna.emoji_usage ?? ''}${dna.style_analysis.line_break_pattern ? `\n${String(dna.style_analysis.line_break_pattern)}` : ''}`} onChange={(e) => updateDNA({ emoji_usage: e.target.value })} /></label>
        <label>CTA style<textarea value={dna.cta_style ?? ''} onChange={(e) => updateDNA({ cta_style: e.target.value })} /></label>
        <label>Extra writing instructions<textarea value={dna.advanced_instructions ?? ''} onChange={(e) => updateDNA({ advanced_instructions: e.target.value })} /></label>
      </div>}
    </section>}
  </>;
}

function BrainStep({ brain, updateDNA, setBrain }: { brain: { writing_dna: WritingDNA; content_types: string[] }; updateDNA: (patch: Partial<WritingDNA>) => void; setBrain: React.Dispatch<React.SetStateAction<{ writing_dna: WritingDNA; content_types: string[] }>> }) {
  const dna = brain.writing_dna;
  return <section className="onboarding-section"><div className="section-intro"><span className="eyebrow">Part B</span><h1>Teach your AI how to sound</h1><p>Build a writing style manually, or show the AI three to five examples of your posts.</p></div><div className="mode-switch"><button className={dna.mode === 'manual' ? 'is-selected' : ''} onClick={() => updateDNA({ mode: 'manual' })}>Build manually</button><button className={dna.mode === 'samples' ? 'is-selected' : ''} onClick={() => updateDNA({ mode: 'samples' })}>Learn from my posts</button></div>{dna.mode === 'manual' ? <><FieldGroup title="Tone and personality"><div className="chip-grid">{TONES.map((item) => <Chip key={item} label={item} selected={dna.tone.includes(item)} onClick={() => updateDNA({ tone: toggleValue(dna.tone, item) })} />)}</div></FieldGroup><FieldGroup title="Writing style"><div className="chip-grid">{WRITING_STYLES.map((item) => <Chip key={item} label={item} selected={dna.personality.includes(item)} onClick={() => updateDNA({ personality: toggleValue(dna.personality, item) })} />)}</div></FieldGroup></> : <FieldGroup title="Show us how you write" hint="Paste 3–5 real posts. The analysis will become editable Writing DNA."><div className="sample-list">{[0, 1, 2, 3, 4].map((index) => <textarea key={index} value={dna.sample_posts[index] ?? ''} onChange={(e) => { const samples = [...dna.sample_posts]; samples[index] = e.target.value; updateDNA({ sample_posts: samples }); }} placeholder={`Post example ${index + 1}${index > 2 ? ' (optional)' : ''}`} />)}</div></FieldGroup>}<FieldGroup title="Formatting and feel"><div className="chip-grid">{FORMATTING.map((item) => <Chip key={item} label={item} selected={dna.formatting.includes(item)} onClick={() => updateDNA({ formatting: toggleValue(dna.formatting, item) })} />)}</div><div className="form-grid"><label>Emoji usage<select value={dna.emoji_usage ?? ''} onChange={(e) => updateDNA({ emoji_usage: e.target.value })}><option value="">Choose</option><option>None</option><option>Minimal</option><option>Moderate</option><option>Heavy</option></select></label><label>Post length<select value={dna.post_length ?? ''} onChange={(e) => updateDNA({ post_length: e.target.value })}><option value="">Choose</option><option>Short</option><option>Medium</option><option>Long</option></select></label></div></FieldGroup><FieldGroup title="Content types"><div className="chip-grid">{CONTENT_TYPES.map((item) => <Chip key={item} label={item} selected={brain.content_types.includes(item)} onClick={() => setBrain((current) => ({ ...current, content_types: toggleValue(current.content_types, item) }))} />)}</div></FieldGroup><FieldGroup title="Advanced instructions (optional)"><textarea value={dna.advanced_instructions ?? ''} onChange={(e) => updateDNA({ advanced_instructions: e.target.value })} placeholder="Any extra guidance for how your AI should write." /></FieldGroup></section>;
}

function CtaStep({ cta, setCta }: { cta: { enabled: boolean; products: ProductOffer[]; ctas: CTAConfig[]; promotion_style: string; max_promotions_per_week: number }; setCta: React.Dispatch<React.SetStateAction<{ enabled: boolean; products: ProductOffer[]; ctas: CTAConfig[]; promotion_style: string; max_promotions_per_week: number }>> }) {
  const product = cta.products[0] ?? { name: '', description: '', selling_points: [], benefits: [] };
  const updateProduct = (patch: Partial<ProductOffer>) => setCta((current) => ({ ...current, products: [{ ...product, ...patch }] }));
  const ctaConfig = cta.ctas[0] ?? { type: 'Telegram DM' };
  const updateCta = (patch: Partial<CTAConfig>) => setCta((current) => ({ ...current, ctas: [{ ...ctaConfig, ...patch }] }));
  return <section className="onboarding-section"><div className="section-intro"><span className="eyebrow">Part C</span><h1>Give your AI a CTA library</h1><p>Optional. Add products and destinations only when promotion is part of your strategy. Your AI will not attach a CTA to every post.</p></div><div className="toggle-row"><div><strong>Use products and CTAs</strong><span>Enable this when you sell, promote, or drive traffic.</span></div><button className={`toggle ${cta.enabled ? 'is-on' : ''}`} onClick={() => setCta((current) => ({ ...current, enabled: !current.enabled }))} aria-label="Toggle CTA library"><span /></button></div>{cta.enabled && <><FieldGroup title="Product or offer"><label>Name<input value={product.name} onChange={(e) => updateProduct({ name: e.target.value })} placeholder="Facebook Ads Masterclass" /></label><label>What problem does it solve?<textarea value={product.description ?? ''} onChange={(e) => updateProduct({ description: e.target.value })} placeholder="Practical tutorials and templates for growing with ads." /></label><label>Selling points<textarea value={product.selling_points.join('\n')} onChange={(e) => updateProduct({ selling_points: e.target.value.split('\n').filter(Boolean) })} placeholder="One point per line" /></label></FieldGroup><FieldGroup title="How should people take action?"><div className="form-grid"><label>CTA type<select value={ctaConfig.type} onChange={(e) => updateCta({ type: e.target.value })}><option>Telegram DM</option><option>Link click</option><option>Join a channel</option><option>Purchase link</option></select></label><label>Telegram username or URL<input value={ctaConfig.telegram_username ?? ctaConfig.destination_url ?? ''} onChange={(e) => updateCta({ telegram_username: e.target.value, destination_url: e.target.value })} placeholder="@support or https://..." /></label><label>Keyword<input value={ctaConfig.keyword ?? ''} onChange={(e) => updateCta({ keyword: e.target.value })} placeholder="ADS" /></label><label>Maximum promotions / week<input type="number" min="0" max="20" value={cta.max_promotions_per_week} onChange={(e) => setCta((current) => ({ ...current, max_promotions_per_week: Number(e.target.value) }))} /></label></div></FieldGroup><FieldGroup title="Promotion style"><div className="chip-grid">{['Soft sell', 'Educational before selling', 'Direct', 'Urgent', 'Curiosity-driven', 'Story-based'].map((item) => <Chip key={item} label={item} selected={cta.promotion_style === item} onClick={() => setCta((current) => ({ ...current, promotion_style: item }))} />)}</div></FieldGroup></>}</section>;
}

function ActivateStep({ channel, identity, brain, cta, publishMode, setPublishMode, testPost, testTopic, setTestTopic, testContext, setTestContext, testType, setTestType, remainingTests, isTesting, generateTest, sendFeedback, feedbackStatus, isSendingFeedback, purchaseCredits, purchasingCredits }: { channel: Channel; identity: IdentityProps['identity']; brain: { writing_dna: WritingDNA; content_types: string[] }; cta: { enabled: boolean; products: ProductOffer[] }; publishMode: 'approval' | 'auto'; setPublishMode: React.Dispatch<React.SetStateAction<'approval' | 'auto'>>; testPost: string; testTopic: string; setTestTopic: React.Dispatch<React.SetStateAction<string>>; testContext: string; setTestContext: React.Dispatch<React.SetStateAction<string>>; testType: string; setTestType: React.Dispatch<React.SetStateAction<string>>; remainingTests: number | null; isTesting: boolean; generateTest: () => Promise<void>; sendFeedback: (feedback: string) => Promise<void>; feedbackStatus: string | null; isSendingFeedback: boolean; purchaseCredits: (usageType: 'test_generation' | 'style_analysis') => Promise<void>; purchasingCredits: 'test_generation' | 'style_analysis' | null }) {
  return <section className="onboarding-section"><div className="section-intro"><span className="eyebrow">Part D</span><h1>Review and activate your AI manager</h1><p>Try the configured voice, choose publishing behavior, then activate automation.</p></div><FieldGroup title="Test your AI" hint={remainingTests === null ? 'Each test uses a limited allowance.' : `${remainingTests} test generation${remainingTests === 1 ? '' : 's'} remaining`}><div className="form-grid"><label>Content type<select value={testType} onChange={(e) => setTestType(e.target.value)}>{CONTENT_TYPES.map((type) => <option key={type}>{type}</option>)}</select></label><label>Topic<input value={testTopic} onChange={(e) => setTestTopic(e.target.value)} placeholder="A topic for this sample post" /></label></div><label>Optional context<textarea value={testContext} onChange={(e) => setTestContext(e.target.value)} placeholder="What should this sample emphasize?" /></label><div className="credit-actions"><Button variant="secondary" isLoading={isTesting} onClick={() => void generateTest()} disabled={!testTopic.trim() || remainingTests === 0} leftIcon={<Sparkles size={16} />}>Generate sample</Button>{remainingTests === 0 && <Button variant="primary" isLoading={purchasingCredits === 'test_generation'} onClick={() => void purchaseCredits('test_generation')}>Get 5 more for 150 Stars</Button>}</div>{testPost && <div className="test-post"><div className="test-post__label">Generated sample</div><div className="test-post__content">{testPost}</div><div className="feedback-row"><span>How does it feel?</span><button type="button" disabled={isSendingFeedback} onClick={() => void sendFeedback('Sounds like me')}>Sounds like me</button><button type="button" disabled={isSendingFeedback} onClick={() => void sendFeedback('Needs work')}>Needs work</button>{feedbackStatus && <strong className="feedback-status" role="status">{feedbackStatus}</strong>}</div></div>}</FieldGroup><div className="review-card"><ReviewRow label="Channel" value={channel.name} /><ReviewRow label="Niche" value={identity.niches.join(', ') || 'Not set'} /><ReviewRow label="Topics" value={identity.topics.join(', ') || 'Not set'} /><ReviewRow label="Audience" value={identity.audience.description || 'Not set'} /><ReviewRow label="Writing style" value={brain.writing_dna.tone.join(', ') || 'Sample-based'} /><ReviewRow label="Goals" value={identity.conversion_goals.join(', ') || 'Grow and engage'} /><ReviewRow label="CTA library" value={cta.enabled ? `${cta.products[0]?.name || 'Configured offer'}` : 'Skipped for now'} /></div><FieldGroup title="How should publishing work?"><div className="publish-options"><button className={publishMode === 'approval' ? 'is-selected' : ''} onClick={() => setPublishMode('approval')}><strong>Approve before publish</strong><span>Receive each generated draft and decide when it goes live.</span></button><button className={publishMode === 'auto' ? 'is-selected' : ''} onClick={() => setPublishMode('auto')}><strong>Auto publish</strong><span>Your AI publishes automatically according to the schedule.</span></button></div></FieldGroup><div className="activation-note"><Info size={18} /><span>Automata TG will only activate after the bot is an administrator with permission to post messages.</span></div></section>;
}

function ReviewRow({ label, value }: { label: string; value: string }) { return <div className="review-row"><span>{label}</span><strong>{value}</strong></div>; }
function FieldGroup({ title, hint, children }: { title: string; hint?: string; children: React.ReactNode }) { return <div className="field-group"><div className="field-group__heading"><h2>{title}</h2>{hint && <p>{hint}</p>}</div>{children}</div>; }
function Chip({ label, selected, onClick }: { label: string; selected: boolean; onClick: () => void }) { return <button type="button" className={`chip ${selected ? 'is-selected' : ''}`} onClick={onClick}>{selected && <Check size={14} />}{label}</button>; }
