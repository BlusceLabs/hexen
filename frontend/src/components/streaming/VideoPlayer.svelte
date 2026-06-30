<script lang="ts">
  import { onMount } from 'svelte';

  interface Props {
    src: string;
    poster?: string;
    title?: string;
    autoplay?: boolean;
  }

  let { src, poster, title = 'Video Player', autoplay = false }: Props = $props();

  let videoElement: HTMLVideoElement;
  let playing = $state(false);
  let currentTime = $state(0);
  let duration = $state(0);
  let volume = $state(1);
  let muted = $state(false);
  let fullscreen = $state(false);
  let showControls = $state(true);
  let buffering = $state(false);
  let hideControlsTimeout: ReturnType<typeof setTimeout>;

  function togglePlay() {
    if (!videoElement) return;
    if (playing) {
      videoElement.pause();
    } else {
      videoElement.play();
    }
  }

  function seek(e: MouseEvent) {
    if (!videoElement) return;
    const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
    const percent = (e.clientX - rect.left) / rect.width;
    videoElement.currentTime = percent * duration;
  }

  function changeVolume(e: Event) {
    if (!videoElement) return;
    const value = parseFloat((e.target as HTMLInputElement).value);
    videoElement.volume = value;
    volume = value;
    muted = value === 0;
  }

  function toggleMute() {
    if (!videoElement) return;
    videoElement.muted = !muted;
    muted = !muted;
  }

  function toggleFullscreen() {
    if (!document.fullscreenElement) {
      videoElement?.parentElement?.requestFullscreen();
      fullscreen = true;
    } else {
      document.exitFullscreen();
      fullscreen = false;
    }
  }

  function formatTime(seconds: number): string {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    if (h > 0) {
      return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }
    return `${m}:${s.toString().padStart(2, '0')}`;
  }

  function handleMouseMove() {
    showControls = true;
    clearTimeout(hideControlsTimeout);
    if (playing) {
      hideControlsTimeout = setTimeout(() => {
        showControls = false;
      }, 3000);
    }
  }

  function handleKeyPress(e: KeyboardEvent) {
    switch (e.key) {
      case ' ':
      case 'k':
        e.preventDefault();
        togglePlay();
        break;
      case 'f':
        e.preventDefault();
        toggleFullscreen();
        break;
      case 'm':
        e.preventDefault();
        toggleMute();
        break;
      case 'ArrowLeft':
        e.preventDefault();
        if (videoElement) videoElement.currentTime -= 10;
        break;
      case 'ArrowRight':
        e.preventDefault();
        if (videoElement) videoElement.currentTime += 10;
        break;
      case 'ArrowUp':
        e.preventDefault();
        if (videoElement && volume < 1) videoElement.volume = Math.min(1, volume + 0.1);
        break;
      case 'ArrowDown':
        e.preventDefault();
        if (videoElement && volume > 0) videoElement.volume = Math.max(0, volume - 0.1);
        break;
    }
  }

  onMount(() => {
    document.addEventListener('fullscreenchange', () => {
      fullscreen = !!document.fullscreenElement;
    });
  });
</script>

<div 
  class="relative aspect-video w-full bg-black"
  onmousemove={handleMouseMove}
  onmouseleave={() => playing && (showControls = false)}
  role="region"
  aria-label="Video player"
