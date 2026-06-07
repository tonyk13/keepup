import React, { useEffect, useState, useCallback } from 'react';
import { Zap, Sun, Moon } from 'lucide-react';
import { useTheme } from './ThemeContext';
import { fetchPosts, fetchSources, fetchStats, markRead, markUnread, toggleFavorite } from './api';
import Sidebar from './components/Sidebar';
import FilterBar from './components/FilterBar';
import Feed from './components/Feed';

function App() {
  const { theme, toggleTheme } = useTheme();
  const [posts, setPosts] = useState([]);
  const [sources, setSources] = useState([]);
  const [stats, setStats] = useState({});
  const [filters, setFilters] = useState({
    sort: 'date',
    min_score: 75,
    since: '7d',
    limit: 30,
    offset: 0,
    exclude_source: 'arxiv_cs_ai,arxiv_cs_cl',
  });
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [p, s, st] = await Promise.all([
        fetchPosts(filters),
        fetchSources(),
        fetchStats(),
      ]);
      setPosts(p.posts);
      setTotal(p.total);
      setSources(s);
      setStats(st);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    load();
  }, [load]);

  // Auto-refresh every 60s
  useEffect(() => {
    const id = setInterval(() => load(), 60000);
    return () => clearInterval(id);
  }, [load]);

  const handleToggleRead = async (id, read) => {
    if (read) await markRead(id);
    else await markUnread(id);
    setPosts((prev) => prev.map((p) => (p.id === id ? { ...p, is_read: read } : p)));
  };

  const handleToggleFavorite = async (id) => {
    const res = await toggleFavorite(id);
    setPosts((prev) => prev.map((p) => (p.id === id ? { ...p, is_favorite: res.is_favorite } : p)));
  };

  const handlePageChange = (newOffset) => {
    setFilters((f) => ({ ...f, offset: newOffset }));
  };

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950 transition-colors">
      <header className="sticky top-0 z-50 border-b border-gray-200 dark:border-gray-800 bg-white/80 dark:bg-gray-950/80 backdrop-blur transition-colors">
        <div className="mx-auto flex max-w-7xl items-center gap-3 px-4 py-3">
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-sky-600">
                <Zap className="h-5 w-5 text-white" />
              </div>
              <h1 className="text-lg font-bold tracking-tight text-gray-900 dark:text-gray-100">KeepUp</h1>
            </div>
            <p className="hidden sm:block text-xs italic text-gray-500 dark:text-gray-400 ml-10 -mt-0.5">
              It's like every week there's something new
            </p>
          </div>
          <div className="ml-auto flex items-center gap-3">
            <span className="hidden sm:inline text-xs text-gray-400 dark:text-gray-500">Auto-refreshes every 60s</span>
            {loading && (
              <span className="inline-flex items-center gap-1.5 rounded-full border border-gray-200 dark:border-gray-800 bg-gray-100/60 dark:bg-gray-900/60 px-2.5 py-1 text-xs text-gray-500 dark:text-gray-400">
                <span className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-sky-400" />
                Updating...
              </span>
            )}
            <button
              onClick={toggleTheme}
              className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800 transition"
              title={theme === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}
            >
              {theme === 'light' ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-6">
        <div className="flex flex-col gap-6 lg:flex-row">
          <Sidebar
            sources={sources}
            filters={filters}
            onChange={setFilters}
            stats={stats}
            onRefresh={load}
          />
          <div className="flex-1 min-w-0">
            <div className="mb-5">
              <FilterBar filters={filters} onChange={setFilters} />
            </div>
            <Feed
              posts={posts}
              total={total}
              offset={filters.offset || 0}
              limit={filters.limit || 30}
              onPageChange={handlePageChange}
              onToggleRead={handleToggleRead}
              onToggleFavorite={handleToggleFavorite}
            />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
