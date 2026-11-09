from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, database, schemas

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Bank System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/api/users")
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first
    if db_user:
        return db_user
    new_user = models.User(username = user.username, balance = 5000.0)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.get("/api/user/{user_id}")
def get_user(user_id: int, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == user.id).first()
    if not user:
        raise HTTPException(status_code=404, detail = "Пользователь не найден")
    return user

@app.post("/api/deposit")
def deposit(data: schemas.Transactions, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail= "Пользователь не найден")

    user.balance +=data.amount

    tx= models.Transaction(user_id=user.id, type='add amount', amount=data.amount)
    db.add(tx)
    db.commit()
    return {"message": "Success apply", "new balance": user.balance}

@app.post("/api/withdraw")
def withdraw(data:schemas.TransactionsCreate, db : Session=Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code = 404,  detail="Пользователь не найден")

    if user.balance < data.amount:
        raise HTTPException(status_code=404, detail = "Недостаточно средств")

    user.balance -= data.amount
    tx = models.Transaction(user_id = user.id, type = "Снятие", amount = data.amount)
    db.add(tx)
    db.commit()
    return{"message": "Success", "new_balance": user.balance}

@app.get("/api/transactions/{user_id}")
def get_transactions(user_id: int, db:Session=Depends(database.get_db)):
    txs = db.query(models.Transaction).filter(models.Transaction.user_id == user_id).all()
    return txs
    
