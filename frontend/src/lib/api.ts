import { API_BASE_URL } from './env'
import type { ProcessedDocument } from './types'

const PROCESSING_ERRORS: Readonly<Record<number, string>> = {
  400: 'This file is empty. Choose a document that contains invoice or receipt data.',
  413: 'This file is larger than 4 MB. Choose a smaller PDF or image.',
  415: 'This file type is not supported. Choose a PDF, PNG, or JPEG.',
  422: 'We could not identify this document as an invoice or receipt.',
  502: 'A processing service is temporarily unavailable. Your file was not saved; try again.',
}

export class DocumentProcessingApiError extends Error {
  readonly status: number | null

  constructor(message: string, status: number | null = null) {
    super(message)
    this.name = 'DocumentProcessingApiError'
    this.status = status
  }
}

export async function processDocument(file: File): Promise<ProcessedDocument> {
  const formData = new FormData()
  formData.append('file', file)

  let response: Response
  try {
    response = await fetch(`${API_BASE_URL}/api/documents/process`, {
      method: 'POST',
      body: formData,
    })
  } catch {
    throw new DocumentProcessingApiError(
      'We could not reach the processing service. Check that the API is running and try again.',
    )
  }

  if (!response.ok) {
    const message =
      PROCESSING_ERRORS[response.status] ??
      'The document could not be processed. Your file was not saved; try again.'
    throw new DocumentProcessingApiError(message, response.status)
  }

  try {
    return (await response.json()) as ProcessedDocument
  } catch {
    throw new DocumentProcessingApiError(
      'The processing service returned an unreadable response. Try again.',
      response.status,
    )
  }
}
