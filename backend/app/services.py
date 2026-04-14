from collections import defaultdict
from datetime import date

from sqlalchemy import extract, func
from sqlalchemy.orm import Session, joinedload

from . import models, schemas


def month_bounds(month_str: str | None) -> tuple[int | None, int | None]:
    if not month_str:
        return None, None
    year_str, month_num = month_str.split("-")
    return int(year_str), int(month_num)


def apply_month_filter(query, month_str: str | None):
    year, month = month_bounds(month_str)
    if year and month:
        query = query.filter(extract("year", models.Transaction.date) == year)
        query = query.filter(extract("month", models.Transaction.date) == month)
    return query


def serialize_transaction(transaction: models.Transaction) -> schemas.TransactionResponse:
    return schemas.TransactionResponse(
        id=transaction.id,
        description=transaction.description,
        amount=transaction.amount,
        kind=transaction.kind,
        date=transaction.date,
        category_id=transaction.category_id,
        user_id=transaction.user_id,
        notes=transaction.notes,
        created_at=transaction.created_at,
        category_name=transaction.category.name,
        category_color=transaction.category.color,
    )


def current_balance(db: Session, user_id: int) -> float:
    income = (
        db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0))
        .filter(models.Transaction.user_id == user_id, models.Transaction.kind == "income")
        .scalar()
    )
    expense = (
        db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0))
        .filter(models.Transaction.user_id == user_id, models.Transaction.kind == "expense")
        .scalar()
    )
    return float(income or 0) - float(expense or 0)


def month_totals(db: Session, user_id: int, month_str: str) -> tuple[float, float]:
    base_query = db.query(func.coalesce(func.sum(models.Transaction.amount), 0.0)).filter(
        models.Transaction.user_id == user_id
    )
    income = apply_month_filter(base_query.filter(models.Transaction.kind == "income"), month_str).scalar()
    expense = apply_month_filter(base_query.filter(models.Transaction.kind == "expense"), month_str).scalar()
    return float(income or 0), float(expense or 0)


def category_breakdown(db: Session, user_id: int, month_str: str | None) -> list[schemas.CategoryPoint]:
    query = (
        db.query(models.Category.name, models.Category.color, func.sum(models.Transaction.amount).label("total"))
        .join(models.Transaction.category)
        .filter(models.Transaction.user_id == user_id, models.Transaction.kind == "expense")
    )
    query = apply_month_filter(query, month_str)
    query = query.group_by(models.Category.name, models.Category.color).order_by(func.sum(models.Transaction.amount).desc())
    return [
        schemas.CategoryPoint(category=name, total=float(total), color=color)
        for name, color, total in query.all()
    ]


def monthly_series(db: Session, user_id: int) -> list[schemas.MonthlyPoint]:
    rows = (
        db.query(
            extract("year", models.Transaction.date).label("year"),
            extract("month", models.Transaction.date).label("month"),
            models.Transaction.kind,
            func.sum(models.Transaction.amount).label("total"),
        )
        .filter(models.Transaction.user_id == user_id)
        .group_by("year", "month", models.Transaction.kind)
        .order_by("year", "month")
        .all()
    )

    grouped: dict[str, dict[str, float]] = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
    for year, month, kind, total in rows:
        month_key = f"{int(year):04d}-{int(month):02d}"
        grouped[month_key][kind] = float(total or 0)

    return [
        schemas.MonthlyPoint(
            month=month_key,
            income=values["income"],
            expense=values["expense"],
            balance=values["income"] - values["expense"],
        )
        for month_key, values in sorted(grouped.items())
    ]


def recent_transactions(db: Session, user_id: int, month_str: str | None, limit: int = 8) -> list[schemas.TransactionResponse]:
    query = (
        db.query(models.Transaction)
        .options(joinedload(models.Transaction.category))
        .filter(models.Transaction.user_id == user_id)
        .order_by(models.Transaction.date.desc(), models.Transaction.id.desc())
    )
    query = apply_month_filter(query, month_str)
    return [serialize_transaction(item) for item in query.limit(limit).all()]


def report_data(db: Session, user_id: int, month_str: str | None) -> schemas.ReportResponse:
    query = (
        db.query(models.Transaction)
        .options(joinedload(models.Transaction.category))
        .filter(models.Transaction.user_id == user_id)
        .order_by(models.Transaction.date.desc(), models.Transaction.id.desc())
    )
    query = apply_month_filter(query, month_str)
    transactions = query.all()

    income = sum(item.amount for item in transactions if item.kind == "income")
    expense = sum(item.amount for item in transactions if item.kind == "expense")

    categories_map: dict[tuple[str, str], float] = defaultdict(float)
    for item in transactions:
        if item.kind == "expense":
            categories_map[(item.category.name, item.category.color)] += item.amount

    categories = [
        schemas.CategoryPoint(category=name, total=total, color=color)
        for (name, color), total in sorted(categories_map.items(), key=lambda pair: pair[1], reverse=True)
    ]

    return schemas.ReportResponse(
        month=month_str,
        total_income=income,
        total_expense=expense,
        balance=income - expense,
        transaction_count=len(transactions),
        categories=categories,
        transactions=[serialize_transaction(item) for item in transactions],
    )


def dashboard_data(db: Session, user_id: int, month_str: str | None) -> schemas.DashboardResponse:
    selected_month = month_str or date.today().strftime("%Y-%m")
    income, expense = month_totals(db, user_id, selected_month)
    return schemas.DashboardResponse(
        month=selected_month,
        current_balance=current_balance(db, user_id),
        month_income=income,
        month_expense=expense,
        by_category=category_breakdown(db, user_id, selected_month),
        by_month=monthly_series(db, user_id),
        recent_transactions=recent_transactions(db, user_id, selected_month),
    )
