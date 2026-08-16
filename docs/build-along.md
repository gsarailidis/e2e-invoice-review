# Build-along guide

The complete guided build lives at <https://learn.datalumina.com/docs/invoice-review>. This local guide records the first checkpoint represented by the `main` branch.

## Starter outcome

The repository installs reproducibly, starts a minimal FastAPI service and React interface, and includes the business brief plus fictional source documents.

## Why this boundary exists

The starter removes the completed workflow while preserving every prerequisite needed to build it. You begin with the user, the source documents, and explicit service boundaries instead of reverse-engineering a finished application.

## Commands

```bash
cd backend
uv sync --locked

cd ../frontend
pnpm install --frozen-lockfile

cd ..
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
./scripts/dev.sh --check
./scripts/dev.sh
```

## Important locations

- `docs/client-brief.md`: the recurring finance problem and definition of done
- `docs/architecture.md`: the intended boundaries and data flow
- `samples/`: the fictional evaluation corpus and manifest
- `backend/app/main.py`: the initial API boundary
- `frontend/src/App.tsx`: the initial interface boundary

## What you should observe

- `GET http://localhost:8000/health` returns `{"status":"ok"}`.
- `http://localhost:5173` shows the Invoice Review starter screen.
- No Azure request occurs at this checkpoint.

## Checkpoint

- [ ] Locked backend and frontend installs succeed.
- [ ] Backend lint passes.
- [ ] Frontend type-check, lint, and production build pass.
- [ ] `./scripts/dev.sh --check` reports that Invoice Review is ready to start.
- [ ] The health endpoint and starter screen load locally.

