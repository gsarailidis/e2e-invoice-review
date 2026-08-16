const MAX_UPLOAD_BYTES = 4 * 1024 * 1024
const ACCEPTED_MEDIA_TYPES = new Set(['application/pdf', 'image/png', 'image/jpeg'])

export function validateDocumentFile(file: File): string | null {
  if (!ACCEPTED_MEDIA_TYPES.has(file.type)) {
    return 'Choose a PDF, PNG, or JPEG document.'
  }
  if (file.size === 0) {
    return 'This file is empty. Choose another document.'
  }
  if (file.size > MAX_UPLOAD_BYTES) {
    return 'This file is larger than the 4 MB upload limit.'
  }
  return null
}
