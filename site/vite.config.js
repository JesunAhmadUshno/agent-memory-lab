import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
// The site reads the level-*/results_*.json files and the Python sources at build time, so every number on the page is generated, never typed.
export default defineConfig({
  base: '/agent-memory-lab/',
  plugins: [react()],
  server: { fs: { allow: ['..'] } },
});
