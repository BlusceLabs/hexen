<script lang="ts">
  import { api, ApiError } from '@/lib/api/client';
  import type { SearchResult } from '@/lib/api/types';
  import { posterUrl } from '@/lib/utils/image';
  import { formatYear } from '@/lib/utils/format';

  let query = '';
  let results: SearchResult[] = [];
  let loading = false;
  let open = false;
  let error: string | null = null;
  let timer: ReturnType<typeof setTimeout> | undefined;
  let blurTimer: ReturnType<typeof setTimeout> | undefined;
  let selectedIndex = -1;

  async function runSearch(q: string) {
    if (!q.trim()) { results = []; open = false; error = null; return; }
    loading = true;
    error = null;
    open = true;
    try {
      const res = await api.searchMulti(q.trim(), 1);
      results = res.results.slice(0, 8);
    } catch (e) {
      results = [];
      error = e instanceof ApiError ? e.message : 'Search failed. Please try again.';
    } finally {
      loading = false;
    }
  }

  function onInput(e: Event) {
    query = (e.target as HTMLInputElement).value;
    selectedIndex = -1;
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => runSearch(query), 350);
  }

  function submit(e: Event) {
    e.preventDefault();
    if (!query.trim()) return;
    if (timer) clearTimeout(timer);
    window.location.href = `/search?q=${encodeURIComponent(query.trim())}`;
  }

  function onFocus() {
    if (blurTimer) clearTimeout(blurTimer);
    if (results.length || error) open = true;
  }

  function onBlur() {
    blurTimer = setTimeout(() => { open = false; selectedIndex = -1; }, 150);
  }

  function onKeyDown(e: KeyboardEvent) {
    if (!open) return;
    
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      selectedIndex = Math.min(selectedIndex + 1, results.length - 1);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      selectedIndex = Math.max(selectedIndex - 1, -1);
    } else if (e.key === 'Enter' && selectedIndex >= 0) {
      e.preventDefault();
      window.location.href = hrefFor(results[selectedIndex]);
    } else if (e.key === 'Escape') {
      open = false;
      selectedIndex = -1;
    }
  }

  function hrefFor(r: SearchResult): string {
    return r.media_type === 'movie' ? `/movies/${r.id}`
      : r.media_type === 'tv' ? `/tv/${r.id}`
      : `/person/${r.id}`;
  }

  function titleFor(r: SearchResult): string {
    return r.title ?? r.name ?? 'Untitled';
  }
</script>

<form class="relative flex-1 max-w-md" onsubmit={submit}>
  <div class="relative">
    <svg class="absolute left-3 top-1/2 -translate-y-1/2 text-ink-secondary" xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
      <circle cx="11" cy="11" r="8"/>
      <line x1="21" y1="21" x2="16.65" y2="16.65"/>
    </svg>
    <input
      type="text"
      value={query}
      oninput={onInput}
      onfocus={onFocus}
      onblur={onBlur}
      onkeydown={onKeyDown}
      placeholder="Search movies, TV, people…"
      class="input pl-9"
      autocomplete="off"
      aria-label="Search"
      aria-autocomplete="list"
      aria-controls="search-results"
      aria-expanded={open}
      role="combobox"
    />
  </div>

  {#if open && (query.trim() || loading)}
    <div 
      id="search-results"
      class="absolute z-50 mt-2 w-full overflow-hidden rounded-lg border border-base-border bg-base-surface shadow-2xl"
      role="listbox"
      aria-label="Search results"
    >
      {#if loading}
        <div class="flex items-center gap-2 p-4 text-sm text-ink-secondary">
          <svg class="h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Searching…
        </div>
      {:else if error}
        <div class="p-4 text-sm text-red-600" role="alert">{error}</div>
      {:else if results.length === 0}
        <div class="p-4 text-sm text-ink-secondary">No results for "{query}"</div>
      {:else}
        <ul class="max-h-96 overflow-y-auto">
          {#each results as r, i (r.id)}
            <li role="option" aria-selected={i === selectedIndex}>
              <a 
                href={hrefFor(r)} 
                class="flex items-center gap-3 p-3 transition-colors focus:outline-none focus:ring-2 focus:ring-inset focus:ring-accent {i === selectedIndex ? 'bg-base-elevated' : 'hover:bg-base-elevated'}"
                aria-label="{titleFor(r)}, {r.media_type}{formatYear(r.release_date ?? r.first_air_date) ? ', ' + formatYear(r.release_date ?? r.first_air_date) : ''}"
              >
                <div class="h-14 w-10 flex-shrink-0 overflow-hidden rounded bg-base-elevated">
                  {#if posterUrl(r.poster_path ?? r.profile_path, 'w92')}
                    <img src={posterUrl(r.poster_path ?? r.profile_path, 'w92')!} alt="" class="h-full w-full object-cover" loading="lazy" />
                  {/if}
                </div>
                <div class="min-w-0 flex-1">
                  <div class="truncate text-sm font-medium text-ink-primary">{titleFor(r)}</div>
                  <div class="text-xs text-ink-secondary capitalize">{r.media_type}{#if formatYear(r.release_date ?? r.first_air_date)} · {formatYear(r.release_date ?? r.first_air_date)}{/if}</div>
                </div>
              </a>
            </li>
          {/each}
        </ul>
        <button 
          type="submit" 
          class="block w-full border-t border-base-border p-3 text-center text-xs font-medium text-accent transition-colors hover:bg-base-elevated focus:outline-none focus:ring-2 focus:ring-inset focus:ring-accent"
        >
          See all results for "{query}"
        </button>
      {/if}
    </div>
  {/if}
</form>
