from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

GeneralLedgerCode = Literal[
    "6100",
    "6110",
    "6120",
    "6130",
    "6140",
    "6200",
    "6210",
    "6300",
    "6400",
    "6500",
]


class GeneralLedgerAccount(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    code: GeneralLedgerCode
    name: str
    description: str


GENERAL_LEDGER_ACCOUNTS = (
    GeneralLedgerAccount(
        code="6100",
        name="Cleaning Services",
        description="External janitorial, sanitation, and specialist cleaning services.",
    ),
    GeneralLedgerAccount(
        code="6110",
        name="Repairs and Maintenance",
        description="General building repairs, preventive maintenance, and handyman services.",
    ),
    GeneralLedgerAccount(
        code="6120",
        name="Electrical Services",
        description="Electrical installation, inspection, repair, and related call-out work.",
    ),
    GeneralLedgerAccount(
        code="6130",
        name="Plumbing Services",
        description="Plumbing installation, drainage, leak repair, and water-system services.",
    ),
    GeneralLedgerAccount(
        code="6140",
        name="HVAC Services",
        description="Heating, ventilation, air-conditioning maintenance, and repair services.",
    ),
    GeneralLedgerAccount(
        code="6200",
        name="Equipment Purchases",
        description="Purchased tools, machinery, and operational facility equipment.",
    ),
    GeneralLedgerAccount(
        code="6210",
        name="Equipment Rental",
        description="Short-term hire or lease of tools, machinery, and access equipment.",
    ),
    GeneralLedgerAccount(
        code="6300",
        name="Fuel and Vehicle Expenses",
        description="Fuel, charging, tolls, parking, and routine vehicle operating costs.",
    ),
    GeneralLedgerAccount(
        code="6400",
        name="Facility Supplies",
        description="Consumable cleaning, maintenance, safety, and general facility supplies.",
    ),
    GeneralLedgerAccount(
        code="6500",
        name="Professional Services",
        description="External consulting, engineering, inspection, and advisory services.",
    ),
)

_ACCOUNTS_BY_CODE = {account.code: account for account in GENERAL_LEDGER_ACCOUNTS}


class GeneralLedgerSelection(BaseModel):
    """Strict model output before the code is resolved through the local catalog."""

    model_config = ConfigDict(extra="forbid")

    account_code: GeneralLedgerCode
    rationale: str = Field(min_length=1, max_length=400)


class GeneralLedgerSuggestion(BaseModel):
    """Provider-independent metadata attached to the processed document."""

    model_config = ConfigDict(extra="forbid")

    account: GeneralLedgerAccount
    rationale: str
    source: Literal["azure_openai"] = "azure_openai"


def get_general_ledger_account(code: GeneralLedgerCode) -> GeneralLedgerAccount:
    return _ACCOUNTS_BY_CODE[code]


def general_ledger_catalog_prompt() -> str:
    return "\n".join(
        f"- {account.code}: {account.name} — {account.description}"
        for account in GENERAL_LEDGER_ACCOUNTS
    )
