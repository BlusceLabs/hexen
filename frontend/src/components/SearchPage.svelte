<script lang="ts">
  import SearchBar from './SearchBar.svelte';

  let { initialQuery = '', initialResults = [], initialError = false } = $props();

  let query = $state(initialQuery);
  let results = $state(initialResults);
  let loading = $state(false);
  let error = $state(initialError);
  let activeFilter = $state('all');
  let debounceTimer: ReturnType<typeof setTimeout>;

  let filteredResults = $derived(activeFilter === 'all' ? results : results.filter((r: any) => r.media_type === activeFilter));
  let movieCount = $derived(results.filter((r: any) => r.media_type === 'movie').length);
  let tvCount = $derived(results.filter((r: any) => r.media_type === 'tv').length);
  let personCount = $derived(results.filter((r: any) => r.media_type === 'person').length);

  function onInput(e: Event) {
    const val = (e.target as HTMLInputElement).value;
    query = val;
    clearTimeout(debounceTimer);
    if (!val.trim()) { results = []; return; }
    loading = true;
    debounceTimer = setTimeout(() => {
      window.location.href = '/search?q=' + encodeURIComponent(val.trim());
    }, 600);
  }

  function setFilter(filter: string) { activeFilter = filter; }
</script>

<div class="search-page">
  <div class="search-hero">
    <h1 class="search-title">{query ? `Results for "${query}"` : 'Search'}</h1>
    <div class="search-wrapper">
      <SearchBar {initialQuery} autofocus={!initialQuery} />
    </div>
    <p class="hint">Press <kbd>/</kbd> anywhere to focus search</p>
  </div>

  {#if loading}
    <div class="loading">
      <div class="spinner"></div>
      <p>Searching...</p>
    </div>
  {:else if error}
    <div class="empty-state">
      <span class="empty-icon">[!]</span>
      <p>Search failed. <a href="/search">Try again</a></p>
    </div>
  {:else if query && filteredResults.length > 0}
    <div class="container">
      <div class="chips" style="margin-bottom:20px">
        <button class="chip" class:active={activeFilter === 'all'} onclick={() => setFilter('all')}>All ({results.length})</button>
        {#if movieCount > 0}<button class="chip" class:active={activeFilter === 'movie'} onclick={() => setFilter('movie')}>Movies ({movieCount})</button>{/if}
        {#if tvCount > 0}<button class="chip" class:active={activeFilter === 'tv'} onclick={() => setFilter('tv')}>TV ({tvCount})</button>{/if}
        {#if personCount > 0}<button class="chip" class:active={activeFilter === 'person'} onclick={() => setFilter('person')}>People ({personCount})</button>{/if}
      </div>

      <div class="results-list">
        {#each filteredResults as item (item.id)}
          <a href={`/${item.media_type}/${item.id}`} class="search-result">
            <div class="result-thumb">
              {#if item.poster}
                <img src={item.poster} alt={item.title} loading="lazy" />
              {:else}
                <div class="thumb-ph">—</div>
              {/if}
              <span class="type-badge">{item.media_type}</span>
              {#if item.rating > 0}
                <span class="rating-badge">{(item.rating / 10).toFixed(1)}</span>
              {/if}
            </div>
            <div class="result-info">
              <h3>{item.title}</h3>
              {#if item.year}
                <span class="result-year">{item.year}</span>
              {/if}
              {#if item.overview}
                <p class="result-overview">{item.overview.slice(0, 180)}{item.overview.length > 180 ? '...' : ''}</p>
              {/if}
            </div>
          </a>
        {/each}
      </div>
    </div>
  {:else if query}
    <div class="empty-state">
      <span class="empty-icon">[?]</span>
      <p>No results for "<strong>{query}</strong>"</p>
      <p class="empty-hint">Try different keywords or check spelling</p>
    </div>
  {:else}
    <div class="container suggestions-wrapper">
      <div class="suggestions">
        <h2>Popular Searches</h2>
        <div class="suggestion-grid">
          <a href="/search?q=Avatar" class="suggestion">Avatar</a>
          <a href="/search?q=Breaking Bad" class="suggestion">Breaking Bad</a>
          <a href="/search?q=Inception" class="suggestion">Inception</a>
          <a href="/search?q=Game of Thrones" class="suggestion">Game of Thrones</a>
          <a href="/search?q=Marvel" class="suggestion">Marvel</a>
          <a href="/search?q=Stranger Things" class="suggestion">Stranger Things</a>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .search-page { min-height: 80vh; }

  .search-hero {
    text-align: center;
    padding: 60px 0 30px;
  }

  .search-title {
    font-size: 36px;
    font-weight: 600;
    margin-bottom: 24px;
    letter-spacing: -0.02em;
  }

  .search-wrapper {
    margin-bottom: 16px;
  }

  .hint {
    margin-top: 10px;
    font-size: 13px;
    color: var(--text-secondary);
  }

  .hint kbd {
    padding: 3px 10px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    font-family: monospace;
    font-size: 12px;
    letter-spacing: 0.5px;
  }

  .loading {
    text-align: center;
    padding: 80px 0;
  }

  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--border);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin: 0 auto 12px;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .results-list {
    max-width: 800px;
  }

  .search-result {
    display: flex;
    gap: 20px;
    padding: 16px 0;
    border-bottom: 1px solid var(--border);
    transition: background 0.2s;
  }

  .search-result:hover {
    background: var(--bg-hover);
  }

  .result-thumb {
    width: 360px;
    aspect-ratio: 16/9;
    border-radius: var(--radius);
    overflow: hidden;
    flex-shrink: 0;
    background: var(--bg-card);
    position: relative;
  }

  .result-thumb img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .thumb-ph {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    opacity: 0.3;
  }

  .type-badge {
    position: absolute;
    top: 10px;
    left: 10px;
    padding: 3px 10px;
    border-radius: var(--radius-sm);
    font-size: 11px;
    font-weight: 600;
    color: white;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    background: var(--accent);
  }

  .rating-badge {
    position: absolute;
    top: 10px;
    right: 10px;
    padding: 3px 10px;
    background: rgba(0, 0, 0, 0.85);
    border-radius: var(--radius-sm);
    font-size: 11px;
    font-weight: 600;
    color: var(--gold);
  }

  .result-info {
    padding: 4px 0;
    min-width: 0;
  }

  .result-info h3 {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 6px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    letter-spacing: -0.01em;
  }

  .result-year {
    font-size: 14px;
    color: var(--text-secondary);
    display: block;
    margin-bottom: 10px;
  }

  .result-overview {
    font-size: 14px;
    color: var(--text-secondary);
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .empty-state {
    text-align: center;
    padding: 80px 24px;
  }

  .empty-icon {
    font-size: 32px;
    display: block;
    margin-bottom: 12px;
    opacity: 0.5;
    font-family: monospace;
  }

  .empty-state p {
    font-size: 16px;
    color: var(--text-secondary);
  }

  .empty-hint {
    font-size: 14px;
    margin-top: 6px;
  }

  .suggestions-wrapper {
    padding: 40px 0 80px;
  }

  .suggestions {
    text-align: center;
    padding: 40px 0;
  }

  .suggestions h2 {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 20px;
    color: var(--text-secondary);
    letter-spacing: -0.01em;
  }

  .suggestion-grid {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 10px;
  }

  .suggestion {
    padding: 10px 24px;
    background: var(--bg-chip);
    border-radius: var(--radius-xl);
    font-size: 14px;
    font-weight: 500;
    transition: all 0.2s ease;
    letter-spacing: -0.01em;
  }

  .suggestion:hover {
    background: var(--bg-hover);
    transform: scale(1.03);
  }

  @media (max-width: 768px) {
    .search-result {
      flex-direction: column;
    }

    .result-thumb {
      width: 100%;
    }

    .search-title {
      font-size: 28px;
    }

    .search-hero {
      padding: 40px 0 20px;
    }

    .suggestion-grid {
      gap: 8px;
    }
  }
</style>