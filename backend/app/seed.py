from sqlalchemy.orm import Session

from . import models


DEFAULT_CATEGORIES = [
    {"name": "Salario", "kind": "income", "color": "#177245"},
    {"name": "Freelance", "kind": "income", "color": "#22c55e"},
    {"name": "Moradia", "kind": "expense", "color": "#dc2626"},
    {"name": "Alimentacao", "kind": "expense", "color": "#f97316"},
    {"name": "Transporte", "kind": "expense", "color": "#2563eb"},
    {"name": "Lazer", "kind": "expense", "color": "#7c3aed"},
    {"name": "Saude", "kind": "expense", "color": "#0891b2"},
]


def seed_defaults(db: Session) -> None:
    if not db.query(models.Category).first():
        for category_data in DEFAULT_CATEGORIES:
            db.add(models.Category(**category_data))

    if not db.query(models.User).filter(models.User.username == "admin").first():
        db.add(models.User(username="admin", password="1234"))

    db.commit()
