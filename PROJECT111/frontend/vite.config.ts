import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path' // Node.js의 'path' 모듈을 불러옵니다.

// https://vitejs/plugin-react
export default defineConfig({
  plugins: [react(), tailwindcss()],
  // 아래 resolve.alias 부분이 경로 별칭을 설정하는 핵심 코드입니다.
  resolve: {
    alias: {
      // '@'라는 별칭이 src 폴더를 가리키도록 설정합니다.
      '@': path.resolve(__dirname, './src'),
    },
  },
})

