<script lang="ts">
  import { api } from '@/lib/api/client';
  import type { Season, Episode } from '@/lib/api/types';
  import { stillUrl } from '@/lib/utils/image';
  import { formatDate } from '@/lib/utils/format';

  interface SimpleSeason {
    season_number: number;
    name: string;
    episode_count: number;
  }
  interface Props {
    showId: number;
    seasons: SimpleSeason[];
    initialSeason: Season | null;
  }
  let { showId, seasons, initialSeason }: Props = $props();

  let currentSeasonNum = $state(initialSeason?.season_number ?? seasons[0]?.season_number ?? 1);
  let episodes = $state<Episode[]>(initialSeason?.episodes ?? []);
  let loading = $state(false);
  let error = $state('');

  async function loadSeason(num: number) {
    currentSeasonNum = num;
    loading = true;
    error = '';
    try {
      const data = await api.tvSeason(showId, num);
      episodes = data.episodes ?? [];
    } catch (e: any) {
      error = e?.message ?? 'Failed to load season';
      episodes = [];
    } finally {
      loading = false;
    }
  }

  function selectSeason(num: number) {
    if (num === currentSeasonNum) return;
    loadSeason(num);
  }
</script>

<section class="mt-8">
  <div class="mb-4 flex items-center justify-between">
    <h2 class="text-xl font-bold">Episodes</h2>
    {#if seasons.length > 1}
      <select
        class="input max-w-xs"
        value={currentSeasonNum}
        onchange={(e) => selectSeason(Number((e.target as HTMLSelectElement).value))}
      >
        {#each seasons as s (s.season_number)}
          <option value={s.season_number}>{s.name} ({s.episode_count} eps)</option>
        {/each}
      </select>
    {/if}
  </div>

  {#if loading}
    <div class="space-y-3">
      {#each Array(5) as _, i}
        <div class="flex gap-4 rounded-lg bg-base-surface p-3">
          <div class="skeleton aspect-video w-48 flex-shrink-0"></div>
          <div class="flex-1 space-y-2">
            <div class="skeleton h-5 w-1/3"></div>
            <div class="skeleton h-4 w-full"></div>
            <div class="skeleton h-4 w-2/3"></div>
          </div>
        </div>
      {/each}
    </div>
  {:else if error}
    <p class="text-red-400">{error}</p>
  {:else if episodes.length === 0}
    <p class="text-ink-secondary">No episodes found for this season.</p>
  {:else}
    <div class="space-y-3">
      {#each episodes as ep (ep.id)}
        <a
          href={`/watch/tv/${showId}?season=${currentSeasonNum}&episode=${ep.episode_number}`}
          class="flex flex-col gap-4 rounded-lg bg-base-surface p-3 transition-colors hover:bg-base-elevated sm:flex-row"
        >
          <div class="relative aspect-video w-full flex-shrink-0 overflow-hidden rounded bg-base-elevated sm:w-48">
            {#if stillUrl(ep.still_path, 'w300')}
              <img src={stillUrl(ep.still_path, 'w300')!} alt={ep.name} class="h-full w-full object-cover" loading="lazy" />
            {/if}
            <span class="absolute left-2 top-2 rounded bg-black/80 px-1.5 py-0.5 text-xs font-bold">E{ep.episode_number}</span>
          </div>
          <div class="flex-1">
            <div class="flex items-center justify-between gap-2">
              <h3 class="font-medium">{ep.episode_number}. {ep.name}</h3>
              {#if ep.vote_average > 0}<span class="text-xs text-yellow-400">★ {ep.vote_average.toFixed(1)}</span>{/if}
            </div>
            {#if ep.overview}<p class="mt-1 text-sm text-ink-secondary line-clamp-2">{ep.overview}</p>{/if}
            {#if ep.air_date}<p class="mt-1 text-xs text-ink-secondary">{formatDate(ep.air_date)}</p>{/if}
          </div>
        </a>
      {/each}
    </div>
  {/if}
</section>
