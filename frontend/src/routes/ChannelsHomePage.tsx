import React from 'react';
import { useAuth } from '@/context/AuthContext';
import { useChannels } from '@/hooks/useChannels';
import { ChannelList } from '@/components/channels/ChannelList';
import { ChannelsEmptyState } from '@/components/channels/ChannelsEmptyState';
import { NewChannelButton } from '@/components/channels/NewChannelButton';
import { Bot, Clock3, RefreshCw, Send, X } from 'lucide-react';
import { postsApi } from '@/api/channels';
import type { ScheduledPost } from '@/types/channel';
import { Button } from '@/components/ui/Button';
import './ChannelsHomePage.css';

export default function ChannelsHomePage() {
  const { user } = useAuth();
  const { channels, isLoading, error, refetch } = useChannels();
  const [pendingPosts, setPendingPosts] = React.useState<ScheduledPost[]>([]);
  const [postsError, setPostsError] = React.useState<string | null>(null);
  const [actingPostId, setActingPostId] = React.useState<string | null>(null);

  const loadPendingPosts = React.useCallback(async () => {
    try {
      setPendingPosts(await postsApi.pending());
      setPostsError(null);
    } catch (err) {
      setPostsError(err instanceof Error ? err.message : 'Could not load posts awaiting review.');
    }
  }, []);

  React.useEffect(() => {
    void loadPendingPosts();
  }, [loadPendingPosts]);

  React.useEffect(() => {
    const refreshOnReturn = () => {
      if (document.visibilityState === 'visible') void loadPendingPosts();
    };
    document.addEventListener('visibilitychange', refreshOnReturn);
    return () => document.removeEventListener('visibilitychange', refreshOnReturn);
  }, [loadPendingPosts]);

  const decidePost = async (post: ScheduledPost, decision: 'approve' | 'decline') => {
    setActingPostId(post.id);
    setPostsError(null);
    try {
      if (decision === 'approve') await postsApi.approve(post.id);
      else await postsApi.decline(post.id);
      setPendingPosts((current) => current.filter((item) => item.id !== post.id));
    } catch (err) {
      setPostsError(err instanceof Error ? err.message : 'Could not update this post.');
    } finally {
      setActingPostId(null);
    }
  };

  return (
    <div className="channels-home">
      {/* Header */}
      <header className="channels-home__header">
        <div>
          <h1 className="channels-home__title">My Channels</h1>
          {user && (
            <p className="channels-home__subtitle">
              Hi {user.first_name} 👋 — {channels.length} channel{channels.length !== 1 ? 's' : ''} connected
            </p>
          )}
        </div>
        {channels.length > 0 && <NewChannelButton compact />}
      </header>

      {/* Content */}
      <div className="channels-home__body">
        <section className="pending-posts" aria-labelledby="pending-posts-title">
          <div className="pending-posts__heading">
            <div>
              <span className="pending-posts__eyebrow"><Clock3 size={13} /> Content review</span>
              <h2 id="pending-posts-title">Posts awaiting approval</h2>
            </div>
            {pendingPosts.length > 0 && <span className="pending-posts__count">{pendingPosts.length}</span>}
          </div>
          {postsError && <p className="pending-posts__error" role="alert">{postsError}</p>}
          {!postsError && pendingPosts.length === 0 && (
            <p className="pending-posts__empty">Gemini’s scheduled drafts will appear here for review.</p>
          )}
          {pendingPosts.map((post) => (
            <article className="pending-post" key={post.id}>
              <div className="pending-post__meta">
                <strong>{post.channel_name}</strong>
                <time dateTime={post.scheduled_for}>
                  {new Date(post.scheduled_for).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })}
                </time>
              </div>
              {post.poll ? (
                <div className="pending-post__poll">
                  <strong>{post.poll.question}</strong>
                  <ol>{post.poll.options.map((option, index) => <li key={`${index}-${option}`}>{option}</li>)}</ol>
                  {post.poll.poll_type === 'quiz' && <small>Correct answer: {post.poll.options[post.poll.correct_option_id ?? -1] ?? 'Not provided'}</small>}
                </div>
              ) : (
                <p className="pending-post__content">{post.content}</p>
              )}
              <div className="pending-post__actions">
                <Button
                  variant="ghost"
                  size="sm"
                  disabled={actingPostId !== null}
                  onClick={() => void decidePost(post, 'decline')}
                  leftIcon={<X size={15} />}
                >
                  Decline
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  isLoading={actingPostId === post.id}
                  disabled={actingPostId !== null}
                  onClick={() => void decidePost(post, 'approve')}
                  leftIcon={<Send size={15} />}
                >
                  Approve & publish
                </Button>
              </div>
            </article>
          ))}
        </section>

        {isLoading && (
          <div className="channels-home__loading" aria-label="Loading channels">
            {[1, 2, 3].map((i) => (
              <div key={i} className="channel-skeleton" />
            ))}
          </div>
        )}

        {!isLoading && error && (
          <div className="channels-home__error">
            <Bot size={32} />
            <p>{error}</p>
            <button className="channels-home__retry" onClick={refetch}>
              <RefreshCw size={14} /> Try again
            </button>
          </div>
        )}

        {!isLoading && !error && channels.length === 0 && <ChannelsEmptyState />}

        {!isLoading && !error && channels.length > 0 && (
          <ChannelList channels={channels} />
        )}
      </div>
    </div>
  );
}
