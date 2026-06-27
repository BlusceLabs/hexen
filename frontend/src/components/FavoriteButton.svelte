<script lang="ts">
  import { isFavorite, toggleFavorite } from '../lib/favorites';

  let { id, title = '', poster = '', year = '', media_type = 'movie' } = $props();

  let favorited = $state(false);

  $effect(() => {
    if (typeof window !== 'undefined') {
      favorited = isFavorite(id, media_type);
    }
  });

  function handleToggle(e: Event) {
    e.preventDefault();
    e.stopPropagation();
    if (media_type !== 'movie' && media_type !== 'tv') return;
    favorited = toggleFavorite({ id, title, poster, year, media_type });

    const event = new CustomEvent('favorite-toggle', {
      detail: { id, media_type, favorited },
      bubbles: true,
    });
    dispatchEvent(event);
  }
</script>

<button
  class="fav-btn"
  class:active={favorited}
  onclick={handleToggle}
  aria-label={favorited ? 'Remove from favorites' : 'Add to favorites'}
  aria-pressed={favorited}
>
  <svg class="fav-icon" width="18" height="18" viewBox="0 0 24 24" fill={favorited ? 'currentColor' : 'none'} stroke="currentColor" stroke-width="2">
    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78L12 21.29l8.84-8.84a5.5 5.5 0 0 0 0-7.78z"/>
  </svg>
</button>

<style>
  .fav-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: var(--bg-chip);
    border: 1px solid var(--border);
    cursor: pointer;
    transition: all 0.2s ease;
  }
  .fav-btn:hover {
    background: var(--bg-hover);
    border-color: var(--accent);
  }
  .fav-btn.active {
    background: var(--accent);
    color: white;
    border-color: var(--accent);
  }
  .fav-icon {
    transition: transform 0.2s;
  }
  .fav-btn:hover .fav-icon { transform: scale(1.1); }
</style>