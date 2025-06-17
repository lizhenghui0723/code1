from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from db import User, Category, Product, StockLog, SystemNotification, SalesOrder, SalesOrderItem, SessionLocal
from models import *
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime, timedelta, date
from fastapi.security import OAuth2PasswordRequestForm
from auth import create_access_token, get_current_user
import pandas as pd
import io
import uuid
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

app = FastAPI(title="ERP系统API", description="毕业设计 - 现代化企业资源管理系统", version="2.0.0")

# 允许所有来源跨域（开发环境用，生产请指定域名）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_order_no():
    """生成订单号"""
    return f"SO{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"

def check_and_create_notification(db: Session, user_id: int, product: Product):
    """检查库存并创建预警通知"""
    if product.stock <= product.min_stock:
        # 检查是否已有未读的同类通知
        existing = db.query(SystemNotification).filter(
            SystemNotification.user_id == user_id,
            SystemNotification.type == 'warning',
            SystemNotification.title.contains(product.name),
            SystemNotification.is_read == False
        ).first()
        
        if not existing:
            notification = SystemNotification(
                user_id=user_id,
                type='warning',
                title=f'商品 {product.name} 库存预警',
                content=f'商品 {product.name} 当前库存为 {product.stock}，已低于最低库存 {product.min_stock}，请及时补货！'
            )
            db.add(notification)
            db.commit()

# ================================
# 用户认证相关接口
# ================================

