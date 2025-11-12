import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
    plugins: [
        react({
            // Enable Fast Refresh (HMR) for React
            fastRefresh: true,
        })
    ],
    build: {
        outDir: 'dist',
        // Build for production - React handles all frontend
    },
    server: {
        port: 5173,
        cors: true,
        strictPort: true,
        hmr: {
            // Enable HMR for cross-origin requests (when Flask serves the page)
            clientPort: 5173,
            protocol: 'ws',
            host: 'localhost'
        },
        headers: {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        proxy: {
            '/api': {
                target: 'http://localhost:5001',
                changeOrigin: true
            }
        }
    }
})

