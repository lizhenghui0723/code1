from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime

# 用户相关模型
class UserCreate(BaseModel):
    """用户创建模型"""
    username: str
    password: str
    email: Optional[str] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """用户登录模型"""
    username: str
    password: str

    class Config:
        from_attributes = True

# 分类相关模型
class CategoryBase(BaseModel):
    """
    分类基础模型（仅一级分类）
    字段说明：
    - name: 分类名称
    - description: 分类描述
    """
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class CategoryCreate(CategoryBase):
    """分类创建模型"""
    class Config:
        from_attributes = True

class CategoryUpdate(CategoryBase):
    """分类更新模型"""
    class Config:
        from_attributes = True

class CategoryOut(CategoryBase):
    """
    分类输出模型
    字段说明：
    - id: 分类ID
    - created_at: 创建时间
    - updated_at: 更新时间
    """
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 商品相关模型 - 增强版
class ProductBase(BaseModel):
    """商品基础模型"""
    name: str
    description: Optional[str] = None
    price: float
    cost_price: float = 0
    stock: int = 0
    min_stock: int = 10
    unit: str = "件"
    category_id: Optional[int] = None
    sku: Optional[str] = None

    class Config:
        from_attributes = True

class ProductCreate(ProductBase):
    """商品创建模型"""
    class Config:
        from_attributes = True

class ProductUpdate(ProductBase):
    """商品更新模型"""
    class Config:
        from_attributes = True

class ProductOut(ProductBase):
    """商品输出模型"""
    id: int
    user_id: int
    sales_count: int = 0
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryOut] = None
    
    class Config:
        from_attributes = True

# 销售订单相关模型
class SalesOrderItemBase(BaseModel):
    """销售订单明细基础模型"""
    product_id: int
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True

class SalesOrderItemCreate(SalesOrderItemBase):
    """销售订单明细创建模型"""
    class Config:
        from_attributes = True

class SalesOrderItemOut(SalesOrderItemBase):
    """销售订单明细输出模型"""
    id: int
    order_id: int
    total_price: float
    product: Optional[ProductOut] = None
    
    class Config:
        from_attributes = True

class SalesOrderBase(BaseModel):
    """销售订单基础模型"""
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class SalesOrderCreate(SalesOrderBase):
    """销售订单创建模型"""
    items: List[SalesOrderItemCreate]

    class Config:
        from_attributes = True

class SalesOrderUpdate(BaseModel):
    """销售订单更新模型"""
    status: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class SalesOrderOut(SalesOrderBase):
    """销售订单输出模型"""
    id: int
    user_id: int
    order_no: str
    total_amount: float
    status: str
    created_at: datetime
    order_items: List[SalesOrderItemOut] = []
    
    class Config:
        from_attributes = True

# 库存相关模型 - 增强版
class StockChange(BaseModel):
    """库存变动模型"""
    product_id: int
    change: int
    type: str
    reference_no: Optional[str] = None

    class Config:
        from_attributes = True

class StockLogOut(BaseModel):
    """库存流水输出模型"""
    id: int
    product_id: int
    user_id: int
    change: int
    type: str
    before_stock: Optional[int]
    after_stock: Optional[int]
    reference_no: Optional[str]
    timestamp: datetime
    product: Optional[ProductOut] = None
    
    class Config:
        from_attributes = True

# 通知相关模型
class NotificationOut(BaseModel):
    """通知输出模型"""
    id: int
    type: str
    title: str
    content: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# 查询和筛选模型
class ProductQuery(BaseModel):
    """商品查询模型"""
    name: Optional[str] = None
    category_id: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    min_stock: Optional[int] = None
    max_stock: Optional[int] = None
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"
    page: int = 1
    page_size: int = 20

    class Config:
        from_attributes = True

# 统计模型
class DashboardStats(BaseModel):
    """仪表盘统计数据"""
    total_products: int
    total_categories: int
    total_orders: int
    total_sales: float
    low_stock_products: int
    today_sales: float
    month_sales: float
    recent_orders: List[SalesOrderOut] = []

    class Config:
        from_attributes = True

class CategoryStats(BaseModel):
    """分类统计数据"""
    category_name: str
    product_count: int
    total_stock: int
    total_value: float

    class Config:
        from_attributes = True

# Excel导入导出模型
class ImportResult(BaseModel):
    """导入结果"""
    success_count: int
    error_count: int
    errors: List[str] = []

    class Config:
        from_attributes = True

class ExportRequest(BaseModel):
    """导出请求"""
    export_type: str  # products/orders/stock_logs
    format: str = "excel"  # excel/csv
    filters: Optional[dict] = None

    class Config:
        from_attributes = True

# 自引用模型修复
CategoryOut.update_forward_refs() 