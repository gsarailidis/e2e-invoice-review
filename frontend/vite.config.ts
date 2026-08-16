import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

function codeServerProxyUrl(): URL | null {
  const proxyUri = process.env.VSCODE_PROXY_URI
  if (!proxyUri) return null

  try {
    return new URL(proxyUri.replace('{{port}}', '5173'))
  } catch {
    return null
  }
}

const proxyUrl = codeServerProxyUrl()

function codeServerProxyBase(proxy: URL | null): Plugin {
  return {
    name: 'code-server-proxy-base',
    configureServer(server) {
      if (!proxy) return

      const proxyBase = proxy.pathname.replace(/\/$/, '')
      server.middlewares.use((request, _response, next) => {
        const requestUrl = request.url
        if (
          requestUrl &&
          !requestUrl.startsWith(proxyBase) &&
          !requestUrl.startsWith('/backend')
        ) {
          request.url = `${proxyBase}${requestUrl.startsWith('/') ? '' : '/'}${requestUrl}`
        }
        next()
      })
    },
  }
}

// https://vite.dev/config/
export default defineConfig(({ command }) => {
  const developmentProxy = command === 'serve' ? proxyUrl : null

  return {
    base: developmentProxy?.pathname ?? './',
    plugins: [codeServerProxyBase(developmentProxy), react(), tailwindcss()],
    server: {
      port: 5173,
      strictPort: true,
      allowedHosts: developmentProxy ? [developmentProxy.hostname] : [],
      proxy: {
        '/backend': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/backend/, ''),
        },
      },
    },
  }
})
