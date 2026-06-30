import { defineConfig } from 'astro/config';
import svelte from '@astrojs/svelte';
import tailwind from '@astrojs/tailwind';
import node from '@astrojs/node';

export default defineConfig({
  output: 'server',
  adapter: node({ mode: 'standalone' }),
  integrations: [
    svelte(),
    tailwind({ applyBaseStyles: false }),
  ],
  server: { host: true, port: 4321 },
  vite: {
    define: {
      'import.meta.env.PUBLIC_API_BASE': JSON.stringify(
        process.env.PUBLIC_API_BASE ?? 'http://localhost:8000'
      ),
    },
  },
});
