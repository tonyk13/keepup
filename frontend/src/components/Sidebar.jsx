import React, { useState } from 'react';
import { Rss, Cpu, Users, Newspaper, Wrench, Flame, ChevronDown, ChevronRight, RotateCw, Eye } from 'lucide-react';
import { triggerScrape } from '../api';

const categoryIcons = {
  tech: <Cpu className="w-4 h-4" />,
  ai_research: <Newspaper className="w-4 h-4" />,
  ai_tooling: <Wrench className="w-4 h-4" />,
  ai_news: <Flame className="w-4 h-4" />,
  community: <Users className="w-4 h-4" />,
  news: <Rss className="w-4 h-4" />,
};

// arXiv feeds hidden by default — offer quick-show toggles
const ARXIV_SOURCES = [
  { key: 'arxiv_cs_ai', label: 'arXiv CS.AI' },
  { key: 'arxiv_cs_cl', label: 'arXiv CS.CL' },
];

const DEFAULT_EXCLUDE = 'arxiv_cs_ai,arxiv_cs_cl';

export default function Sidebar({ sources, filters, onChange, stats, onRefresh }) {
  const [collapsed, setCollapsed] = useState({});
  const grouped = sources.reduce((acc, s) => {
    acc[s.category] = acc[s.category] || [];
    acc[s.category].push(s);
    return acc;
  }, {});

  const excludedList = (filters.exclude_source || '').split(',').filter(Boolean);

  const handleCategoryClick = (cat) => {
    onChange({ ...filters, category: filters.category === cat ? null : cat, source: null, offset: 0 });
  };

  const handleSourceClick = (name) => {
    onChange({ ...filters, source: filters.source === name ? null : name, offset: 0 });
  };

  const toggleArxiv = (sourceKey) => {
    const current = new Set(excludedList);
    if (current.has(sourceKey)) {
      current.delete(sourceKey);
    } else {
      current.add(sourceKey);
    }
    const newExclude = Array.from(current).join(',');
    onChange({ ...filters, exclude_source: newExclude, offset: 0 });
  };

  return (
    <aside className="w-full lg:w-72 shrink-0 flex flex-col gap-6">
      <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white/40 dark:bg-gray-900/40 p-5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400">Stats</h2>
          <button onClick={onRefresh} className="text-gray-400 hover:text-gray-700 dark:text-gray-500 dark:hover:text-gray-200 transition" title="Refresh">
            <RotateCw className="w-4 h-4" />
          </button>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-lg bg-gray-100/50 dark:bg-gray-800/50 p-3">
            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.total_posts ?? 0}</div>
            <div className="text-xs text-gray-400 dark:text-gray-500">Total posts</div>
          </div>
          <div className="rounded-lg bg-gray-100/50 dark:bg-gray-800/50 p-3">
            <div className="text-2xl font-bold text-sky-600 dark:text-sky-400">{stats.unread_posts ?? 0}</div>
            <div className="text-xs text-gray-400 dark:text-gray-500">Unread</div>
          </div>
          <div className="rounded-lg bg-gray-100/50 dark:bg-gray-800/50 p-3">
            <div className="text-2xl font-bold text-amber-600 dark:text-amber-400">{stats.favorite_posts ?? 0}</div>
            <div className="text-xs text-gray-400 dark:text-gray-500">Favorites</div>
          </div>
          <div className="rounded-lg bg-gray-100/50 dark:bg-gray-800/50 p-3">
            <div className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">{stats.average_score ?? 0}</div>
            <div className="text-xs text-gray-400 dark:text-gray-500">Avg score</div>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white/40 dark:bg-gray-900/40 p-5">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-3">Filters</h2>
        <div className="flex flex-wrap gap-2 mb-4">
          <button
            onClick={() => onChange({ ...filters, is_favorite: filters.is_favorite ? null : true, offset: 0 })}
            className={`rounded-full border px-3 py-1 text-xs font-medium transition ${filters.is_favorite ? 'border-amber-500/40 bg-amber-500/15 text-amber-700 dark:text-amber-300' : 'border-gray-200 dark:border-gray-700 bg-gray-100/50 dark:bg-gray-800/50 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'}`}
          >
            Favorites
          </button>
          <button
            onClick={() => onChange({ ...filters, is_read: filters.is_read === false ? null : false, offset: 0 })}
            className={`rounded-full border px-3 py-1 text-xs font-medium transition ${filters.is_read === false ? 'border-sky-500/40 bg-sky-500/15 text-sky-700 dark:text-sky-300' : 'border-gray-200 dark:border-gray-700 bg-gray-100/50 dark:bg-gray-800/50 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'}`}
          >
            Unread only
          </button>
          <button
            onClick={() => onChange({ category: null, source: null, exclude_source: DEFAULT_EXCLUDE, search: '', min_score: 0, since: '', sort: 'score', is_read: null, is_favorite: null, offset: 0 })}
            className="rounded-full border border-gray-200 dark:border-gray-700 bg-gray-100/50 dark:bg-gray-800/50 px-3 py-1 text-xs font-medium text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition"
          >
            Reset
          </button>
        </div>

        <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-2">arXiv sources</h2>
        <p className="text-xs text-gray-400 dark:text-gray-500 mb-2">Hidden by default — click to show</p>
        <div className="flex flex-wrap gap-2 mb-4">
          {ARXIV_SOURCES.map((s) => {
            const isHidden = excludedList.includes(s.key);
            return (
              <button
                key={s.key}
                onClick={() => toggleArxiv(s.key)}
                className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium transition ${
                  !isHidden
                    ? 'border-emerald-500/40 bg-emerald-500/15 text-emerald-700 dark:text-emerald-300'
                    : 'border-gray-200 dark:border-gray-700 bg-gray-100/50 dark:bg-gray-800/50 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
                }`}
              >
                {!isHidden ? <Eye className="w-3 h-3" /> : null}
                {s.label}
              </button>
            );
          })}
        </div>

        <h2 className="text-sm font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-2">Sources</h2>
        <div className="space-y-1">
          {Object.entries(grouped).map(([cat, srcs]) => (
            <div key={cat}>
              <button
                onClick={() => {
                  setCollapsed({ ...collapsed, [cat]: !collapsed[cat] });
                  handleCategoryClick(cat);
                }}
                className={`flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-sm transition ${filters.category === cat ? 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100' : 'text-gray-500 dark:text-gray-400 hover:bg-gray-100/50 dark:hover:bg-gray-800/50 hover:text-gray-700 dark:hover:text-gray-200'}`}
              >
                {collapsed[cat] ? <ChevronRight className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                {categoryIcons[cat] || <Rss className="w-4 h-4" />}
                <span className="capitalize flex-1 text-left">{cat.replace('_', ' ')}</span>
                <span className="text-xs text-gray-400 dark:text-gray-600">{srcs.length}</span>
              </button>
              {!collapsed[cat] && (
                <div className="ml-7 mt-1 space-y-0.5">
                  {srcs.map((s) => (
                    <button
                      key={s.name}
                      onClick={() => handleSourceClick(s.name)}
                      className={`flex w-full items-center justify-between rounded-md px-2 py-1 text-xs transition ${filters.source === s.name ? 'bg-gray-100 dark:bg-gray-800 text-sky-600 dark:text-sky-300' : 'text-gray-400 dark:text-gray-500 hover:bg-gray-100/40 dark:hover:bg-gray-800/40 hover:text-gray-600 dark:hover:text-gray-300'}`}
                    >
                      <span className="truncate">{s.name.replace('reddit_', 'r/')}</span>
                      {s.post_count > 0 && <span className="text-gray-400 dark:text-gray-600 ml-2 shrink-0">{s.post_count}</span>}
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 dark:border-gray-800 bg-white/40 dark:bg-gray-900/40 p-5">
        <button
          onClick={async () => { await triggerScrape(); onRefresh(); }}
          className="w-full rounded-lg bg-sky-600 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-500 transition"
        >
          Trigger scrape now
        </button>
        <p className="mt-2 text-xs text-gray-400 dark:text-gray-500">Scrapers run automatically every 60 minutes.</p>
      </div>
    </aside>
  );
}
