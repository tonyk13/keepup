import React, { useState } from 'react';
import PostCard from './PostCard';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export default function Feed({ posts, total, offset, limit, onPageChange, onToggleRead, onToggleFavorite }) {
  const [expandedId, setExpandedId] = useState(null);
  const pages = Math.ceil(total / limit) || 1;
  const currentPage = Math.floor(offset / limit) + 1;

  return (
    <div className="flex flex-col gap-4">
      {posts.length === 0 && (
        <div className="rounded-xl border border-dashed border-gray-200 dark:border-gray-800 bg-gray-50/30 dark:bg-gray-900/30 p-10 text-center text-gray-400 dark:text-gray-500">
          No posts match your filters.
        </div>
      )}
      {posts.map((post) => (
        <PostCard
          key={post.id}
          post={post}
          onToggleRead={onToggleRead}
          onToggleFavorite={onToggleFavorite}
        />
      ))}

      {pages > 1 && (
        <div className="flex items-center justify-between pt-2">
          <button
            onClick={() => onPageChange(Math.max(0, offset - limit))}
            disabled={offset === 0}
            className="flex items-center gap-1 rounded-lg border border-gray-200 dark:border-gray-800 bg-white/60 dark:bg-gray-900/60 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-40 disabled:cursor-not-allowed transition"
          >
            <ChevronLeft className="w-4 h-4" /> Previous
          </button>
          <span className="text-sm text-gray-400 dark:text-gray-500">
            Page {currentPage} of {pages}
          </span>
          <button
            onClick={() => onPageChange(offset + limit)}
            disabled={offset + limit >= total}
            className="flex items-center gap-1 rounded-lg border border-gray-200 dark:border-gray-800 bg-white/60 dark:bg-gray-900/60 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 disabled:opacity-40 disabled:cursor-not-allowed transition"
          >
            Next <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}
