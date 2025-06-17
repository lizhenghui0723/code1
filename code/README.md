# ERP系统

## 项目简介
ERP系统是一个基于 Python FastAPI + Vue3 + Element Plus 的现代化企业资源管理系统，支持用户注册、登录、商品管理、库存管理、入库出库流水、总库存统计等功能。系统采用 JWT 鉴权，数据存储于本地 SQLite，无需外部依赖，UI 现代美观，兼容主流浏览器和移动端。

## 主要功能
- 用户注册与登录（密码前端MD5加密，后端JWT鉴权）
- 商品信息管理（增删改查，仅可操作本人数据）
- 商品库存管理、入库、出库流水
- 总库存统计
- 响应式美观UI，支持移动端

## 技术栈
- 前端：Vue3 + Element Plus + Axios + CryptoJS
- 后端：Python 3 + FastAPI + SQLAlchemy + Uvicorn
- 数据库：SQLite（嵌入式）

## 目录结构
```
code/
  backend/        # 后端服务
    main.py       # FastAPI主入口
    db.py         # 数据模型与表结构
    models.py     # Pydantic模型
    auth.py       # JWT鉴权相关
    requirements.txt
  frontend/       # 前端Vue3项目
    src/          # 前端源码
    package.json  # 前端依赖
    index.html    # 网页入口
    vite.config.js# 前端代理配置
  scripts/        # 启动/关闭脚本
    start.sh      # 一键启动前后端
    stop.sh       # 一键关闭
  README.md       # 项目说明（本文件）
```

## 安装与启动
1. **安装依赖**
   - 后端：
     ```bash
     cd code/backend
     pip install -r requirements.txt
     ```
   - 前端：
     ```bash
     cd code/frontend
     npm install
     ```
2. **一键启动前后端**
   ```bash
   cd code/scripts
   bash start.sh
   ```
   - 后端默认 http://localhost:8000
   - 前端默认 http://localhost:5100

3. **关闭服务**
   ```bash
   bash stop.sh
   ```

## 鉴权与接口说明
- 所有商品、库存相关接口均需登录并携带JWT Token。
- 登录/注册时，前端用 CryptoJS.MD5(password) 加密密码后提交。
- 登录成功后，前端自动保存token，所有请求自动带上 `Authorization: Bearer <token>`。
- 商品和库存数据均为用户隔离，仅可操作和查询自己的数据。

## 注意事项
- **如数据库结构有变动（如新增user_id字段），需删除 `code/backend/inventory.db` 文件，重启后端自动生成新表。**
- 首次启动请先注册新用户再进行商品等操作。
- 如遇 500 错误，多为数据库表结构未同步导致。

## 常见问题排查
- **前端报 `crypto-js` 未找到**：请在 `code/frontend` 下执行 `npm install crypto-js`。
- **接口401/403**：请确认已登录且请求头带有正确的token。
