import os
from datetime import datetime, timezone
from typing import List, Optional, Union
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel, Field, Session, create_engine, select

# --- CONEXIÓN A BASE DE DATOS EN LA NUBE (SUPABASE / RENDER) ---
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.wuorftaoixtanodllrxu:70K0zi5JJiEQwJFv@aws-1-eu-west-1.pooler.supabase.com:5432/postgres"
)

# Motor de base de datos listo para PostgreSQL en la nube
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


# --- MODELOS DE DATOS (BASE DE DATOS INTACTA) ---
class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    type: str


class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    description: Optional[str] = None
    category_id: int = Field(foreign_key="category.id")
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# --- ESQUEMAS DE ENTRADA (DTOs) ---
class CategoryCreate(SQLModel):
    name: str
    type: str


class TransactionCreate(SQLModel):
    amount: float
    description: Optional[str] = None
    category_id: int
    type: Optional[str] = None
    date: Optional[Union[datetime, str]] = None


# --- DETERMINADOR PRECISO DE TIPO ---
def determine_type(tx_type_param: Optional[str], category: Optional[Category]) -> str:
    # 1. Prioridad: Tipo enviado directamente en el envío del formulario
    if tx_type_param and tx_type_param.strip():
        t = tx_type_param.strip().lower()
        if "ingres" in t or "income" in t:
            return "ingreso"
        if "gast" in t or "egres" in t or "expense" in t:
            return "gasto"

    # 2. Prioridad: Tipo definido en la categoría asociada
    if category and category.type:
        cat_type = category.type.strip().lower()
        if "gast" in cat_type or "egres" in cat_type or "expense" in cat_type:
            return "gasto"
        if "ingres" in cat_type or "income" in cat_type or "gananc" in cat_type:
            return "ingreso"

    # 3. Prioridad: Nombre de la categoría (regla de respaldo para datos antiguos)
    if category and category.name:
        cat_name = category.name.strip().lower()
        if any(w in cat_name for w in ["sueldo", "nomina", "nómina", "ingreso", "cobro", "ventas", "venta"]):
            return "ingreso"

    # 4. Por defecto: Todo movimiento no clasificado es GASTO
    return "gasto"


# --- APLICACIÓN FASTAPI ---
app = FastAPI(title="Control de Finanzas API")

# --- PERMISOS CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Error interno del servidor: {str(exc)}"},
        headers={"Access-Control-Allow-Origin": "*"}
    )


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# --- ENDPOINTS DE CATEGORÍAS ---
@app.post("/categories/", response_model=Category)
def create_category(category: CategoryCreate, session: Session = Depends(get_session)):
    try:
        existing = session.exec(select(Category).where(Category.name.ilike(category.name.strip()))).first()
        if existing:
            return existing

        db_category = Category(name=category.name.strip(), type=category.type.lower().strip())
        session.add(db_category)
        session.commit()
        session.refresh(db_category)
        return db_category
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear la categoría: {str(e)}")


@app.get("/categories/", response_model=List[Category])
def read_categories(session: Session = Depends(get_session)):
    return session.exec(select(Category)).all()


# --- ENDPOINTS DE TRANSACCIONES ---
@app.post("/transactions/")
def create_transaction(transaction: TransactionCreate, session: Session = Depends(get_session)):
    category = session.get(Category, transaction.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    parsed_date = datetime.now(timezone.utc)
    if transaction.date:
        if isinstance(transaction.date, datetime):
            parsed_date = transaction.date
        elif isinstance(transaction.date, str) and transaction.date.strip():
            try:
                parsed_date = datetime.fromisoformat(transaction.date.replace("Z", "+00:00"))
            except ValueError:
                try:
                    parsed_date = datetime.strptime(transaction.date, "%Y-%m-%d")
                except ValueError:
                    parsed_date = datetime.now(timezone.utc)

    if parsed_date.tzinfo is None:
        parsed_date = parsed_date.replace(tzinfo=timezone.utc)

    try:
        db_transaction = Transaction(
            amount=float(transaction.amount),
            description=transaction.description,
            category_id=transaction.category_id,
            date=parsed_date
        )
        session.add(db_transaction)
        session.commit()
        session.refresh(db_transaction)

        tx_type = determine_type(transaction.type, category)
        return {
            "id": db_transaction.id,
            "amount": db_transaction.amount,
            "description": db_transaction.description,
            "category_id": db_transaction.category_id,
            "date": db_transaction.date,
            "type": tx_type,
            "category_name": category.name
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error al guardar la transacción: {str(e)}")


@app.get("/transactions/")
def read_transactions(session: Session = Depends(get_session)):
    txs = session.exec(select(Transaction).order_by(Transaction.date.desc())).all()
    cats = session.exec(select(Category)).all()
    cat_map = {c.id: c for c in cats if c.id is not None}

    output = []
    for tx in txs:
        cat = cat_map.get(tx.category_id)
        tx_type = determine_type(None, cat)
        output.append({
            "id": tx.id,
            "amount": tx.amount,
            "description": tx.description,
            "category_id": tx.category_id,
            "date": tx.date,
            "type": tx_type,
            "category_name": cat.name if cat else "Sin categoría"
        })
    return output


# --- ENDPOINTS DE RESUMEN Y ESTADÍSTICAS ---
@app.get("/summary/balance")
def get_balance_summary(session: Session = Depends(get_session)):
    txs = session.exec(select(Transaction)).all()
    cats = session.exec(select(Category)).all()
    cat_map = {c.id: c for c in cats if c.id is not None}
    
    total_income = 0.0
    total_expense = 0.0
    
    for tx in txs:
        cat = cat_map.get(tx.category_id)
        amt = abs(tx.amount)
        if determine_type(None, cat) == "ingreso":
            total_income += amt
        else:
            total_expense += amt

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense
    }


@app.get("/summary/monthly-history")
def get_monthly_history(session: Session = Depends(get_session)):
    txs = session.exec(select(Transaction)).all()
    if not txs:
        return []
    
    cats = session.exec(select(Category)).all()
    cat_map = {c.id: c for c in cats if c.id is not None}
    
    monthly_data = {}
    for tx in txs:
        period = tx.date.strftime("%Y-%m")
        if period not in monthly_data:
            monthly_data[period] = {"income": 0.0, "expense": 0.0}
        
        cat = cat_map.get(tx.category_id)
        amt = abs(tx.amount)
        if determine_type(None, cat) == "ingreso":
            monthly_data[period]["income"] += amt
        else:
            monthly_data[period]["expense"] += amt
            
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
    
    inc_pct = round((inc_diff / prev["income"]) * 100, 2) if prev.get("income", 0) > 0 else None
    exp_pct = round((exp_diff / prev["expense"]) * 100, 2) if prev.get("expense", 0) > 0 else None
    
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