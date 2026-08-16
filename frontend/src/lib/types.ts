export type DocumentType = 'invoice' | 'receipt'

export interface ExtractedField<Value> {
  value: Value
  content: string | null
  confidence: number | null
  source: 'document_intelligence'
}

export interface Invoice {
  document_type: 'invoice'
  document_confidence: number
  invoice_number: ExtractedField<string> | null
  invoice_date: ExtractedField<string> | null
  due_date: ExtractedField<string> | null
  vendor_name: ExtractedField<string> | null
  vendor_vat_id: ExtractedField<string> | null
  customer_name: ExtractedField<string> | null
  customer_vat_id: ExtractedField<string> | null
  purchase_order: ExtractedField<string> | null
  currency: ExtractedField<string> | null
  subtotal: ExtractedField<string> | null
  total_tax: ExtractedField<string> | null
  invoice_total: ExtractedField<string> | null
  items: unknown[]
}

export interface Receipt {
  document_type: 'receipt'
  document_confidence: number
  merchant_name: ExtractedField<string> | null
  transaction_date: ExtractedField<string> | null
  transaction_time: ExtractedField<string> | null
  receipt_type: ExtractedField<string> | null
  country_region: ExtractedField<string> | null
  currency: ExtractedField<string> | null
  subtotal: ExtractedField<string> | null
  total_tax: ExtractedField<string> | null
  total: ExtractedField<string> | null
  items: unknown[]
}

export interface ValidationIssue {
  code: string
  field: string
  severity: 'error' | 'warning'
  message: string
}

export interface ProcessedDocument {
  classification: {
    document_type: DocumentType
  }
  document: Invoice | Receipt
  validation: {
    issues: ValidationIssue[]
    is_valid: boolean
  }
  metadata: {
    general_ledger: {
      account: {
        code: string
        name: string
        description: string
      }
      rationale: string
      source: 'azure_openai'
    }
  }
}
