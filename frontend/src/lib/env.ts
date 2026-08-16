const configuredApiBaseUrl = import.meta.env.VITE_API_BASE_URL

if (typeof configuredApiBaseUrl !== 'string' || configuredApiBaseUrl.trim() === '') {
  throw new Error('VITE_API_BASE_URL must be configured')
}

const normalizedApiBaseUrl = configuredApiBaseUrl.trim().replace(/\/+$/, '')

if (!normalizedApiBaseUrl.startsWith('./')) {
  let parsedUrl: URL

  try {
    parsedUrl = new URL(normalizedApiBaseUrl)
  } catch {
    throw new Error('VITE_API_BASE_URL must be an HTTP(S) URL or a ./ relative path')
  }

  if (!['http:', 'https:'].includes(parsedUrl.protocol)) {
    throw new Error('VITE_API_BASE_URL must use HTTP or HTTPS')
  }
}

export const API_BASE_URL = normalizedApiBaseUrl
