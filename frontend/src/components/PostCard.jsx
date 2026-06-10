import React from 'react';
import { ExternalLink, Star, Eye, EyeOff, Sparkles } from 'lucide-react';

function ScoreBadge({ score }) {
  let cls = 'score-low';
  if (score >= 75) cls = 'score-high';
  else if (score >= 50) cls = 'score-mid';
  return (
    <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${cls}`}>
      {score.toFixed(0)}
    </span>
  );
}

function SourceBadge({ source, category }) {
  const colors = {
    tech: 'bg-sky-100 text-sky-700 border-sky-200 dark:bg-sky-500/15 dark:text-sky-300 dark:border-sky-500/25',
    ai_research: 'bg-violet-100 text-violet-700 border-violet-200 dark:bg-violet-500/15 dark:text-violet-300 dark:border-violet-500/25',
    ai_tooling: 'bg-fuchsia-100 text-fuchsia-700 border-fuchsia-200 dark:bg-fuchsia-500/15 dark:text-fuchsia-300 dark:border-fuchsia-500/25',
    ai_news: 'bg-amber-100 text-amber-700 border-amber-200 dark:bg-amber-500/15 dark:text-amber-300 dark:border-amber-500/25',
    community: 'bg-rose-100 text-rose-700 border-rose-200 dark:bg-rose-500/15 dark:text-rose-300 dark:border-rose-500/25',
    news: 'bg-teal-100 text-teal-700 border-teal-200 dark:bg-teal-500/15 dark:text-teal-300 dark:border-teal-500/25',
  };
  return (
    <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${colors[category] || colors.tech}`}>
      {source.replace('reddit_', 'r/')}
    </span>
  );
}

export default function PostCard({ post, onToggleRead, onToggleFavorite }) {
  const rawDate = post.published_at ? new Date(post.published_at) : null;
  const isSentinel = rawDate && rawDate.getFullYear() < 2000;
  const date = isSentinel
    ? 'Unknown date'
    : rawDate
    ? rawDate.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
    : 'Unknown date';

  return (
    <div className={`group relative rounded-xl border border-gray-200 dark:border-gray-800 bg-white/60 dark:bg-gray-900/60 p-5 transition hover:border-gray-300 dark:hover:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-900 ${post.is_read ? 'opacity-60' : ''}`}>
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <SourceBadge source={post.source} category={post.category} />
            <ScoreBadge score={post.score} />
            {post.hn_score !== null && post.hn_score !== undefined && (
              <span className="text-xs text-gray-400 dark:text-gray-500">▲ {post.hn_score}</span>
            )}
            {post.comment_count !== null && post.comment_count !== undefined && (
              <span className="text-xs text-gray-400 dark:text-gray-500">💬 {post.comment_count}</span>
            )}
            <span className="text-xs text-gray-400 dark:text-gray-500">{date}</span>
          </div>
          <h3 className="text-base font-semibold text-gray-900 dark:text-gray-100 leading-snug">
            <a href={post.url} target="_blank" rel="noopener noreferrer" className="hover:text-sky-600 dark:hover:text-sky-400 transition">
              {post.title}
            </a>
          </h3>
          {post.llm_summary && (
            <div className="mt-2 flex items-start gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-sky-500 mt-0.5 shrink-0" />
              <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed italic">
                {post.llm_summary}
              </p>
            </div>
          )}
          {!post.llm_summary && post.content && (
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400 line-clamp-3 leading-relaxed">
              {post.content}
            </p>
          )}
        </div>
        <div className="flex flex-col items-end gap-2 shrink-0">
          <a
            href={post.url}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-lg p-2 text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-700 dark:hover:text-gray-100 transition"
            title="Open link"
          >
            <ExternalLink className="w-4 h-4" />
          </a>
          <button
            onClick={() => onToggleRead(post.id, !post.is_read)}
            className={`rounded-lg p-2 transition ${post.is_read ? 'text-gray-400 hover:bg-gray-100 dark:text-gray-500 dark:hover:bg-gray-800' : 'text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-700 dark:hover:text-gray-100'}`}
            title={post.is_read ? 'Mark unread' : 'Mark read'}
          >
            {post.is_read ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
          <button
            onClick={() => onToggleFavorite(post.id)}
            className={`rounded-lg p-2 transition ${post.is_favorite ? 'text-amber-500 dark:text-amber-400 hover:bg-gray-100 dark:hover:bg-gray-800' : 'text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-700 dark:hover:text-gray-100'}`}
            title="Favorite"
          >
            <Star className={`w-4 h-4 ${post.is_favorite ? 'fill-current' : ''}`} />
          </button>
        </div>
      </div>
    </div>
  );
}
