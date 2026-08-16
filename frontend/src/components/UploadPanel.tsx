import type { ChangeEvent } from 'react'

function formatFileSize(bytes: number): string {
  if (bytes < 1024 * 1024) {
    return `${Math.max(1, Math.round(bytes / 1024))} KB`
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

interface UploadPanelProps {
  file: File | null
  error: string | null
  isProcessing: boolean
  onFileSelected: (file: File) => void
  onRemove: () => void
  onProcess: () => void
}

export function UploadPanel({
  file,
  error,
  isProcessing,
  onFileSelected,
  onRemove,
  onProcess,
}: UploadPanelProps) {
  function handleChange(event: ChangeEvent<HTMLInputElement>) {
    const selectedFile = event.currentTarget.files?.[0]
    if (selectedFile) {
      onFileSelected(selectedFile)
    }
    event.currentTarget.value = ''
  }

  return (
    <section
      className="overflow-hidden rounded-[1.75rem] border border-slate-200/80 bg-white shadow-[0_30px_80px_-42px_rgba(15,23,42,0.45)]"
      aria-labelledby="upload-title"
    >
      <div className="border-b border-slate-100 px-6 py-5 sm:px-8">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-bold tracking-[0.16em] text-teal-700 uppercase">
              New review
            </p>
            <h2 id="upload-title" className="mt-1.5 text-xl font-semibold text-slate-950">
              Choose a financial document
            </h2>
          </div>
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
            Step 1 of 2
          </span>
        </div>
      </div>

      <div className="px-6 py-6 sm:px-8 sm:py-8">
        {!file ? (
          <label
            htmlFor="document-upload"
            className="group flex min-h-64 cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50/70 px-6 text-center transition hover:border-teal-500 hover:bg-teal-50/40 focus-within:border-teal-500 focus-within:ring-4 focus-within:ring-teal-100"
          >
            <span className="flex size-14 items-center justify-center rounded-2xl bg-white text-teal-700 shadow-sm ring-1 ring-slate-200 transition group-hover:-translate-y-0.5 group-hover:shadow-md">
              <svg viewBox="0 0 24 24" fill="none" className="size-7" aria-hidden="true">
                <path
                  d="M12 16V4m0 0L7.5 8.5M12 4l4.5 4.5M5 14.5v3A2.5 2.5 0 0 0 7.5 20h9a2.5 2.5 0 0 0 2.5-2.5v-3"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </span>
            <span className="mt-5 text-base font-semibold text-slate-900">Select a file to review</span>
            <span className="mt-2 max-w-xs text-sm leading-6 text-slate-500">
              PDF, PNG, or JPEG. One invoice or receipt, up to 4 MB.
            </span>
            <span className="mt-5 rounded-full bg-slate-950 px-5 py-2.5 text-sm font-semibold text-white transition group-hover:bg-teal-800">
              Browse files
            </span>
            <input
              id="document-upload"
              type="file"
              accept="application/pdf,image/png,image/jpeg,.pdf,.png,.jpg,.jpeg"
              className="sr-only"
              onChange={handleChange}
              disabled={isProcessing}
            />
          </label>
        ) : (
          <div className="rounded-2xl border border-slate-200 bg-slate-50/80 p-5">
            <div className="flex items-start gap-4">
              <span className="flex size-12 shrink-0 items-center justify-center rounded-xl bg-white text-teal-700 shadow-sm ring-1 ring-slate-200">
                <svg viewBox="0 0 24 24" fill="none" className="size-6" aria-hidden="true">
                  <path
                    d="M7.5 3.75h6.75L18.5 8v12.25H7.5V3.75Z"
                    stroke="currentColor"
                    strokeWidth="1.7"
                    strokeLinejoin="round"
                  />
                  <path d="M14 4v4.25h4.25M10 12h6M10 15.5h6" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
                </svg>
              </span>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold text-slate-950">{file.name}</p>
                <p className="mt-1 text-xs font-medium text-slate-500">
                  {file.type === 'application/pdf' ? 'PDF document' : 'Image document'} ·{' '}
                  {formatFileSize(file.size)}
                </p>
                <div className="mt-4 flex items-center gap-4">
                  <label
                    htmlFor="document-change"
                    className={`text-sm font-semibold text-teal-700 ${isProcessing ? 'cursor-not-allowed opacity-50' : 'cursor-pointer hover:text-teal-900'}`}
                  >
                    Change
                    <input
                      id="document-change"
                      type="file"
                      accept="application/pdf,image/png,image/jpeg,.pdf,.png,.jpg,.jpeg"
                      className="sr-only"
                      onChange={handleChange}
                      disabled={isProcessing}
                    />
                  </label>
                  <button
                    type="button"
                    className="text-sm font-semibold text-slate-500 hover:text-slate-900 disabled:cursor-not-allowed disabled:opacity-50"
                    onClick={onRemove}
                    disabled={isProcessing}
                  >
                    Remove
                  </button>
                </div>
              </div>
              <span className="flex size-7 items-center justify-center rounded-full bg-emerald-100 text-emerald-700" aria-label="File ready">
                <svg viewBox="0 0 20 20" fill="none" className="size-4" aria-hidden="true">
                  <path d="m5 10 3 3 7-7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </span>
            </div>
          </div>
        )}

        {error && (
          <div className="mt-4 flex gap-3 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm leading-5 text-rose-800" role="alert">
            <svg viewBox="0 0 20 20" fill="none" className="mt-0.5 size-4 shrink-0" aria-hidden="true">
              <path d="M10 6.5v4M10 14h.01" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
              <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="1.5" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        <button
          type="button"
          className="mt-6 flex w-full items-center justify-center gap-2.5 rounded-xl bg-teal-700 px-5 py-3.5 text-sm font-bold text-white shadow-sm transition hover:bg-teal-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:shadow-none"
          disabled={!file || isProcessing}
          onClick={onProcess}
        >
          {isProcessing ? (
            <>
              <span className="size-4 animate-spin rounded-full border-2 border-white/40 border-t-white" aria-hidden="true" />
              Processing document…
            </>
          ) : (
            <>
              Start processing
              <svg viewBox="0 0 20 20" fill="none" className="size-4" aria-hidden="true">
                <path d="M4 10h12m0 0-4-4m4 4-4 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </>
          )}
        </button>

        <p className="mt-4 flex items-center justify-center gap-2 text-center text-xs leading-5 text-slate-500">
          <svg viewBox="0 0 20 20" fill="none" className="size-4 shrink-0" aria-hidden="true">
            <path d="M6 9V7a4 4 0 1 1 8 0v2m-9 0h10v8H5V9Z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
          </svg>
          Documents are processed in memory and are not stored.
        </p>
      </div>
    </section>
  )
}
