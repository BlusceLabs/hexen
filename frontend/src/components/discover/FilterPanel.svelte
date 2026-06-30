<script lang="ts">
  import { api } from '@/lib/api/client';
  import type { Genre } from '@/lib/api/types';

  interface Props {
    type: 'movie' | 'tv';
    genres: Genre[];
    initialFilters: Record<string, string>;
  }
  let { type, genres, initialFilters }: Props = $props();

  let mediaType = $state(type);
  let sortBy = $state(initialFilters.sort_by ?? 'popularity.desc');
  let selectedGenres = $state<Set<number>>(
    new Set((initialFilters.with_genres ?? '').split(',').filter(Boolean).map(Number))
  );
  let yearFrom = $state(initialFilters['primary_release_date.gte'] ?? '');
  let yearTo = $state(initialFilters['primary_release_date.lte'] ?? '');
  let minRating = $state(Number(initialFilters['vote_average.gte'] ?? '0'));
  let language = $state(initialFilters.with_original_language ?? '');

  function toggleGenre(id: number) {
    if (selectedGenres.has(id)) selectedGenres.delete(id);
    else selectedGenres.add(id);
    selectedGenres = new Set(selectedGenres);
  }

  function buildParams(): Record<string, string> {
    const params: Record<string, string> = { sort_by: sortBy };
    if (selectedGenres.size > 0) params.with_genres = [...selectedGenres].join(',');
    if (minRating > 0) params['vote_average.gte'] = String(minRating);
    if (language) params.with_original_language = language;
    if (yearFrom) {
      params[mediaType === 'movie' ? 'primary_release_date.gte' : 'first_air_date.gte'] = `${yearFrom}-01-01`;
    }
    if (yearTo) {
      params[mediaType === 'movie' ? 'primary_release_date.lte' : 'first_air_date.lte'] = `${yearTo}-12-31`;
    }
    return params;
  }

  function apply() {
    const params = buildParams();
    const qs = new URLSearchParams({ type: mediaType, ...params }).toString();
    window.location.href = `/discover?${qs}`;
  }

  function reset() {
    selectedGenres = new Set();
    sortBy = 'popularity.desc';
    yearFrom = '';
    yearTo = '';
    minRating = 0;
    language = '';
    window.location.href = '/discover';
  }
</script>

<div class="card-surface sticky top-20 p-4">
  <h3 class="mb-4 text-lg font-bold">Filters</h3>

  <!-- Type toggle -->
  <div class="mb-4">
    <label class="mb-1.5 block text-xs text-ink-secondary">Type</label>
    <div class="flex gap-2">
      <button
        type="button"
        class:list={["chip flex-1 justify-center", mediaType === 'movie' && 'chip-active']}
        onclick={() => { mediaType = 'movie'; }}
      >Movies</button>
      <button
        type="button"
        class:list={["chip flex-1 justify-center", mediaType === 'tv' && 'chip-active']}
        onclick={() => { mediaType = 'tv'; }}
      >TV Shows</button>
    </div>
  </div>

  <!-- Sort -->
  <div class="mb-4">
    <label for="sort" class="mb-1.5 block text-xs text-ink-secondary">Sort by</label>
    <select id="sort" class="input" bind:value={sortBy}>
      <option value="popularity.desc">Popularity ↓</option>
      <option value="popularity.asc">Popularity ↑</option>
      <option value="vote_average.desc">Rating ↓</option>
      <option value="vote_average.asc">Rating ↑</option>
      <option value="release_date.desc">Release Date ↓</option>
      <option value="release_date.asc">Release Date ↑</option>
      <option value="revenue.desc">Revenue ↓</option>
      <option value="title.asc">Title A-Z</option>
    </select>
  </div>

  <!-- Genres -->
  <div class="mb-4">
    <label class="mb-1.5 block text-xs text-ink-secondary">Genres</label>
    <div class="flex flex-wrap gap-1.5">
      {#each genres as g (g.id)}
        <button
          type="button"
          class:list={["chip text-xs", selectedGenres.has(g.id) && 'chip-active']}
          onclick={() => toggleGenre(g.id)}
        >{g.name}</button>
      {/each}
    </div>
  </div>

  <!-- Year range -->
  <div class="mb-4">
    <label class="mb-1.5 block text-xs text-ink-secondary">Year range</label>
    <div class="flex items-center gap-2">
      <input type="number" class="input" placeholder="From" min="1900" max="2099" bind:value={yearFrom} />
      <span class="text-ink-secondary">—</span>
      <input type="number" class="input" placeholder="To" min="1900" max="2099" bind:value={yearTo} />
    </div>
  </div>

  <!-- Min rating -->
  <div class="mb-4">
    <label for="rating" class="mb-1.5 block text-xs text-ink-secondary">Min rating: {minRating}</label>
    <input id="rating" type="range" min="0" max="10" step="0.5" class="w-full accent-accent" bind:value={minRating} />
  </div>

  <!-- Language -->
  <div class="mb-4">
    <label for="lang" class="mb-1.5 block text-xs text-ink-secondary">Language</label>
    <select id="lang" class="input" bind:value={language}>
      <option value="">Any</option>
      <option value="en">English</option>
      <option value="ja">Japanese</option>
      <option value="ko">Korean</option>
      <option value="es">Spanish</option>
      <option value="fr">French</option>
      <option value="de">German</option>
      <option value="hi">Hindi</option>
      <option value="zh">Chinese</option>
      <option value="it">Italian</option>
      <option value="pt">Portuguese</option>
    </select>
  </div>

  <div class="flex gap-2">
    <button type="button" class="btn-primary flex-1" onclick={apply}>Apply</button>
    <button type="button" class="btn-ghost" onclick={reset}>Reset</button>
  </div>
</div>
