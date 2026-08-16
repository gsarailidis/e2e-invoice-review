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

## Document Intelligence invoice checkpoint

### Outcome

`DocumentIntelligenceService` owns the configured Azure client and submits local invoices with
the `prebuilt-invoice` model. The separate playground example selects the fictional English
sample, calls the service, and prints the complete result model as formatted JSON.

### Why

This is the smallest useful provider check: it proves that the local endpoint and key work,
that Azure accepts a local PDF, and that the extracted invoice fields are visible before the
application introduces normalization or business rules.

### Commands

Add local `AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT` and `AZURE_DOCUMENT_INTELLIGENCE_KEY` values
to `backend/.env`, then run the example from the playground directory:

```bash
cd playground
uv run --project ../backend --locked --no-sync ruff check \
  ../backend/app/services/document_intelligence_service.py document_intelligence.py
uv run --project ../backend --locked --no-sync python document_intelligence.py
```

The second command makes one Azure Document Intelligence analysis request and may consume paid
or limited provider capacity. It analyzes only
`samples/generated/01-en-happy-classic.pdf`, writes no output file, and needs no cleanup.

### What you should observe

The command prints JSON whose top-level values include `apiVersion`, `modelId`, extracted
`content`, `pages`, and a `documents` collection. For the selected sample, the first document
contains invoice `EN-2026-1001`, four line items, EUR 100.00 subtotal, EUR 21.00 tax, and
EUR 121.00 total together with Azure confidence values.

### Checkpoint

- [ ] Backend lint passes.
- [ ] The provider request completes with the configured local Azure resource.
- [ ] The printed result uses the `prebuilt-invoice` model and contains one extracted invoice.
