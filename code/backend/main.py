from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.db import SessionLocal, User, Product, StockLog
from backend.models import UserCreate, UserLogin, ProductBase, ProductUpdate, ProductOut, StockChange, StockLogOut
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime
from fastapi.security import OAuth2PasswordRequestForm
from backend.auth import create_access_token, get_current_user

app = FastAPI()

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 用户注册
@app.post('/api/register')
def register(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail='用户名已存在')
    # 直接存储前端传来的MD5密码
    db_user = User(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"msg": "注册成功"}

# 用户登录，返回JWT token
@app.post('/api/token')
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 直接用MD5密码比对
    db_user = db.query(User).filter(User.username == form_data.username, User.password == form_data.password).first()
    if not db_user:
        raise HTTPException(status_code=400, detail='用户名或密码错误')
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# 商品列表（仅查自己）
@app.get('/api/products', response_model=List[ProductOut])
def get_products(name: str = Query(None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Product).filter(Product.user_id == current_user.id)
    if name:
        query = query.filter(Product.name.contains(name))
    return query.all()

# 新增商品（归属自己）
@app.post('/api/products', response_model=ProductOut)
def add_product(product: ProductBase, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_product = Product(**product.dict(), user_id=current_user.id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# 编辑商品（只能编辑自己）
@app.put('/api/products/{pid}', response_model=ProductOut)
def update_product(pid: int, product: ProductUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_product = db.query(Product).filter(Product.id == pid, Product.user_id == current_user.id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail='商品不存在')
    for k, v in product.dict().items():
        setattr(db_product, k, v)
    db.commit()
    db.refresh(db_product)
    return db_product

# 删除商品（只能删自己）
@app.delete('/api/products/{pid}')
def delete_product(pid: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_product = db.query(Product).filter(Product.id == pid, Product.user_id == current_user.id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail='商品不存在')
    db.delete(db_product)
    db.commit()
    return {"msg": "删除成功"}

# 商品入库/出库（只能操作自己商品）
@app.post('/api/stock')
def change_stock(stock: StockChange, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_product = db.query(Product).filter(Product.id == stock.product_id, Product.user_id == current_user.id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail='商品不存在')
    db_product.stock += stock.change if stock.type == '入库' else -stock.change
    db.add(StockLog(product_id=stock.product_id, user_id=current_user.id, change=stock.change if stock.type == '入库' else -stock.change, type=stock.type, timestamp=datetime.utcnow()))
    db.commit()
    return {"msg": f"{stock.type}成功"}

# 库存流水（仅查自己）
@app.get('/api/stock_logs', response_model=List[StockLogOut])
def get_stock_logs(product_id: int = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    q = db.query(StockLog).filter(StockLog.user_id == current_user.id)
    if product_id:
        q = q.filter(StockLog.product_id == product_id)
    return q.order_by(StockLog.timestamp.desc()).all()

# 总库存（仅自己）
@app.get('/api/total_stock')
def get_total_stock(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total = db.query(Product).filter(Product.user_id == current_user.id).with_entities(Product.stock).all()
    return {"total": sum([x[0] for x in total])} 