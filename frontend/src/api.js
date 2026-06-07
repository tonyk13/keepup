const API_BASE = '';

export async function fetchPosts(params = {}) {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') qs.set(k, String(v));
  });
  const res = await fetch(`${API_BASE}/api/posts?${qs.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch posts');
  return res.json();
}

export async function fetchSources() {
  const res = await fetch(`${API_BASE}/api/sources`);
  if (!res.ok) throw new Error('Failed to fetch sources');
  return res.json();
}

export async function fetchStats() {
  const res = await fetch(`${API_BASE}/api/stats`);
  if (!res.ok) throw new Error('Failed to fetch stats');
  return res.json();
}

export async function markRead(id) {
  const res = await fetch(`${API_BASE}/api/posts/${id}/read`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to mark read');
  return res.json();
}

export async function markUnread(id) {
  const res = await fetch(`${API_BASE}/api/posts/${id}/unread`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to mark unread');
  return res.json();
}

export async function toggleFavorite(id) {
  const res = await fetch(`${API_BASE}/api/posts/${id}/favorite`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to toggle favorite');
  return res.json();
}

export async function triggerScrape() {
  const res = await fetch(`${API_BASE}/api/trigger-scrape`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to trigger scrape');
  return res.json();
}
