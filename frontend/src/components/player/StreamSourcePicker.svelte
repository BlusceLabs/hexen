<script lang="ts">
  import { api, ApiError } from '@/lib/api/client';
  import type { StreamInfo } from '@/lib/api/types';

  interface Props {
    query: string;
    isTv?: boolean;
    initialSeason?: number;
    initialEpisode?: number;
  }
  let { query, isTv = false, initialSeason = 1, initialEpisode = 1 }: Props = $props();

  let info = $state<StreamInfo | null>(null);
  let loading = $state(true);
  let error = $state('');
  let selectedUrl = $state('');
  let season = $state(initialSeason);
  let episode = $state(initialEpisode);

  async function load() {
    loading = true;
    error = '';
    info = null;
    selectedUrl = '';
    try {
      info = isTv
        ? await api.streamTv(query, season, episode)
        : await api.streamInfo(query);
      if (info.downloads.length > 0) {
        selectedUrl = info.downloads[0].url;
      }
    } catch (e: any) {
      error = e instanceof ApiError ? e.message : 'Failed to fetch stream info';
    } finally {
      loading = false;
    }
  }

  function select(url: string) {
    selectedUrl = url;
  }

  function reloadTv() {
    load();
  }

  $effect(() => { load(); });

  // Expose selectedUrl to parent via callback prop
  interface PropsWithCallback extends Props {
    onselect?: (url: string) => void;
  }
</script>

<div class="card-surface p-4">
  <h3 class="mb-3 text-lg font-bold">Stream Sources</h3>
  <p class="mb-3 text-sm text-ink-secondary">
    Searching Moviebox for: <span class="font-medium text-ink-primary">{query}</span>
  </p>

  {#if isTv}
    <div class="mb-4 flex items-end gap-2">
      <div>
        <label for="season" class="mb-1 block text-xs text-ink-secondary">Season</label>
        <input id="season" type="number" min="1" class="input w-24" bind:value={season} />
      </div>
      <div>
        <label for="episode" class="mb-1 block text-xs text-ink-secondary">Episode</label>
        <input id="episode" type="number" min="1" class="input w-24" bind:value={episode} />
      </div>
      <button type="button" class="btn-primary" onclick={reloadTv}>Load</button>
    </div>
  {/if}

  {#if loading}
    <div class="space-y-2">
      {#each Array(3) as _}
        <div class="skeleton h-12 w-full"></div>
      {/each}
    </div>
  {:else if error}
    <div class="rounded-lg border border-red-500/30 bg-red-500/10 p-4">
      <p class="text-sm text-red-400">{error}</p>
    </div>
  {:else if info}
    {#if !info.has_resource || info.downloads.length === 0}
      <div class="rounded-lg border border-yellow-500/30 bg-yellow-500/10 p-4">
        <p class="text-sm text-yellow-400">No streamable source found for "{info.title}".</p>
        <p class="mt-1 text-xs text-ink-secondary">This title may not be available on Moviebox.</p>
      </div>
    {:else}
      <div class="space-y-2">
        {#each info.downloads as d (d.url)}
          <button
            type="button"
            onclick={() => select(d.url)}
            class:list={[
              "flex w-full items-center justify-between gap-3 rounded-lg border p-3 text-left transition-colors",
              selectedUrl === d.url
                ? "border-accent bg-accent/10"
                : "border-base-border bg-base-elevated hover:bg-base-surface"
            ]}
          >
            <div class="flex items-center gap-3">
              <span class="text-sm font-bold uppercase">{d.resolution}</span>
              {#if d.ext}<span class="text-xs text-ink-secondary">.{d.ext}</span>{/if}
            </div>
            <div class="flex items-center gap-3 text-xs text-ink-secondary">
              {#if d.size}<span>{d.size}</span>{/if}
              {#if selectedUrl === d.url}
                <span class="text-accent">● Selected</span>
              {/if}
            </div>
          </button>
        {/each}
      </div>
      <p class="mt-3 text-xs text-ink-secondary">
        Pick a resolution, then use the player below. The stream is proxied through the backend.
      </p>
    {/if}
  {/if}
</div>

{#snippet player(url: string)}
  {#if url}
    <div class="mt-4 overflow-hidden rounded-lg bg-black">
      <video
        controls
        autoplay
        class="aspect-video w-full"
        src={api.proxyUrl(url)}
      ></video>
    </div>
  {/if}
{/snippet}

{#if selectedUrl}
  {@render player(selectedUrl)}
{/if}
