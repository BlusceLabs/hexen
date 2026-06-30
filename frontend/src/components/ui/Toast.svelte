<script lang="ts">
  import { onMount } from 'svelte';

  interface Props {
    message: string;
    type?: 'success' | 'error' | 'warning' | 'info';
    duration?: number;
    onClose?: () => void;
  }

  let { message, type = 'info', duration = 5000, onClose }: Props = $props();

  let visible = $state(true);

  onMount(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        visible = false;
        setTimeout(() => onClose?.(), 300);
      }, duration);
      return () => clearTimeout(timer);
    }
  });

  function close() {
    visible = false;
    setTimeout(() => onClose?.(), 300);
  }

  const styles = {
    success: 'bg-green-600 text-white',
    error: 'bg-red-600 text-white',
    warning: 'bg-yellow-600 text-white',
    info: 'bg-accent text-white',
  };

  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ',
  };
</script>

{#if visible}
  <div
    role="alert"
    aria-live="polite"
    class="fixed bottom-4 right-4 z-50 flex min-w-[320px] max-w-md items-center gap-3 rounded-lg px-4 py-3 shadow-2xl transition-all duration-300 {styles[type]}"
    class:animate-slide-in={visible}
  >
    <span class="text-xl" aria-hidden="true">{icons[type]}</span>
    <p class="flex-1 text-sm font-medium">{message}</p>
    <button
      onclick={close}
      class="rounded p-1 hover:bg-white/20 focus:outline-none focus:ring-2 focus:ring-white/50"
      aria-label="Close notification"
      type="button"
    >
      <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>
{/if}

<style>
  @keyframes slide-in {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }
  .animate-slide-in {
    animation: slide-in 0.3s ease-out;
  }
</style>
