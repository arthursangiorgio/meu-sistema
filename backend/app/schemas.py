from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=3, max_length=50)


class UserResponse(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    kind: str
    color: str = "#2563eb"


class CategoryResponse(CategoryCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TransactionCreate(BaseModel):
    description: str = Field(min_length=2, max_length=120)
    amount: float = Field(gt=0)
    kind: str
    date: date
    category_id: int
    user_id: int
    notes: str | None = None


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