Continue with the [online tutorial](https://learn.datalumina.com/docs/invoice-review).

## Typed Document Intelligence checkpoint

### Outcome

The Azure provider adapter analyzes invoices and receipts with their respective prebuilt models,
then maps provider output into separate, provider-independent Pydantic models. Every extracted
field keeps its typed value, source content, confidence, and Document Intelligence provenance.

### Why

Provider SDK objects stop inside the Azure adapter. The application receives dates, times,
`Decimal` amounts, ISO currency codes, line items, and explicit missing values without knowing
Azure's response shape. This preserves the later boundary between probabilistic extraction and
deterministic finance policy.

### Commands

Add local `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` and `AZURE_DOCUMENT_INTELLIGENCE_KEY` values
to `backend/.env`, then run the example from the playground directory:

```bash
cd playground
uv run --project ../backend --locked --no-sync ruff check \
  ../backend/app document_intelligence.py
uv run --project ../backend --locked --no-sync python document_intelligence.py
```

The second command makes exactly two Azure Document Intelligence analysis requests and may
consume paid or limited provider capacity. It analyzes one page from
`samples/generated/01-en-happy-classic.pdf` and one page from
`samples/generated/13-nl-fuel-receipt.png`. The two pages fit within the F0 monthly allowance
when quota remains; at the documented S0 USD retail rate they cost about $0.02 in total. The
experiment writes no output file and needs no cleanup.

### What you should observe

The command prints the normalized invoice and receipt models plus manifest comparisons. The
invoice contains `EN-2026-1001`, four line items, EUR 100.00 subtotal, EUR 21.00 tax, and EUR
121.00 total. The receipt contains merchant `NORTH SEA FUEL B.V.` as printed, transaction date
2026-07-19, one fuel line, EUR 50.00 subtotal, EUR 10.50 tax, and EUR 60.50 total. Both
`manifest_comparison.matches` values and all line-item checks are `true` when extraction matches
the fictional corpus. Organization names are compared case-insensitively because Azure preserves
the source document's typography; the mapped value and content are never rewritten.

### Checkpoint

- [ ] Backend lint passes.
- [ ] Both provider requests complete with the configured local Azure resource.
- [ ] Pydantic serialization retains values, content, confidence, and provenance.
- [ ] Invoice and receipt manifest comparisons report no mapping differences.
- [ ] The invoice contains four line items and the receipt contains one line item.

## Azure OpenAI connection checkpoint

### Outcome

`AzureOpenAIService` owns the OpenAI client configured for the Azure `/openai/v1` endpoint.
Central `Settings` loads the endpoint and API key and passes them into the adapter, which uses the
hard-coded `gpt-5.6-terra` deployment and returns plain text from the Responses API.

### Why

OpenAI SDK response types and credentials stay inside the Azure provider adapter. Callers provide
ordinary text and receive ordinary text, while the adapter owns the model selection, request
storage setting, empty-response handling, client lifetime, and Azure endpoint normalization.

### Commands

Add local `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY` values to `backend/.env`, then run
the connection check from the playground directory:

```bash
cd playground
uv run --project ../backend --locked --no-sync ruff check \
  ../backend/app azure_openai.py
uv run --project ../backend --locked --no-sync python azure_openai.py
uv run --project ../backend --locked --no-sync python azure_openai.py \
  "Reply with exactly: playground-ok"
```

Each Python invocation makes one token-metered Azure OpenAI Responses API request with a 64-token
output ceiling. With no argument, the script sends only a fictional general-knowledge prompt; a
quoted positional argument supplies any other text prompt. Use `--max-output-tokens` to change the
ceiling, with a minimum of 16. Requests set `store=False`, write no output file, and need no
cleanup. See the official
[Responses API reference](https://developers.openai.com/api/reference/python/resources/responses/methods/create)
for the request contract.

### What you should observe

The command prints `answer: Paris`. The exact surrounding punctuation may vary, but the response
must identify Paris and complete without exposing the API key or an OpenAI SDK response object.

### Checkpoint

- [ ] Backend and playground lint pass.
- [ ] The configured Azure endpoint accepts the hard-coded `gpt-5.6-terra` deployment.
- [ ] The provider returns non-empty plain text and closes its client cleanly.
- [ ] No credential is present in tracked or playground source files.

## Structured document classification checkpoint

### Outcome

`DocumentClassificationStep` sends the original PDF, PNG, or JPEG to the hard-coded
`gpt-5.6-terra` Azure deployment and returns a provider-independent Pydantic model. Its
`document_type` is constrained to `invoice`, `receipt`, or `other`. Pydantic AI uses Azure's
Responses API with strict native JSON Schema output, and requests set `store=False`.

### Why

Classification is a narrow pipeline decision, not an extraction or finance-policy decision.
Native structured output prevents free-form labels from reaching routing logic, while `other`
avoids forcing an unrelated or ambiguous upload into the invoice or receipt workflow. Azure
credentials and provider construction remain in the provider adapter; the pipeline owns the
classification schema and prompt.

The implementation follows Pydantic AI's documented
[Azure Responses API](https://pydantic.dev/docs/ai/models/openai/#using-azure-with-the-responses-api)
and [Native Output](https://pydantic.dev/docs/ai/core-concepts/output/#native-output) patterns.

### Commands

With `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY` configured in `backend/.env`, run:

```bash
uv sync --project backend --locked
uv run --project backend --locked --no-sync ruff check \
  backend/app playground/classification.py
uv run --project backend --locked --no-sync python playground/classification.py
uv run --project backend --locked --no-sync python playground/classification.py \
  samples/generated/13-nl-fuel-receipt.png
```

The default command analyzes `01-en-happy-classic.pdf`. An optional positional path can point to
any local PDF, PNG, JPEG, or JPG. Each classification invocation makes one token-metered Azure
OpenAI request and sends that document to the configured Azure resource. The evaluator persists
neither the input nor the response.

### What you should observe

The default invoice prints `{"document_type":"invoice"}` and the Dutch fuel receipt prints
`{"document_type":"receipt"}` as formatted JSON. A schema mismatch fails validation instead of
returning an unchecked string.

### Checkpoint

- [ ] The locked backend environment installs successfully.
- [ ] Backend and classification playground lint pass.
- [ ] The fictional invoice is classified as `invoice`.
- [ ] The fictional fuel receipt is classified as `receipt`.
- [ ] No raw OpenAI response, credential, uploaded document, or generated output file is exposed.

## Typed financial-document pipeline checkpoint

### Outcome

A reusable synchronous `Pipeline` chains classification, extraction, and deterministic validation:

```python
pipeline = (
    Pipeline.start(classification_step)
    .then(extraction_step)
    .then(validation_step)
)
```

Each step has a distinct typed input and output. The final `ProcessedDocument` contains the strict
classification, a discriminated `Invoice | Receipt` Pydantic model, and structured validation
issues. Document bytes pass through the chain without coupling providers to local file paths.

### Why

Typed transitions make step order and contracts visible without a mutable context containing
partially initialized fields. Classification chooses `prebuilt-invoice` or `prebuilt-receipt`;
an `other` result stops before Document Intelligence is called. Extraction remains probabilistic,
while offline VAT checks and total reconciliation remain pure deterministic functions that never
rewrite extracted evidence or claim a live VIES registration result.

`app/config.py` is the single backend environment boundary. Provider adapters receive explicit
configuration, and Azure SDK response types remain inside those adapters.

### Commands

With both Azure services configured in `backend/.env`, run from the repository root:

```bash
uv sync --project backend --locked
uv run --project backend --locked --no-sync ruff check backend/app playground
uv run --project backend --locked --no-sync python playground/pipeline.py
```

The evaluator processes four one-page fictional documents. It makes eight live requests: four
token-metered Azure OpenAI classifications and four Document Intelligence analyses. The four
Document Intelligence pages fit within the F0 monthly allowance when quota remains; at the
documented S0 USD retail rate they cost about $0.04 in total. Azure OpenAI cost depends on the
configured deployment and the input/output tokens consumed by each document. The evaluator
persists neither document bytes nor provider output, so no cleanup command is required.

### What you should observe

The evaluator prints each final Pydantic result, normalized-field comparisons, issue-code
comparisons, and an overall `"matches": true`:

- `01-en-happy-classic.pdf`: invoice, four line items, no focused issues.
- `06-de-invalid-vendor-vat.pdf`: `vendor_vat_id_invalid`.
- `08-en-total-mismatch.pdf`: `invoice_total_mismatch`.
- `13-nl-fuel-receipt.png`: receipt, one line item, no focused issues.

Present supplier and customer VAT IDs are checked locally with `python-stdnum`. Invoice and
receipt totals reconcile when `abs(subtotal + VAT - total) <= Decimal("0.01")`; a focused check is
skipped when one of its inputs is missing. Findings annotate the result rather than interrupting
downstream human review.

### Checkpoint

- [ ] The locked backend environment installs and Ruff passes.
- [ ] The chain returns provider-independent, JSON-serializable Pydantic output.
- [ ] Invoice and receipt classifications select their matching Document Intelligence models.
- [ ] All four field and issue-code comparisons match the fictional manifest.
- [ ] `other` documents stop before extraction.
- [ ] No raw provider output, secrets, documents, or runtime data are persisted.
