from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=3, max_length=50)


class UserResponse(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=3, max_length=50)


class UserSettingsResponse(BaseModel):
    default_income_description: str | None
    default_expense_description: str | None
    default_income_category_id: int | None
    default_expense_category_id: int | None

    model_config = ConfigDict(from_attributes=True)


class UserSettingsUpdate(BaseModel):
    default_income_description: str | None = Field(default=None, max_length=120)
    default_expense_description: str | None = Field(default=None, max_length=120)
    default_income_category_id: int | None = None
    default_expense_category_id: int | None = None

    @model_validator(mode="after")
    def normalize_descriptions(self):
        self.default_income_description = (self.default_income_description or "").strip() or None
        self.default_expense_description = (self.default_expense_description or "").strip() or None
        return self


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    kind: str
    color: str = "#2563eb"


class CategoryResponse(CategoryCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TransactionCreate(BaseModel):
    description: str = Field(default="", max_length=120)
    amount: float = Field(gt=0)
    kind: str
    date: date
    category_id: int | None = None
    user_id: int
    notes: str | None = None

    @model_validator(mode="after")
    def fill_default_description(self):
        if self.description.strip():
            self.description = self.description.strip()
            return self

        self.description = "Receita" if self.kind == "income" else "Despesa"
        return self


class TransactionResponse(BaseModel):
    id: int
    description: str
    amount: float
    kind: str
    date: date
    category_id: int
    user_id: int
    notes: str | None
    created_at: datetime
    category_name: str
    category_color: str

    model_config = ConfigDict(from_attributes=True)


class MonthlyPoint(BaseModel):
    month: str
    income: float
    expense: float
    balance: float


class CategoryPoint(BaseModel):
    category: str
    total: float
    color: str


class DashboardResponse(BaseModel):
    month: str
    current_balance: float
    month_income: float
    month_expense: float
    by_category: list[CategoryPoint]
    by_month: list[MonthlyPoint]
    recent_transactions: list[TransactionResponse]


class ReportResponse(BaseModel):
    month: str | None
    total_income: float
    total_expense: float
    balance: float
    transaction_count: int
    categories: list[CategoryPoint]
    transactions: list[TransactionResponse]


class ExportInfoResponse(BaseModel):
    csv_ready: bool
    pdf_ready: bool
    message: str


class ServiceCreate(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    client_name: str | None = Field(default=None, max_length=120)
    amount: float = Field(gt=0)
    status: str = Field(default="pending")
    service_date: date
    received_date: date | None = None
    user_id: int
    notes: str | None = None

    @model_validator(mode="after")
    def normalize_service(self):
        self.title = self.title.strip()
        self.client_name = (self.client_name or "").strip() or None
        self.notes = (self.notes or "").strip() or None

        if self.status not in {"pending", "received"}:
            raise ValueError("Status do servico invalido.")

        if self.status == "received" and self.received_date is None:
            self.received_date = self.service_date

        if self.status == "pending":
            self.received_date = None

        return self


class ServiceUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=120)
    client_name: str | None = Field(default=None, max_length=120)
    amount: float | None = Field(default=None, gt=0)
    status: str | None = None
    service_date: date | None = None
    received_date: date | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def normalize_service(self):
        if self.title is not None:
            self.title = self.title.strip()
        if self.client_name is not None:
            self.client_name = self.client_name.strip() or None
        if self.notes is not None:
            self.notes = self.notes.strip() or None
        if self.status is not None and self.status not in {"pending", "received"}:
            raise ValueError("Status do servico invalido.")
        return self


class ServiceResponse(BaseModel):
    id: int
    title: str
    client_name: str | None
    amount: float
    status: str
    service_date: date
    received_date: date | None
    notes: str | None
    created_at: datetime
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class ServiceSummaryResponse(BaseModel):
    pending_amount: float
    received_amount: float
    total_services: int
