<script lang="ts">
  let { initialQuery = '', autofocus = false } = $props();

  let query = $state(initialQuery);
  let inputEl: HTMLInputElement | undefined = $state(undefined);
  let focused = $state(false);

  function onSubmit(e: Event) {
    e.preventDefault();
    if (query.trim()) {
      window.location.href = '/search?q=' + encodeURIComponent(query.trim());
    }
  }

  function onKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      query = '';
      inputEl?.blur();
    }
  }

  $effect(() => {
    function handleKeydown(e: KeyboardEvent) {
      if (e.key === '/' && !e.ctrlKey && !e.metaKey && !e.altKey) {
        const tag = (e.target as HTMLElement)?.tagName;
        if (tag !== 'INPUT' && tag !== 'TEXTAREA') {
          e.preventDefault();
          inputEl?.focus();
        }
      }
    }
    document.addEventListener('keydown', handleKeydown);
    return () => document.removeEventListener('keydown', handleKeydown);
  });
</script>

<form class="search-bar" class:focused onsubmit={onSubmit} role="search">
  <span class="search-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/>
              <path d="M21 21l-4.35-4.35"/>
            </svg>
          </span>
  <input
    bind:this={inputEl}
    bind:value={query}
    type="text"
    placeholder="Search movies, TV shows, people..."
    autocomplete="off"
    aria-label="Search"
    {autofocus}
    onfocus={() => focused = true}
    onblur={() => focused = false}
    onkeydown={onKeydown}
  />
  {#if query}
    <button type="button" class="clear-btn" onclick={() => { query = ''; inputEl?.focus(); }} aria-label="Clear search">✕</button>
  {/if}
  <button type="submit" class="submit-btn">Search</button>
</form>

<style>
  .search-bar {
    display: flex;
    align-items: center;
    max-width: 700px;
    margin: 0 auto;
    background: var(--bg-card);
    border: 2px solid var(--border);
    border-radius: var(--radius-xl);
    overflow: hidden;
    transition: border-color 0.3s, box-shadow 0.3s;
  }

  .search-bar.focused {
    border-color: var(--accent);
    box-shadow: 0 0 0 4px rgba(255, 45, 85, 0.15);
  }

  .search-icon {
    padding: 0 0 0 18px;
    font-size: 18px;
    opacity: 0.6;
  }

  input {
    flex: 1;
    background: none;
    border: none;
    outline: none;
    color: var(--text-primary);
    padding: 16px 12px;
    font-size: 16px;
    font-family: inherit;
  }

  input::placeholder {
    color: var(--text-tertiary);
  }

  .clear-btn {
    background: none;
    border: none;
    color: var(--text-secondary);
    font-size: 18px;
    padding: 8px 12px;
    cursor: pointer;
    transition: color 0.2s;
  }

  .clear-btn:hover {
    color: var(--text-primary);
  }

  .submit-btn {
    background: var(--accent-gradient);
    border: none;
    color: white;
    padding: 16px 28px;
    font-size: 14px;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    transition: opacity 0.2s;
  }

  .submit-btn:hover {
    opacity: 0.9;
  }
</style>