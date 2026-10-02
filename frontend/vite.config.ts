import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';

// Dev-сервер повторяет маршрутизацию продового nginx.conf: в Django уходят только /api/ и
// /admin/ (плюс /media/ и /static/, которые в проде раздаёт сам Nginx), всё остальное — SPA.
// Раньше здесь приходилось отдельно проксировать /listings, /bookings, /users и т.д., потому
// что бэкенд висел на корне; после переноса всего API под /api/ это больше не нужно, а SPA-роут
// /listings/:id и API-роут /api/listings/<uuid>/ больше не конфликтуют.
const DJANGO = 'http://localhost:8000';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': { target: DJANGO, changeOrigin: true },
      '/admin': { target: DJANGO, changeOrigin: true },
      '/media': { target: DJANGO, changeOrigin: true },
      '/static': { target: DJANGO, changeOrigin: true },
    },
  },
});
