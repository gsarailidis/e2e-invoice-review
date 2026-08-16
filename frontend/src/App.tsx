import { useState } from 'react'

import { ResultSummary } from './components/ResultSummary'
import { UploadPanel } from './components/UploadPanel'
import { DocumentProcessingApiError, processDocument } from './lib/api'
import { validateDocumentFile } from './lib/files'
import type { ProcessedDocument } from './lib/types'

type WorkflowStatus = 'idle' | 'ready' | 'processing' | 'success' | 'error'

export default function App() {
  const [file, setFile] = useState<File | null>(null)
  const [status, setStatus] = useState<WorkflowStatus>('idle')
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<ProcessedDocument | null>(null)

  function selectFile(selectedFile: File) {
    const validationError = validateDocumentFile(selectedFile)
    setResult(null)

    if (validationError) {
      setFile(null)
      setError(validationError)
      setStatus('error')
      return
    }

    setFile(selectedFile)
    setError(null)
    setStatus('ready')
  }

  function removeFile() {
    setFile(null)
    setError(null)
    setStatus('idle')
  }

  async function startProcessing() {
    if (!file || status === 'processing') return

    setError(null)
    setStatus('processing')

    try {
      const processedDocument = await processDocument(file)
      setResult(processedDocument)
      setStatus('success')
    } catch (processingError: unknown) {
      const message =
        processingError instanceof DocumentProcessingApiError
          ? processingError.message
          : 'Something unexpected happened. Your file was not saved; try again.'
      setError(message)
      setStatus('error')
    }
  }

  function resetWorkflow() {
    setFile(null)
    setError(null)
    setResult(null)
    setStatus('idle')
  }

  return (
    <div className="min-h-screen bg-[#f4f7f6] text-slate-950">
      <header className="border-b border-slate-200/80 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 sm:px-8 lg:px-10">
          <div className="flex items-center gap-3">
            <span className="grid size-9 place-items-center rounded-xl bg-teal-700 text-white shadow-sm">
              <svg viewBox="0 0 24 24" fill="none" className="size-5" aria-hidden="true">
                <path d="M7 4h7l4 4v12H7V4Z" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" />
                <path d="M14 4v4h4M10 12h5M10 15h3" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
              </svg>
            </span>
            <div>
              <p className="text-sm font-bold tracking-tight text-slate-950">Northstar</p>
              <p className="text-[0.68rem] font-semibold tracking-[0.14em] text-slate-500 uppercase">Invoice review</p>
            </div>
          </div>
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-500">
            <span className="size-2 rounded-full bg-emerald-500 shadow-[0_0_0_4px_rgba(16,185,129,0.12)]" />
            Review workspace
          </div>
        </div>
      </header>

      <main className="relative isolate overflow-hidden">
        <div className="pointer-events-none absolute inset-x-0 top-0 -z-10 h-[30rem] bg-[radial-gradient(circle_at_15%_15%,rgba(13,148,136,0.10),transparent_32%),radial-gradient(circle_at_85%_10%,rgba(15,23,42,0.06),transparent_28%)]" />
        <div className="mx-auto grid max-w-7xl items-center gap-12 px-5 py-14 sm:px-8 sm:py-20 lg:grid-cols-[minmax(0,0.88fr)_minmax(30rem,1fr)] lg:gap-20 lg:px-10 lg:py-24">
          <div className="max-w-xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-teal-200 bg-white/70 px-3 py-1.5 text-xs font-bold text-teal-800 shadow-sm backdrop-blur">
              <span className="size-1.5 rounded-full bg-teal-500" />
              Human-in-the-loop finance review
            </div>
            <h1 className="mt-7 text-4xl leading-[1.08] font-semibold tracking-[-0.04em] text-slate-950 sm:text-5xl lg:text-[3.65rem]">
              Turn the next document into a review-ready record.
            </h1>
            <p className="mt-6 max-w-lg text-base leading-7 text-slate-600 sm:text-lg sm:leading-8">
              Upload an invoice or receipt. We’ll classify it, extract the finance fields, run deterministic checks, and suggest the right general ledger account.
            </p>

            <div className="mt-9 grid gap-4 sm:grid-cols-3 lg:grid-cols-1 xl:grid-cols-3">
              {[
                ['01', 'Classify', 'Invoice or receipt'],
                ['02', 'Extract', 'Structured finance data'],
                ['03', 'Check', 'VAT, totals, and GL'],
              ].map(([number, title, detail]) => (
                <div key={number} className="flex gap-3 sm:block lg:flex xl:block">
                  <span className="text-xs font-bold tracking-wider text-teal-700">{number}</span>
                  <div className="sm:mt-2 lg:mt-0 xl:mt-2">
                    <p className="text-sm font-semibold text-slate-900">{title}</p>
                    <p className="mt-0.5 text-xs leading-5 text-slate-500">{detail}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div aria-live="polite" aria-busy={status === 'processing'}>
            {status === 'success' && result ? (
              <ResultSummary result={result} onReset={resetWorkflow} />
            ) : (
              <UploadPanel
                file={file}
                error={error}
                isProcessing={status === 'processing'}
                onFileSelected={selectFile}
                onRemove={removeFile}
                onProcess={startProcessing}
              />
            )}
          </div>
        </div>
      </main>

      <footer className="mx-auto flex max-w-7xl flex-col gap-2 border-t border-slate-200/70 px-5 py-6 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between sm:px-8 lg:px-10">
        <p>Northstar Facilities B.V. · Fictional review workspace</p>
        <p>Extraction evidence stays visible. Finance policy stays deterministic.</p>
      </footer>
    </div>
  )
}
