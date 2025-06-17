from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime

DATABASE_URL = 'sqlite:///./inventory.db'
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=True, comment='邮箱')
    # 用户与订单、商品、库存日志、通知的关系
    products = relationship('Product', backref='user')
    stock_logs = relationship('StockLog', backref='user')
    system_notifications = relationship('SystemNotification', backref='user')

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    cost_price = Column(Float, default=0, comment='成本价')
    stock = Column(Integer, default=0)
    min_stock = Column(Integer, default=10, comment='最低库存')
    unit = Column(String, default='件', comment='单位')
    category_id = Column(Integer, ForeignKey('categories.id'))
    sku = Column(String, nullable=True, comment='商品编码')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    sales_count = Column(Integer, default=0, comment='累计销量')
    # 商品与库存日志、订单明细的关系
    stock_logs = relationship('StockLog', backref='product')
    order_items = relationship('SalesOrderItem', backref='product')

class StockLog(Base):
    __tablename__ = 'stock_logs'
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    change = Column(Integer)
    type = Column(String)
    before_stock = Column(Integer, nullable=True, comment='变动前库存')
    after_stock = Column(Integer, nullable=True, comment='变动后库存')
    reference_no = Column(String, nullable=True, comment='关联单号')
    timestamp = Column(DateTime, default=datetime.utcnow)
    # 关联商品、用户已在上方定义

class SystemNotification(Base):
    """系统通知表"""
    __tablename__ = 'system_notifications'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type = Column(String)  # warning/info/error
    title = Column(String)
    content = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # 关联用户已在上方定义

class Category(Base):
    """
    商品分类表（每个用户独立）
    字段说明：
    - id: 分类ID
    - user_id: 用户ID
    - name: 分类名称
    - description: 分类描述
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(50), nullable=False, comment='分类名称')
    description = Column(String(200), nullable=True, comment='分类描述')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    # 分类与商品的关系
    products = relationship('Product', backref='category')
    # 分类与用户的关系
    user = relationship('User', backref='categories')

class SalesOrder(Base):
    __tablename__ = 'sales_orders'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    order_no = Column(String, unique=True, index=True, nullable=False)
    customer_name = Column(String, nullable=True)
    customer_phone = Column(String, nullable=True)
    total_amount = Column(Float, default=0)
    status = Column(String, default='pending')  # pending/completed/cancelled
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    # 订单与明细的关系
    order_items = relationship('SalesOrderItem', backref='order', cascade='all, delete-orphan')

class SalesOrderItem(Base):
    __tablename__ = 'sales_order_items'
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('sales_orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    # 关联订单、商品已在上方定义

# 初始化数据库
Base.metadata.create_all(bind=engine) 