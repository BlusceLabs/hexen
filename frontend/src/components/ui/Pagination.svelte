<script lang="ts">
  interface Props {
    page: number;
    totalPages: number;
    basePath: string;
    searchParams?: Record<string, string>;
  }
  let { page, totalPages, basePath, searchParams = {} }: Props = $props();

  function buildUrl(p: number): string {
    const params = new URLSearchParams(searchParams);
    params.set('page', String(p));
    return `${basePath}?${params.toString()}`;
  }

  function navigate(p: number) {
    window.location.href = buildUrl(p);
  }

  function showPage(n: number): boolean {
    return n === 1 || n === totalPages ||
      Math.abs(n - page) <= 1 ||
      n === page;
  }

  function showEllipsis(prev: number, next: number): boolean {
    return next - prev > 1;
  }

  let pages: number[] = $derived(
    Array.from({ length: totalPages }, (_, i) => i + 1).filter(showPage)
  );
</script>

{#if totalPages > 1}
  <nav class="mt-8 flex items-center justify-center gap-2" aria-label="Pagination">
    <button
      type="button"
      class="btn-ghost touch-target disabled:opacity-30"
      onclick={() => navigate(page - 1)}
      disabled={page <= 1}
      aria-label="Go to previous page"
    >
      ← Prev
    </button>

    {#each pages as p, i (p)}
      {#if i > 0 && showEllipsis(pages[i - 1], p)}
        <span class="px-1 text-ink-secondary" aria-hidden="true">…</span>
      {/if}
      <button
        type="button"
        class:list={["btn touch-target min-w-[2.75rem]", p === page ? "bg-accent text-white" : "btn-ghost"]}
        onclick={() => navigate(p)}
        aria-label={p === page ? `Page ${p}, current page` : `Go to page ${p}`}
        aria-current={p === page ? 'page' : undefined}
      >
        {p}
      </button>
    {/each}

    <button
      type="button"
      class="btn-ghost touch-target disabled:opacity-30"
      onclick={() => navigate(page + 1)}
      disabled={page >= totalPages}
      aria-label="Go to next page"
    >
      Next →
    </button>
  </nav>
{/if}