@app.post('/api/register', summary="用户注册")
def register(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册接口"""
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail='用户名已存在')
    
    # 创建用户
    db_user = User(
        username=user.username, 
        password=user.password,
        email=user.email if user.email else None
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"msg": "注册成功", "user_id": db_user.id}

@app.post('/api/token', summary="用户登录")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录接口，返回JWT token"""
    db_user = db.query(User).filter(
        User.username == form_data.username, 
        User.password == form_data.password
    ).first()
    
    if not db_user:
        raise HTTPException(
            status_code=401, 
            detail='用户名或密码错误',
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token = create_access_token(data={"sub": db_user.username})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user_id": db_user.id,
        "username": db_user.username
    }

# ================================
# 分类管理接口（仅一级分类）
# ================================

@app.get('/api/categories', response_model=List[CategoryOut], summary="获取分类列表")
def get_categories(db: Session = Depends(get_db)):
    """
    获取所有商品分类（一级分类，平铺结构）
    返回：分类列表
    """
    categories = db.query(Category).order_by(Category.id).all()
    return [CategoryOut.model_validate(c) for c in categories]

@app.post('/api/categories', response_model=CategoryOut, summary="创建分类")
def create_category(category: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    创建商品分类（仅一级分类）
    参数：category - 分类创建模型
    返回：新建分类信息
    """
    db_category = Category(
        user_id=current_user.id,
        name=category.name,
        description=category.description
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return CategoryOut.model_validate(db_category)

@app.put('/api/categories/{category_id}', response_model=CategoryOut, summary="更新分类")
def update_category(category_id: int, category: CategoryUpdate, db: Session = Depends(get_db)):
    """
    更新商品分类信息（仅一级分类）
    参数：category_id - 分类ID
    返回：更新后的分类信息
    """
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail='分类不存在')
    db_category.name = category.name
    db_category.description = category.description
    db_category.updated_at = datetime.now()
    db.commit()
    db.refresh(db_category)
    return CategoryOut.model_validate(db_category)

@app.delete('/api/categories/{category_id}', summary="删除分类")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """
    删除商品分类（仅一级分类）
    参数：category_id - 分类ID
    返回：删除结果
    """
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail='分类不存在')
    # 检查是否有商品使用此分类
    product_count = db.query(Product).filter(Product.category_id == category_id).count()
    if product_count > 0:
        raise HTTPException(status_code=400, detail=f'该分类下还有 {product_count} 个商品，无法删除')
    db.delete(db_category)
    db.commit()
    return {"msg": "删除成功"}

@app.get('/api/categories/{category_id}/stats', response_model=CategoryStats, summary="获取分类统计")
def get_category_stats(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取分类统计信息"""
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail='分类不存在')
    
    # 统计该分类下的商品
    stats = db.query(
        func.count(Product.id).label('product_count'),
        func.sum(Product.stock).label('total_stock'),
        func.sum(Product.stock * Product.price).label('total_value')
    ).filter(
        Product.category_id == category_id,
        Product.user_id == current_user.id
    ).first()
    
    return CategoryStats(
        category_name=category.name,
        product_count=stats.product_count or 0,
        total_stock=stats.total_stock or 0,
        total_value=stats.total_value or 0
    )



@app.post('/api/products/query', response_model=dict, summary="高级商品查询")
def query_products(
    query: ProductQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """高级商品查询接口，支持多条件筛选和排序"""
    # 构建查询
    q = db.query(Product).filter(Product.user_id == current_user.id)
    
    # 应用筛选条件
    if query.name:
        q = q.filter(Product.name.contains(query.name))
    if query.category_id:
        q = q.filter(Product.category_id == query.category_id)
    if query.min_price is not None:
        q = q.filter(Product.price >= query.min_price)
    if query.max_price is not None:
        q = q.filter(Product.price <= query.max_price)
    if query.min_stock is not None:
        q = q.filter(Product.stock >= query.min_stock)
    if query.max_stock is not None:
        q = q.filter(Product.stock <= query.max_stock)
    
    # 获取总数
    total = q.count()
    
    # 应用排序
    if query.sort_by:
        order_column = getattr(Product, query.sort_by, Product.created_at)
        if query.sort_order == 'asc':
            q = q.order_by(asc(order_column))
        else:
            q = q.order_by(desc(order_column))
    
    # 分页
    offset = (query.page - 1) * query.page_size
    products = q.options(joinedload(Product.category)).offset(offset).limit(query.page_size).all()
    
    return {
        "items": [ProductOut.model_validate(p) for p in products],
        "total": total,
        "page": query.page,
        "page_size": query.page_size,
        "total_pages": (total + query.page_size - 1) // query.page_size
    }

@app.get('/api/products', response_model=List[ProductOut], summary="获取商品列表")
def get_products(
    name: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
  
    query = db.query(Product).filter(Product.user_id == current_user.id)
    if name:
        query = query.filter(Product.name.contains(name))
    products = query.options(joinedload(Product.category)).all()
    return [ProductOut.model_validate(p) for p in products]

@app.post('/api/products', response_model=ProductOut, summary="创建商品")
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新商品"""
    # 生成SKU
    if not product.sku:
        product.sku = f"SKU{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
    
    db_product = Product(
        **product.dict(),
        user_id=current_user.id
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # 检查库存预警
    check_and_create_notification(db, current_user.id, db_product)
    
    return db_product

@app.put('/api/products/{product_id}', response_model=ProductOut, summary="更新商品")
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新商品信息"""
    db_product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()
    
    if not db_product:
        raise HTTPException(status_code=404, detail='商品不存在')
    
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    
    db_product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_product)
    
    # 检查库存预警
    check_and_create_notification(db, current_user.id, db_product)
    
    return db_product

@app.delete('/api/products/{product_id}', summary="删除商品")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除商品"""
    db_product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()
    
    if not db_product:
        raise HTTPException(status_code=404, detail='商品不存在')
    
    db.delete(db_product)
    db.commit()
    return {"msg": "删除成功"}

# ================================
# 销售订单管理接口
# ================================

@app.get('/api/sales-orders', response_model=dict, summary="获取销售订单列表")
def get_sales_orders(
    status: Optional[str] = None,
    order_no: Optional[str] = None,
    customer: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    sort_by: str = 'created_at',
    sort_order: str = 'desc',
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取销售订单列表，支持多条件搜索、排序、分页"""
    query = db.query(SalesOrder).filter(SalesOrder.user_id == current_user.id)
    if status:
        query = query.filter(SalesOrder.status == status)
    if order_no:
        query = query.filter(SalesOrder.order_no.contains(order_no))
    if customer:
        query = query.filter(or_(SalesOrder.customer_name.contains(customer), SalesOrder.customer_phone.contains(customer)))
    if start_time:
        query = query.filter(SalesOrder.created_at >= start_time)
    if end_time:
        query = query.filter(SalesOrder.created_at <= end_time)
    total = query.count()
    order_column = getattr(SalesOrder, sort_by, SalesOrder.created_at)
    if sort_order == 'asc':
        query = query.order_by(asc(order_column))
    else:
        query = query.order_by(desc(order_column))
    offset = (page - 1) * page_size
    orders = query.options(joinedload(SalesOrder.order_items).joinedload(SalesOrderItem.product)).offset(offset).limit(page_size).all()
    return {
        "items": [SalesOrderOut.model_validate(order) for order in orders],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }

@app.post('/api/sales-orders', response_model=SalesOrderOut, summary="创建销售订单")
def create_sales_order(
    order: SalesOrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建销售订单"""
    try:
        # 生成订单号
        order_no = generate_order_no()
        
        # 创建订单
        db_order = SalesOrder(
            user_id=current_user.id,
            order_no=order_no,
            customer_name=order.customer_name,
            customer_phone=order.customer_phone,
            notes=order.notes,
            status='pending',
            total_amount=0
        )
        db.add(db_order)
        db.flush()
        
        total_amount = 0
        
        # 创建订单明细并更新库存
        for item in order.items:
            # 获取商品信息
            product = db.query(Product).filter(
                Product.id == item.product_id,
                Product.user_id == current_user.id
            ).with_for_update().first()
            
            if not product:
                raise HTTPException(status_code=404, detail=f'商品ID {item.product_id} 不存在')
            
            if product.stock < item.quantity:
                raise HTTPException(status_code=400, detail=f'商品 {product.name} 库存不足，当前库存：{product.stock}')
            
            # 创建订单明细
            order_item = SalesOrderItem(
                order_id=db_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.quantity * item.unit_price
            )
            db.add(order_item)
            
            total_amount += order_item.total_price
            
            # 更新商品库存和销量
            before_stock = product.stock
            product.stock -= item.quantity
            product.sales_count += item.quantity
            
            # 记录库存流水
            stock_log = StockLog(
                product_id=product.id,
                user_id=current_user.id,
                change=-item.quantity,
                type='销售',
                before_stock=before_stock,
                after_stock=product.stock,
                reference_no=order_no,
                timestamp=datetime.utcnow()
            )
            db.add(stock_log)
            
            # 检查库存预警
            check_and_create_notification(db, current_user.id, product)
        
        # 更新订单总金额
        db_order.total_amount = total_amount
        
        db.commit()
        db.refresh(db_order)
        
        return SalesOrderOut.model_validate(db_order)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.put('/api/sales-orders/{order_id}', response_model=SalesOrderOut, summary="更新订单状态")
def update_sales_order(
    order_id: int,
    update: SalesOrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新订单状态"""
    db_order = db.query(SalesOrder).filter(
        SalesOrder.id == order_id,
        SalesOrder.user_id == current_user.id
    ).first()
    
    if not db_order:
        raise HTTPException(status_code=404, detail='订单不存在')
    
    if update.status:
        db_order.status = update.status
    if update.notes is not None:
        db_order.notes = update.notes
    
    db.commit()
    db.refresh(db_order)
    
    return db_order

# 库存管理接口 - 增强版


@app.post('/api/stock', summary="库存调整")
def change_stock(
    stock: StockChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """库存调整（入库/出库/调整）"""
    try:
        db_product = db.query(Product).filter(
            Product.id == stock.product_id,
            Product.user_id == current_user.id
        ).with_for_update().first()
        
        if not db_product:
            raise HTTPException(status_code=404, detail='商品不存在')
        
        # 记录变动前库存
        before_stock = db_product.stock
        
        # 更新库存
        if stock.type == '入库':
            db_product.stock += stock.change
        elif stock.type == '出库':
            if db_product.stock < stock.change:
                raise HTTPException(status_code=400, detail='库存不足')
            db_product.stock -= stock.change
        else:  # 调整
            db_product.stock = stock.change
        
        # 记录库存流水
        db_log = StockLog(
            product_id=stock.product_id,
            user_id=current_user.id,
            change=stock.change if stock.type != '出库' else -stock.change,
            type=stock.type,
            before_stock=before_stock,
            after_stock=db_product.stock,
            reference_no=stock.reference_no,
            timestamp=datetime.utcnow()
        )
        db.add(db_log)
        
        db.commit()
        
        # 检查库存预警
        check_and_create_notification(db, current_user.id, db_product)
        
        return {
            "msg": f"{stock.type}成功", 
            "current_stock": db_product.stock,
            "log_id": db_log.id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get('/api/stock_logs', response_model=dict, summary="获取库存流水")
def get_stock_logs(
    product_name: Optional[str] = None,
    type: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    sort_by: str = 'timestamp',
    sort_order: str = 'desc',
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取库存流水记录，支持多条件搜索、排序、分页"""
    query = db.query(StockLog).filter(StockLog.user_id == current_user.id)
    if product_name:
        query = query.join(Product).filter(Product.name.contains(product_name))
    if type:
        query = query.filter(StockLog.type == type)
    if start_time:
        query = query.filter(StockLog.timestamp >= start_time)
    if end_time:
        query = query.filter(StockLog.timestamp <= end_time)
    total = query.count()
    order_column = getattr(StockLog, sort_by, StockLog.timestamp)
    if sort_order == 'asc':
        query = query.order_by(asc(order_column))
    else:
        query = query.order_by(desc(order_column))
    offset = (page - 1) * page_size
    logs = query.options(joinedload(StockLog.product)).offset(offset).limit(page_size).all()
    return {
        "items": [StockLogOut.model_validate(log) for log in logs],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }

# ================================
# 统计分析接口
# ================================

@app.get('/api/dashboard/stats', response_model=DashboardStats, summary="获取仪表盘统计数据")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取仪表盘统计数据"""
    try:
        total_products = db.query(Product).filter(Product.user_id == current_user.id).count()
        total_categories = db.query(Category).count()
        total_orders = db.query(SalesOrder).filter(SalesOrder.user_id == current_user.id).count()
        total_sales = db.query(func.coalesce(func.sum(SalesOrder.total_amount), 0)).filter(SalesOrder.user_id == current_user.id).scalar() or 0
        low_stock_products = db.query(Product).filter(Product.user_id == current_user.id, Product.stock <= Product.min_stock).count()
        today = datetime.now().date()
        today_sales = db.query(func.coalesce(func.sum(SalesOrder.total_amount), 0)).filter(
            SalesOrder.user_id == current_user.id,
            func.date(SalesOrder.created_at) == today
        ).scalar() or 0
        month_start = datetime.now().replace(day=1).date()
        month_sales = db.query(func.coalesce(func.sum(SalesOrder.total_amount), 0)).filter(
            SalesOrder.user_id == current_user.id,
            func.date(SalesOrder.created_at) >= month_start
        ).scalar() or 0
        recent_orders = db.query(SalesOrder).filter(SalesOrder.user_id == current_user.id).order_by(desc(SalesOrder.created_at)).limit(5).all()
        return DashboardStats(
            total_products=total_products,
            total_categories=total_categories,
            total_orders=total_orders,
            total_sales=total_sales,
            low_stock_products=low_stock_products,
            today_sales=today_sales,
            month_sales=month_sales,
            recent_orders=[SalesOrderOut.model_validate(o) for o in recent_orders]
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")

@app.get('/api/dashboard/sales-trend', summary="获取销售趋势数据")
def get_sales_trend(
    days: int = Query(7, description="统计天数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取销售趋势数据"""
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        # 查询每日销售数据
        daily_sales = db.query(
            func.date(SalesOrder.created_at).label('date'),
            func.count(SalesOrder.id).label('order_count'),
            func.coalesce(func.sum(SalesOrder.total_amount), 0.0).label('total_amount')
        ).filter(
            SalesOrder.user_id == current_user.id,
            SalesOrder.created_at >= start_date,
            SalesOrder.status != 'cancelled'
        ).group_by(
            func.date(SalesOrder.created_at)
        ).all()
        # 用字符串日期做key，保证类型一致
        date_dict = {str(item.date): item for item in daily_sales}
        result = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            if date_str in date_dict:
                item = date_dict[date_str]
                result.append({
                    'date': date_str,
                    'order_count': item.order_count,
                    'total_amount': float(item.total_amount)
                })
            else:
                result.append({
                    'date': date_str,
                    'order_count': 0,
                    'total_amount': 0.0
                })
            current_date += timedelta(days=1)
        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"获取销售趋势数据失败: {str(e)}")

@app.get('/api/dashboard/category-sales', summary="获取分类销售统计")
def get_category_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取分类销售统计"""
    try:
        # 查询各分类的销售数据
        category_sales = db.query(
            Category.name,
            func.coalesce(func.sum(SalesOrderItem.quantity), 0).label('quantity'),
            func.coalesce(func.sum(SalesOrderItem.total_price), 0.0).label('amount')
        ).join(
            Product, Product.category_id == Category.id
        ).join(
            SalesOrderItem, SalesOrderItem.product_id == Product.id
        ).join(
            SalesOrder, and_(
                SalesOrder.id == SalesOrderItem.order_id,
                SalesOrder.status != 'cancelled'
            )
        ).filter(
            Product.user_id == current_user.id
        ).group_by(
            Category.id, Category.name
        ).all()
        # 添加未分类商品的销售数据
        uncategorized_sales = db.query(
            func.coalesce(func.sum(SalesOrderItem.quantity), 0).label('quantity'),
            func.coalesce(func.sum(SalesOrderItem.total_price), 0.0).label('amount')
        ).join(
            Product, Product.id == SalesOrderItem.product_id
        ).join(
            SalesOrder, and_(
                SalesOrder.id == SalesOrderItem.order_id,
                SalesOrder.status != 'cancelled'
            )
        ).filter(
            Product.user_id == current_user.id,
            Product.category_id == None
        ).first()
        result = []
        for item in category_sales:
            result.append({
                'name': item.name,
                'quantity': int(item.quantity),
                'amount': float(item.amount)
            })
        if uncategorized_sales and uncategorized_sales.quantity:
            result.append({
                'name': '未分类',
                'quantity': int(uncategorized_sales.quantity),
                'amount': float(uncategorized_sales.amount)
            })
        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"获取分类销售统计失败: {str(e)}")

@app.get('/api/dashboard/stock-status', summary="获取库存状态统计")
def get_stock_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取库存状态统计"""
    try:
        # 充足：库存 > 最低库存 * 2
        sufficient = db.query(Product).filter(
            Product.user_id == current_user.id,
            Product.stock > Product.min_stock * 2
        ).count()
        
        # 正常：最低库存 < 库存 <= 最低库存 * 2
        normal = db.query(Product).filter(
            Product.user_id == current_user.id,
            Product.stock > Product.min_stock,
            Product.stock <= Product.min_stock * 2
        ).count()
        
        # 预警：0 < 库存 <= 最低库存
        warning = db.query(Product).filter(
            Product.user_id == current_user.id,
            Product.stock > 0,
            Product.stock <= Product.min_stock
        ).count()
        
        # 缺货：库存 = 0
        out_of_stock = db.query(Product).filter(
            Product.user_id == current_user.id,
            Product.stock == 0
        ).count()
        
        return [
            {"name": "充足", "value": sufficient, "color": "#67C23A"},
            {"name": "正常", "value": normal, "color": "#409EFF"},
            {"name": "预警", "value": warning, "color": "#E6A23C"},
            {"name": "缺货", "value": out_of_stock, "color": "#F56C6C"}
        ]
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"获取库存状态统计失败: {str(e)}")

# ================================
# 通知管理接口
# ================================

@app.get('/api/notifications', response_model=List[NotificationOut], summary="获取通知列表")
def get_notifications(
    is_read: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取通知列表"""
    try:
        query = db.query(SystemNotification).filter(
            SystemNotification.user_id == current_user.id
        )
        
        if is_read is not None:
            query = query.filter(SystemNotification.is_read == is_read)
        
        notifications = query.order_by(desc(SystemNotification.created_at)).limit(50).all()
        
        return [NotificationOut.model_validate(n) for n in notifications]
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"获取通知列表失败: {str(e)}")

@app.put('/api/notifications/{notification_id}/read', summary="标记通知为已读")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """标记通知为已读"""
    try:
        notification = db.query(SystemNotification).filter(
            SystemNotification.id == notification_id,
            SystemNotification.user_id == current_user.id
        ).with_for_update().first()
        
        if not notification:
            raise HTTPException(status_code=404, detail='通知不存在')
        
        notification.is_read = True
        db.commit()
        
        return {"msg": "标记成功", "notification": NotificationOut.model_validate(notification)}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.put('/api/notifications/read-all', summary="标记所有通知为已读")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """标记所有通知为已读"""
    try:
        result = db.query(SystemNotification).filter(
            SystemNotification.user_id == current_user.id,
            SystemNotification.is_read == False
        ).update({"is_read": True})
        
        db.commit()
        
        return {
            "msg": "全部标记成功",
            "updated_count": result
        }
    except Exception as e:
        db.rollback()
    db.query(SystemNotification).filter(
        SystemNotification.user_id == current_user.id,
        SystemNotification.is_read == False
    ).update({"is_read": True})
    
    db.commit()
    
    return {"msg": "全部标记成功"}

# ================================
# Excel导入导出接口
# ================================

@app.get('/api/export/products', summary="导出商品数据")
def export_products(
    format: str = Query('excel', description="导出格式: excel/csv"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """导出商品数据为Excel或CSV"""
    # 查询商品数据
    products = db.query(Product).filter(
        Product.user_id == current_user.id
    ).options(joinedload(Product.category)).all()
    
    # 构建数据
    data = []
    for product in products:
        data.append({
            '商品编码': product.sku or '',
            '商品名称': product.name,
            '商品描述': product.description or '',
            '分类': product.category.name if product.category else '未分类',
            '销售价格': product.price,
            '成本价格': product.cost_price,
            '当前库存': product.stock,
            '最低库存': product.min_stock,
            '单位': product.unit,
            '累计销量': product.sales_count,
            '创建时间': product.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    df = pd.DataFrame(data)
    
    if format == 'csv':
        # 导出CSV
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            media_type='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename=products_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            }
        )
    else:
        # 导出Excel
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='商品数据', index=False)
            
            # 获取工作表
            worksheet = writer.sheets['商品数据']
            
            # 设置列宽
            column_widths = {
                'A': 15,  # 商品编码
                'B': 20,  # 商品名称
                'C': 30,  # 商品描述
                'D': 15,  # 分类
                'E': 12,  # 销售价格
                'F': 12,  # 成本价格
                'G': 12,  # 当前库存
                'H': 12,  # 最低库存
                'I': 10,  # 单位
                'J': 12,  # 累计销量
                'K': 20   # 创建时间
            }
            
            for col, width in column_widths.items():
                worksheet.column_dimensions[col].width = width
            
            # 设置标题行样式
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_alignment = Alignment(horizontal="center", vertical="center")
            
            for cell in worksheet[1]:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
        
        output.seek(0)
        
        return StreamingResponse(
            output,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={
                'Content-Disposition': f'attachment; filename=products_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            }
        )

@app.get('/api/export/template', summary="下载导入模板")
def download_import_template():
    """下载商品导入模板"""
    # 创建模板数据
    template_data = {
        '商品名称*': ['示例商品1', '示例商品2'],
        '商品描述': ['这是商品描述', ''],
        '分类名称': ['电子产品', '办公用品'],
        '销售价格*': [99.99, 29.99],
        '成本价格': [50.00, 15.00],
        '当前库存*': [100, 200],
        '最低库存': [10, 20],
        '单位': ['件', '个'],
        '商品编码': ['SKU001', 'SKU002']
    }
    
    df = pd.DataFrame(template_data)
    
    # 创建Excel文件
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='商品导入模板', index=False)
        
        # 添加说明sheet
        instructions = pd.DataFrame({
            '说明': [
                '1. 带*号的字段为必填项',
                '2. 商品名称不能重复',
                '3. 价格和库存必须为数字',
                '4. 分类名称如果不存在会自动创建',
                '5. 商品编码如果不填写会自动生成',
                '6. 请勿修改表头名称',
                '7. 导入前请删除示例数据'
            ]
        })
        instructions.to_excel(writer, sheet_name='使用说明', index=False)
        
        # 设置样式
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            
            # 设置列宽
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
            
            # 设置标题行样式
            header_font = Font(bold=True)
            for cell in worksheet[1]:
                cell.font = header_font
    
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition': 'attachment; filename=product_import_template.xlsx'
        }
    )

@app.post('/api/import/products', response_model=ImportResult, summary="导入商品数据")
async def import_products(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """从Excel文件导入商品数据"""
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail='请上传Excel文件')
    
    # 读取文件
    contents = await file.read()
    
    try:
        df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'文件读取失败: {str(e)}')
    
    # 验证必填字段
    required_columns = ['商品名称*', '销售价格*', '当前库存*']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise HTTPException(status_code=400, detail=f'缺少必填列: {", ".join(missing_columns)}')
    
    success_count = 0
    error_count = 0
    errors = []
    
    # 处理每一行数据
    for index, row in df.iterrows():
        try:
            # 获取或创建分类
            category_id = None
            if '分类名称' in row and pd.notna(row['分类名称']):
                category = db.query(Category).filter(
                    Category.user_id == current_user.id,
                    Category.name == row['分类名称']
                ).first()
                if not category:
                    category = Category(
                        user_id=current_user.id,
                        name=row['分类名称']
                    )
                    db.add(category)
                    db.flush()
                category_id = category.id
            
            # 创建商品
            product = Product(
                user_id=current_user.id,
                name=row['商品名称*'],
                description=row.get('商品描述', '') if pd.notna(row.get('商品描述')) else '',
                category_id=category_id,
                price=float(row['销售价格*']),
                cost_price=float(row.get('成本价格', 0)) if pd.notna(row.get('成本价格')) else 0,
                stock=int(row['当前库存*']),
                min_stock=int(row.get('最低库存', 10)) if pd.notna(row.get('最低库存')) else 10,
                unit=row.get('单位', '件') if pd.notna(row.get('单位')) else '件',
                sku=row.get('商品编码') if pd.notna(row.get('商品编码')) else f"SKU{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
            )
            
            db.add(product)
            success_count += 1
            
        except Exception as e:
            error_count += 1
            errors.append(f'第{index + 2}行: {str(e)}')
    
    # 提交事务
    if success_count > 0:
        db.commit()
    
    return ImportResult(
        success_count=success_count,
        error_count=error_count,
        errors=errors
    )

# ================================
# 原有接口保留（兼容性）
# ================================

@app.get('/api/total_stock', summary="获取总库存")
def get_total_stock(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取总库存"""
    total = db.query(func.sum(Product.stock)).filter(
        Product.user_id == current_user.id
    ).scalar()
    
    return {"total": total or 0}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)