>
  <video
    bind:this={videoElement}
    {src}
    {poster}
    {autoplay}
    class="h-full w-full"
    onplay={() => playing = true}
    onpause={() => playing = false}
    ontimeupdate={() => currentTime = videoElement.currentTime}
    onloadedmetadata={() => duration = videoElement.duration}
    onwaiting={() => buffering = true}
    oncanplay={() => buffering = false}
    onvolumechange={() => volume = videoElement.volume}
    onkeydown={handleKeyPress}
    tabindex="0"
    aria-label={title}
  >
    <track kind="captions" />
  </video>

  <!-- Buffering Indicator -->
  {#if buffering}
    <div class="absolute inset-0 flex items-center justify-center bg-black/50">
      <svg class="h-12 w-12 animate-spin text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>
  {/if}

  <!-- Play/Pause Overlay -->
  {#if !playing && !buffering}
    <button
      onclick={togglePlay}
      class="absolute inset-0 flex items-center justify-center bg-black/30 transition-opacity hover:bg-black/40 focus:outline-none focus:ring-4 focus:ring-white/50"
      aria-label="Play video"
      type="button"
    >
      <div class="rounded-full bg-white/90 p-6 shadow-2xl transition-transform hover:scale-110">
        <svg class="h-12 w-12 text-black" fill="currentColor" viewBox="0 0 20 20">
          <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
        </svg>
      </div>
    </button>
  {/if}

  <!-- Controls -->
  {#if showControls || !playing}
    <div 
      class="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 to-transparent p-4 transition-opacity"
      role="group"
      aria-label="Video controls"
    >
      <!-- Progress Bar -->
      <div 
        class="group mb-4 h-1 w-full cursor-pointer rounded-full bg-white/30 hover:h-2 transition-all"
        onclick={seek}
        role="slider"
        aria-label="Seek"
        aria-valuemin="0"
        aria-valuemax={duration}
        aria-valuenow={currentTime}
        tabindex="0"
      >
        <div 
          class="h-full rounded-full bg-accent transition-all"
          style="width: {duration ? (currentTime / duration) * 100 : 0}%"
        ></div>
      </div>

      <div class="flex items-center gap-4">
        <!-- Play/Pause -->
        <button
          onclick={togglePlay}
          class="text-white transition-transform hover:scale-110 focus:outline-none focus:ring-2 focus:ring-white/50 rounded"
          aria-label={playing ? 'Pause' : 'Play'}
          type="button"
        >
          {#if playing}
            <svg class="h-8 w-8" fill="currentColor" viewBox="0 0 20 20">
              <path d="M5 4a2 2 0 012-2h1a2 2 0 012 2v12a2 2 0 01-2 2H7a2 2 0 01-2-2V4zm5 0a2 2 0 012-2h1a2 2 0 012 2v12a2 2 0 01-2 2h-1a2 2 0 01-2-2V4z" />
            </svg>
          {:else}
            <svg class="h-8 w-8" fill="currentColor" viewBox="0 0 20 20">
              <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
            </svg>
          {/if}
        </button>

        <!-- Volume -->
        <div class="flex items-center gap-2">
          <button
            onclick={toggleMute}
            class="text-white transition-transform hover:scale-110 focus:outline-none focus:ring-2 focus:ring-white/50 rounded"
            aria-label={muted ? 'Unmute' : 'Mute'}
            type="button"
          >
            {#if muted || volume === 0}
              <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.707.707L4.586 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.586l3.707-3.707a1 1 0 011.09-.217zM12.293 7.293a1 1 0 011.414 0L15 8.586l1.293-1.293a1 1 0 111.414 1.414L16.414 10l1.293 1.293a1 1 0 01-1.414 1.414L15 11.414l-1.293 1.293a1 1 0 01-1.414-1.414L13.586 10l-1.293-1.293a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            {:else}
              <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.707.707L4.586 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.586l3.707-3.707a1 1 0 011.09-.217zM14.657 2.929a1 1 0 011.414 0A9.972 9.972 0 0119 10a9.972 9.972 0 01-2.929 7.071 1 1 0 01-1.414-1.414A7.971 7.971 0 0017 10c0-2.21-.894-4.208-2.343-5.657a1 1 0 010-1.414zm-2.829 2.828a1 1 0 011.415 0A5.983 5.983 0 0115 10a5.984 5.984 0 01-1.757 4.243 1 1 0 01-1.415-1.415A3.984 3.984 0 0013 10a3.983 3.983 0 00-1.172-2.828 1 1 0 010-1.415z" clip-rule="evenodd" />
              </svg>
            {/if}
          </button>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={volume}
            oninput={changeVolume}
            class="h-1 w-20 cursor-pointer appearance-none rounded-full bg-white/30 accent-accent"
            aria-label="Volume"
          />
        </div>

        <!-- Time -->
        <span class="text-sm font-medium text-white">
          {formatTime(currentTime)} / {formatTime(duration)}
        </span>

        <div class="flex-1"></div>

        <!-- Fullscreen -->
        <button
          onclick={toggleFullscreen}
          class="text-white transition-transform hover:scale-110 focus:outline-none focus:ring-2 focus:ring-white/50 rounded"
          aria-label={fullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
          type="button"
        >
          {#if fullscreen}
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          {:else}
            <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
            </svg>
          {/if}
        </button>
      </div>
    </div>
  {/if}
</div>

<style>
  input[type="range"]::-webkit-slider-thumb {
    appearance: none;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: white;
    cursor: pointer;
  }
</style>
