<script lang="ts">
  import type { SearchResult } from '@/lib/api/types';
  import { posterUrl } from '@/lib/utils/image';

  interface Props {
    title: string;
    items: SearchResult[];
    href?: string;
  }

  let { title, items, href }: Props = $props();

  let scrollContainer: HTMLDivElement;
  let canScrollLeft = $state(false);
  let canScrollRight = $state(true);

  function updateScrollButtons() {
    if (!scrollContainer) return;
    canScrollLeft = scrollContainer.scrollLeft > 0;
    canScrollRight = 
      scrollContainer.scrollLeft < scrollContainer.scrollWidth - scrollContainer.clientWidth - 10;
  }

  function scroll(direction: 'left' | 'right') {
    if (!scrollContainer) return;
    const scrollAmount = scrollContainer.clientWidth * 0.8;
    scrollContainer.scrollBy({
      left: direction === 'left' ? -scrollAmount : scrollAmount,
      behavior: 'smooth'
    });
    setTimeout(updateScrollButtons, 300);
  }

  function titleFor(item: SearchResult): string {
    return item.title ?? item.name ?? 'Untitled';
  }

  function hrefFor(item: SearchResult): string {
    return item.media_type === 'tv' ? `/tv/${item.id}` : `/movies/${item.id}`;
  }

  function yearFor(item: SearchResult): string | null {
    const date = item.release_date ?? item.first_air_date;
    return date ? new Date(date).getFullYear().toString() : null;
  }
</script>

<section class="group relative py-8">
  <div class="container-content mb-4 flex items-center justify-between">
    <h2 class="text-2xl font-bold text-ink-primary">{title}</h2>
    {#if href}
      <a 
        {href}
        class="text-sm font-medium text-accent hover:underline focus:outline-none focus:ring-2 focus:ring-accent rounded"
      >
        View All →
      </a>
    {/if}
  </div>

  <div class="relative">
    <!-- Left scroll button -->
    {#if canScrollLeft}
      <button
        type="button"
        onclick={() => scroll('left')}
        class="absolute left-0 top-0 z-10 flex h-full w-12 items-center justify-center bg-gradient-to-r from-base to-transparent opacity-0 transition-opacity group-hover:opacity-100 focus:opacity-100 focus:outline-none focus:ring-2 focus:ring-accent"
        aria-label="Scroll left"
      >
        <svg class="h-8 w-8 text-white drop-shadow-lg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
    {/if}

    <!-- Carousel -->
    <div 
      bind:this={scrollContainer}
      onscroll={updateScrollButtons}
      class="no-scrollbar container-content flex gap-3 overflow-x-auto scroll-smooth"
    >
      {#each items as item (item.id)}
        <a
          href={hrefFor(item)}
          class="group/card relative flex-shrink-0 w-[150px] sm:w-[180px] md:w-[200px] transition-transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-accent rounded-lg"
        >
          <div class="relative aspect-[2/3] overflow-hidden rounded-lg bg-base-elevated shadow-lg">
            {#if posterUrl(item.poster_path, 'w342')}
              <img
                src={posterUrl(item.poster_path, 'w342')!}
                alt={titleFor(item)}
                class="h-full w-full object-cover transition-opacity group-hover/card:opacity-75"
                loading="lazy"
              />
            {:else}
              <div class="flex h-full items-center justify-center bg-base-elevated">
                <svg class="h-12 w-12 text-ink-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
                </svg>
              </div>
            {/if}
            
            <!-- Rating badge -->
            {#if item.vote_average && item.vote_average > 0}
              <div class="absolute right-2 top-2 rounded bg-black/80 px-2 py-1 text-xs font-bold text-white backdrop-blur">
                ⭐ {item.vote_average.toFixed(1)}
              </div>
            {/if}
          </div>

          <div class="mt-2 px-1">
            <h3 class="text-sm font-medium text-ink-primary line-clamp-2 group-hover/card:text-accent transition-colors">
              {titleFor(item)}
            </h3>
            {#if yearFor(item)}
              <p class="text-xs text-ink-secondary">{yearFor(item)}</p>
            {/if}
          </div>
        </a>
      {/each}
    </div>

    <!-- Right scroll button -->
    {#if canScrollRight}
      <button
        type="button"
        onclick={() => scroll('right')}
        class="absolute right-0 top-0 z-10 flex h-full w-12 items-center justify-center bg-gradient-to-l from-base to-transparent opacity-0 transition-opacity group-hover:opacity-100 focus:opacity-100 focus:outline-none focus:ring-2 focus:ring-accent"
        aria-label="Scroll right"
      >
        <svg class="h-8 w-8 text-white drop-shadow-lg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
        </svg>
      </button>
    {/if}
  </div>
</section>
