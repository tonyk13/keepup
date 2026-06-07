import React from 'react';
import { Search, SlidersHorizontal, ArrowUpDown, Calendar } from 'lucide-react';

const DATE_OPTIONS = [
  { value: '', label: 'All time' },
  { value: '7d', label: 'Past week' },
  { value: '30d', label: 'Past month' },
  { value: '90d', label: 'Past 3 months' },
  { value: '180d', label: 'Past 6 months' },
  { value: '365d', label: 'Past year' },
];

export default function FilterBar({ filters, onChange }) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div className="relative w-full sm:w-80">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-gray-500" />
        <input
          type="text"
          placeholder="Search posts..."
          value={filters.search || ''}
          onChange={(e) => onChange({ ...filters, search: e.target.value, offset: 0 })}
          className="w-full rounded-lg border border-gray-200 dark:border-gray-800 bg-white/60 dark:bg-gray-900/60 py-2 pl-9 pr-3 text-sm text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:border-sky-500 focus:outline-none"
        />
      </div>
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="w-4 h-4 text-gray-400 dark:text-gray-500" />
          <span className="text-xs text-gray-400 dark:text-gray-500 uppercase tracking-wide font-semibold">Min score</span>
          <input
            type="range"
            min={0}
            max={90}
            step={5}
            value={filters.min_score || 0}
            onChange={(e) => onChange({ ...filters, min_score: Number(e.target.value), offset: 0 })}
            className="w-24 accent-sky-500"
          />
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300 w-8">{filters.min_score || 0}</span>
        </div>
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-gray-400 dark:text-gray-500" />
          <select
            value={filters.since || ''}
            onChange={(e) => onChange({ ...filters, since: e.target.value, offset: 0 })}
            className="rounded-lg border border-gray-200 dark:border-gray-800 bg-white/60 dark:bg-gray-900/60 py-1.5 px-2 text-sm text-gray-900 dark:text-gray-100 focus:border-sky-500 focus:outline-none"
          >
            {DATE_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
        <div className="flex items-center gap-2">
          <ArrowUpDown className="w-4 h-4 text-gray-400 dark:text-gray-500" />
          <select
            value={filters.sort || 'score'}
            onChange={(e) => onChange({ ...filters, sort: e.target.value })}
            className="rounded-lg border border-gray-200 dark:border-gray-800 bg-white/60 dark:bg-gray-900/60 py-1.5 px-2 text-sm text-gray-900 dark:text-gray-100 focus:border-sky-500 focus:outline-none"
          >
            <option value="score">Top Score</option>
            <option value="date">Newest</option>
          </select>
        </div>
      </div>
    </div>
  );
}
