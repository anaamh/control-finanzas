from datetime import datetime
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, Session, create_engine, select

# --- CONEXIÓN A BASE DE DATOS EN LA NUBE (SUPABASE) ---
sqlite_url = "postgresql://postgres.wuorftaoixtanodllrxu:70K0zi5JJiEQwJFv@aws-1-eu-west-1.pooler.supabase.com:5432/postgres"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


# --- MODELOS DE DATOS ---
class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    type: str  # Tipo por defecto o tipo asociado al crearse


class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    description: Optional[str] = None
    category_id: int = Field(foreign_key="category.id")
    date: datetime = Field(default_factory=datetime.utcnow)


# --- ESQUEMAS DE ENTRADA (DTOs) ---
class CategoryCreate(SQLModel):
    name: str
    type: str


class TransactionCreate(SQLModel):
    amount: float
    description: Optional[str] = None
    category_id: int
    date: Optional[datetime] = None


# --- APLICACIÓN FASTAPI ---
app = FastAPI(title="Control de Finanzas API")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# --- ENDPOINTS DE CATEGORÍAS ---
@app.post("/categories/", response_model=Category)
def create_category(category: CategoryCreate, session: Session = Depends(get_session)):
    # Si la categoría ya existe (sin importar mayúsculas/minúsculas), la reutiliza
    existing = session.exec(select(Category).where(Category.name.ilike(category.name.strip()))).first()
    if existing:
        return existing

    db_category = Category(name=category.name.strip(), type=category.type.lower())
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


@app.get("/categories/", response_model=List[Category])
def read_categories(session: Session = Depends(get_session)):
    return session.exec(select(Category)).all()


# --- ENDPOINTS DE TRANSACCIONES ---
@app.post("/transactions/", response_model=Transaction)
def create_transaction(transaction: TransactionCreate, session: Session = Depends(get_session)):
    category = session.get(Category, transaction.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    db_transaction = Transaction(
        amount=transaction.amount,
        description=transaction.description,
        category_id=transaction.category_id,
        date=transaction.date if transaction.date else datetime.utcnow()
    )
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction


@app.get("/transactions/", response_model=List[Transaction])
def read_transactions(session: Session = Depends(get_session)):
    return session.exec(select(Transaction).order_by(Transaction.date.desc())).all()


# --- ENDPOINTS DE RESUMEN Y ESTADÍSTICAS ---
@app.get("/summary/balance")
def get_balance_summary(session: Session = Depends(get_session)):
    transactions = session.exec(select(Transaction, Category).where(Transaction.category_id == Category.id)).all()
    
    total_income = 0.0
    total_expense = 0.0
    
    for tx, cat in transactions:
        # El balance depende de si la transacción se registró como ingreso o gasto en el formulario
        if cat.type.lower() == "ingreso":
            total_income += tx.amount
        elif cat.type.lower() == "gasto":
            total_expense += tx.amount

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense
    }


@app.get("/summary/monthly-history")
def get_monthly_history(session: Session = Depends(get_session)):
    transactions = session.exec(select(Transaction, Category).where(Transaction.category_id == Category.id)).all()
    if not transactions:
        return []
    
    monthly_data = {}
    for tx, cat in transactions:
        period = tx.date.strftime("%Y-%m")
        if period not in monthly_data:
            monthly_data[period] = {"income": 0.0, "expense": 0.0}
        
        if cat.type.lower() == "ingreso":
            monthly_data[period]["income"] += tx.amount
        elif cat.type.lower() == "gasto":
            monthly_data[period]["expense"] += tx.amount
            
    sorted_periods = sorted(monthly_data.keys())
    history = []
    accumulated_balance = 0.0
    
    for period in sorted_periods:
        inc = monthly_data[period]["income"]
        exp = monthly_data[period]["expense"]
        net = inc - exp
        accumulated_balance += net
        
        history.append({
            "period": period,
            "income": inc,
            "expense": exp,
            "net": net,
            "ending_balance": accumulated_balance
        })
        
    return history


@app.get("/summary/monthly-comparison")
def get_monthly_comparison(session: Session = Depends(get_session)):
    history = get_monthly_history(session=session)
    
    if not history:
        return {
            "current_month": {"period": "N/A", "income": 0.0, "expense": 0.0},
            "previous_month": {"period": "N/A", "income": 0.0, "expense": 0.0},
            "comparison": {
                "income_difference": 0.0,
                "income_change_percentage": None,
                "expense_difference": 0.0,
                "expense_change_percentage": None
            }
        }
    
    curr = history[-1]
    prev = history[-2] if len(history) > 1 else {"period": "N/A", "income": 0.0, "expense": 0.0}
    
    inc_diff = curr["income"] - prev["income"]
    exp_diff = curr["expense"] - prev["expense"]
    
    inc_pct = round((inc_diff / prev["income"]) * 100, 2) if prev["income"] > 0 else None
    exp_pct = round((exp_diff / prev["expense"]) * 100, 2) if prev["expense"] > 0 else None
    
    return {
        "current_month": curr,
        "previous_month": prev,
        "comparison": {
            "income_difference": inc_diff,
            "income_change_percentage": inc_pct,
            "expense_difference": exp_diff,
            "expense_change_percentage": exp_pct
        }
    }