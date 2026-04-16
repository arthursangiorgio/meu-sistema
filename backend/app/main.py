import csv
import io

from sqlalchemy import inspect, text
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy.orm import Session, joinedload

from . import models, schemas, services
from .database import Base, SessionLocal, engine, get_db
from .seed import seed_defaults


app = FastAPI(title="Expense Control API", version="0.1.0")

def ensure_user_settings_columns():
    inspector = inspect(engine)
    columns = {column["name"] for column in inspector.get_columns("users")}
    missing_columns = {
        "default_income_description": "ALTER TABLE users ADD COLUMN default_income_description VARCHAR",
        "default_expense_description": "ALTER TABLE users ADD COLUMN default_expense_description VARCHAR",
        "default_income_category_id": "ALTER TABLE users ADD COLUMN default_income_category_id INTEGER",
        "default_expense_category_id": "ALTER TABLE users ADD COLUMN default_expense_category_id INTEGER",
    }

    if not missing_columns.keys() - columns:
        return

    with engine.begin() as connection:
        for column_name, statement in missing_columns.items():
            if column_name not in columns:
                connection.execute(text(statement))


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    ensure_user_settings_columns()
    db = SessionLocal()
    try:
        seed_defaults(db)
    finally:
        db.close()


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/login", response_model=schemas.UserResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == payload.username).first()
    if user and user.password == payload.password:
        return user
    if user:
        raise HTTPException(status_code=401, detail="Senha invalida.")

    new_user = models.User(username=payload.username, password=payload.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/api/users", response_model=list[schemas.UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.query(models.User).order_by(models.User.username.asc()).all()


@app.post("/api/users", response_model=schemas.UserResponse)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    exists = db.query(models.User).filter(models.User.username == payload.username).first()
    if exists:
        raise HTTPException(status_code=400, detail="Usuario ja cadastrado.")

    user = models.User(username=payload.username, password=payload.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.delete("/api/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado.")

    db.delete(user)
    db.commit()
    return {"message": "Usuario excluido com sucesso."}


@app.get("/api/users/{user_id}/settings", response_model=schemas.UserSettingsResponse)
def get_user_settings(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado.")
    return user


@app.put("/api/users/{user_id}/settings", response_model=schemas.UserSettingsResponse)
def update_user_settings(user_id: int, payload: schemas.UserSettingsUpdate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado.")

    if payload.default_income_category_id:
        income_category = db.query(models.Category).filter(models.Category.id == payload.default_income_category_id).first()
        if not income_category or income_category.kind != "income":
            raise HTTPException(status_code=400, detail="Categoria padrao de receita invalida.")

    if payload.default_expense_category_id:
        expense_category = db.query(models.Category).filter(models.Category.id == payload.default_expense_category_id).first()
        if not expense_category or expense_category.kind != "expense":
            raise HTTPException(status_code=400, detail="Categoria padrao de despesa invalida.")

    for field, value in payload.model_dump().items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@app.get("/api/categories", response_model=list[schemas.CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).order_by(models.Category.kind, models.Category.name).all()


@app.post("/api/categories", response_model=schemas.CategoryResponse)
def create_category(payload: schemas.CategoryCreate, db: Session = Depends(get_db)):
    exists = db.query(models.Category).filter(models.Category.name == payload.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Categoria ja cadastrada.")

    category = models.Category(**payload.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@app.get("/api/transactions", response_model=list[schemas.TransactionResponse])
def list_transactions(
    user_id: int = Query(...),
    month: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = (
        db.query(models.Transaction)
        .options(joinedload(models.Transaction.category))
        .filter(models.Transaction.user_id == user_id)
        .order_by(models.Transaction.date.desc(), models.Transaction.id.desc())
    )
    query = services.apply_month_filter(query, month)
    return [services.serialize_transaction(item) for item in query.all()]


@app.post("/api/transactions", response_model=schemas.TransactionResponse)
def create_transaction(payload: schemas.TransactionCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado.")

    category_id = payload.category_id
    if category_id is None:
        category_id = (
            user.default_income_category_id if payload.kind == "income" else user.default_expense_category_id
        )

    if category_id is None:
        raise HTTPException(status_code=400, detail="Selecione uma categoria ou defina uma categoria padrao.")

    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoria nao encontrada.")
    if category.kind != payload.kind:
        raise HTTPException(status_code=400, detail="Tipo da transacao e da categoria precisam ser iguais.")

    description = payload.description.strip()
    if not description:
        description = (
            user.default_income_description if payload.kind == "income" else user.default_expense_description
        ) or ("Receita" if payload.kind == "income" else "Despesa")

    transaction_payload = payload.model_dump()
    transaction_payload["category_id"] = category_id
    transaction_payload["description"] = description

    transaction = models.Transaction(**transaction_payload)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    transaction = (
        db.query(models.Transaction)
        .options(joinedload(models.Transaction.category))
        .filter(models.Transaction.id == transaction.id)
        .first()
    )
    return services.serialize_transaction(transaction)


@app.delete("/api/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Lancamento nao encontrado.")

    db.delete(transaction)
    db.commit()
    return {"message": "Lancamento excluido com sucesso."}


@app.get("/api/services", response_model=list[schemas.ServiceResponse])
def list_services(
    user_id: int = Query(...),
    month: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    service_items, _ = services.services_data(db, user_id, month)
    return service_items


@app.get("/api/services/summary", response_model=schemas.ServiceSummaryResponse)
def get_services_summary(
    user_id: int = Query(...),
    month: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    _, summary = services.services_data(db, user_id, month)
    return summary


@app.post("/api/services", response_model=schemas.ServiceResponse)
def create_service(payload: schemas.ServiceCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado.")

    service = models.Service(**payload.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    return services.serialize_service(service)


@app.put("/api/services/{service_id}", response_model=schemas.ServiceResponse)
def update_service(service_id: int, payload: schemas.ServiceUpdate, db: Session = Depends(get_db)):
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Servico nao encontrado.")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(service, field, value)

    if service.status == "received" and service.received_date is None:
        service.received_date = service.service_date
    if service.status == "pending":
        service.received_date = None

    db.commit()
    db.refresh(service)
    return services.serialize_service(service)


@app.delete("/api/services/{service_id}")
def delete_service(service_id: int, db: Session = Depends(get_db)):
    service = db.query(models.Service).filter(models.Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Servico nao encontrado.")

    db.delete(service)
    db.commit()
    return {"message": "Servico excluido com sucesso."}


@app.get("/api/dashboard", response_model=schemas.DashboardResponse)
def get_dashboard(
    user_id: int = Query(...),
    month: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return services.dashboard_data(db, user_id, month)


@app.get("/api/reports", response_model=schemas.ReportResponse)
def get_reports(
    user_id: int = Query(...),
    month: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return services.report_data(db, user_id, month)


@app.get("/api/export-info", response_model=schemas.ExportInfoResponse)
def export_info():
    return schemas.ExportInfoResponse(
        csv_ready=True,
        pdf_ready=True,
        message="As exportacoes em CSV e PDF ja estao disponiveis para download.",
    )


@app.get("/api/exports/csv")
def export_csv(
    user_id: int = Query(...),
    month: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    report = services.report_data(db, user_id, month)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["data", "descricao", "categoria", "tipo", "valor", "observacoes"])
    for item in report.transactions:
        writer.writerow(
            [
                item.date.isoformat(),
                item.description,
                item.category_name,
                "Receita" if item.kind == "income" else "Despesa",
                f"{item.amount:.2f}",
                item.notes or "",
            ]
        )

    data = io.BytesIO(output.getvalue().encode("utf-8-sig"))
    filename = f"relatorio-despesas-{month or 'geral'}.csv"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(data, media_type="text/csv; charset=utf-8", headers=headers)


@app.get("/api/exports/pdf")
def export_pdf(
    user_id: int = Query(...),
    month: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    report = services.report_data(db, user_id, month)
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 50

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(40, y, "Relatorio de Despesas")
    y -= 24

    pdf.setFont("Helvetica", 10)
    pdf.drawString(40, y, f"Mes: {month or 'Todos'}")
    y -= 18
    pdf.drawString(40, y, f"Receitas: R$ {report.total_income:.2f}")
    y -= 16
    pdf.drawString(40, y, f"Despesas: R$ {report.total_expense:.2f}")
    y -= 16
    pdf.drawString(40, y, f"Saldo: R$ {report.balance:.2f}")
    y -= 28

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(40, y, "Lancamentos")
    y -= 18
    pdf.setFont("Helvetica", 9)

    for item in report.transactions:
        line = (
            f"{item.date.isoformat()} | {item.description[:24]} | "
            f"{item.category_name[:18]} | {'Rec' if item.kind == 'income' else 'Desp'} | R$ {item.amount:.2f}"
        )
        pdf.drawString(40, y, line)
        y -= 14
        if y < 60:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 9)

    pdf.save()
    buffer.seek(0)
    filename = f"relatorio-despesas-{month or 'geral'}.pdf"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(buffer, media_type="application/pdf", headers=headers)
