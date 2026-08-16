import type { Invoice, ProcessedDocument, Receipt } from '../lib/types'

function formatMoney(value: string | null, currency: string | null): string {
  if (!value) return 'Not extracted'
  const amount = Number(value)
  if (!Number.isFinite(amount) || !currency || !/^[A-Z]{3}$/.test(currency)) {
    return [currency, value].filter(Boolean).join(' ')
  }
  return new Intl.NumberFormat('en', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
  }).format(amount)
}

function invoiceSummary(invoice: Invoice) {
  return {
    identity: invoice.vendor_name?.value ?? 'Supplier not extracted',
    referenceLabel: 'Invoice number',
    reference: invoice.invoice_number?.value ?? 'Not extracted',
    dateLabel: 'Invoice date',
    date: invoice.invoice_date?.value ?? 'Not extracted',
    currency: invoice.currency?.value ?? null,
    total: invoice.invoice_total?.value ?? null,
    itemCount: invoice.items.length,
  }
}

function receiptSummary(receipt: Receipt) {
  return {
    identity: receipt.merchant_name?.value ?? 'Merchant not extracted',
    referenceLabel: 'Document',
    reference: 'Expense receipt',
    dateLabel: 'Transaction date',
    date: receipt.transaction_date?.value ?? 'Not extracted',
    currency: receipt.currency?.value ?? null,
    total: receipt.total?.value ?? null,
    itemCount: receipt.items.length,
  }
}

interface ResultSummaryProps {
  result: ProcessedDocument
  onReset: () => void
}

export function ResultSummary({ result, onReset }: ResultSummaryProps) {
  const summary =
    result.document.document_type === 'invoice'
      ? invoiceSummary(result.document)
      : receiptSummary(result.document)
  const ledger = result.metadata.general_ledger

  return (
    <section className="overflow-hidden rounded-[1.75rem] border border-slate-200/80 bg-white shadow-[0_30px_80px_-42px_rgba(15,23,42,0.45)]" aria-labelledby="result-title">
      <div className="border-b border-slate-100 px-6 py-5 sm:px-8">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs font-bold tracking-[0.16em] text-teal-700 uppercase">Ready for review</p>
            <h2 id="result-title" className="mt-1.5 text-xl font-semibold text-slate-950">Document prepared</h2>
          </div>
          <span className={`inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-bold ${result.validation.is_valid ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-800'}`}>
            <span className={`size-1.5 rounded-full ${result.validation.is_valid ? 'bg-emerald-500' : 'bg-amber-500'}`} />
            {result.validation.is_valid ? 'Checks passed' : `${result.validation.issues.length} issue${result.validation.issues.length === 1 ? '' : 's'}`}
          </span>
        </div>
      </div>

      <div className="px-6 py-6 sm:px-8 sm:py-8">
        <div className="flex items-center gap-4">
          <span className="flex size-12 shrink-0 items-center justify-center rounded-xl bg-teal-50 text-teal-700">
            <svg viewBox="0 0 24 24" fill="none" className="size-6" aria-hidden="true">
              <path d="M7 3.5h7l4 4v13H7v-17Z" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" />
              <path d="M14 3.75V8h4M10 12h5M10 15.5h5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
            </svg>
          </span>
          <div className="min-w-0">
            <p className="text-xs font-bold tracking-wider text-slate-500 uppercase">{result.document.document_type}</p>
            <p className="mt-1 truncate text-lg font-semibold text-slate-950">{summary.identity}</p>
          </div>
        </div>

        <dl className="mt-6 grid grid-cols-2 gap-x-6 gap-y-5 border-y border-slate-100 py-6">
          <div>
            <dt className="text-xs font-medium text-slate-500">{summary.referenceLabel}</dt>
            <dd className="mt-1 text-sm font-semibold text-slate-900">{summary.reference}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-slate-500">{summary.dateLabel}</dt>
            <dd className="mt-1 text-sm font-semibold text-slate-900">{summary.date}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-slate-500">Line items</dt>
            <dd className="mt-1 text-sm font-semibold text-slate-900">{summary.itemCount}</dd>
          </div>
          <div>
            <dt className="text-xs font-medium text-slate-500">Total</dt>
            <dd className="mt-1 text-sm font-semibold text-slate-900">{formatMoney(summary.total, summary.currency)}</dd>
          </div>
        </dl>

        <div className="mt-6 rounded-2xl bg-slate-950 p-5 text-white">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-xs font-bold tracking-wider text-teal-300 uppercase">Suggested GL account</p>
              <p className="mt-2 text-base font-semibold">{ledger.account.code} · {ledger.account.name}</p>
            </div>
            <span className="rounded-full bg-white/10 px-2.5 py-1 text-[0.68rem] font-semibold text-slate-300">AI suggestion</span>
          </div>
          <p className="mt-3 text-sm leading-6 text-slate-300">{ledger.rationale}</p>
        </div>

        {result.validation.issues.length > 0 && (
          <div className="mt-5 space-y-2" aria-label="Validation issues">
            {result.validation.issues.map((issue) => (
              <div key={`${issue.code}-${issue.field}`} className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm leading-5 text-amber-900">
                {issue.message}
              </div>
            ))}
          </div>
        )}

        <button type="button" className="mt-6 w-full rounded-xl border border-slate-300 px-5 py-3 text-sm font-bold text-slate-800 transition hover:border-slate-400 hover:bg-slate-50 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-700" onClick={onReset}>
          Process another document
        </button>
      </div>
    </section>
  )
}
