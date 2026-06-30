<script lang="ts">
  interface Props {
    videos: { id: string; key: string; name: string; site: string; type: string; official: boolean }[];
  }
  let { videos }: Props = $props();

  let open = $state(false);
  let activeKey = $state('');
  let activeName = $state('');

  // Prefer official YouTube trailers, fall back to any YouTube video
  let playable = $derived(
    videos.filter(v => v.site === 'YouTube' && (v.type === 'Trailer' || v.type === 'Teaser' || v.type === 'Clip'))
  );

  function play(key: string, name: string) {
    activeKey = key;
    activeName = name;
    open = true;
    document.body.style.overflow = 'hidden';
  }

  function close() {
    open = false;
    activeKey = '';
    document.body.style.overflow = '';
  }

  function onKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') close();
  }
</script>

<svelte:window on:keydown={onKeydown} />

{#if playable.length > 0}
  <div class="mt-8">
    <h2 class="mb-3 text-xl font-bold">Videos & Trailers</h2>
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {#each playable.slice(0, 6) as v (v.id)}
        <button
          type="button"
          onclick={() => play(v.key, v.name)}
          class="group relative overflow-hidden rounded-lg bg-base-surface text-left"
        >
          <div class="relative aspect-video bg-base-elevated">
            <img
              src={`https://i.ytimg.com/vi/${v.key}/hqdefault.jpg`}
              alt={v.name}
              class="h-full w-full object-cover transition-opacity group-hover:opacity-80"
              loading="lazy"
            />
            <div class="absolute inset-0 flex items-center justify-center bg-black/30 opacity-0 transition-opacity group-hover:opacity-100">
              <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="white">
                <path d="M8 5v14l11-7z" />
              </svg>
            </div>
          </div>
          <p class="p-2 text-sm font-medium truncate">{v.name}</p>
        </button>
      {/each}
    </div>
  </div>
{/if}

{#if open && activeKey}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4"
    onclick={close}
    role="dialog"
    aria-modal="true"
    aria-label={activeName}
  >
    <div class="relative w-full max-w-4xl" onclick={(e) => e.stopPropagation()}>
      <div class="mb-2 flex items-center justify-between">
        <p class="truncate text-sm text-ink-secondary">{activeName}</p>
        <button type="button" onclick={close} class="btn-ghost p-1" aria-label="Close">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
        </button>
      </div>
      <div class="aspect-video overflow-hidden rounded-lg bg-black">
        <iframe
          src={`https://www.youtube.com/embed/${activeKey}?autoplay=1&rel=0`}
          title={activeName}
          class="h-full w-full"
          allow="autoplay; encrypted-media; fullscreen"
          allowfullscreen
        ></iframe>
      </div>
    </div>
  </div>
{/if}
