# Dependency Injection Pattern for Authorization

## 概述

我们使用 FastAPI 的**依赖注入（Dependency Injection）**系统来处理所有端点的授权和验证逻辑，而不是在每个路由函数中手动编写重复的验证代码。

## 为什么使用依赖注入？

### ❌ 旧方式（手动验证）
```python
@router.get("/{session_id}/datasets/tabular/{dataset_id}/records")
async def query_records(
    session_id: str,
    dataset_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    # 每个端点都要重复这些验证代码
    sess = await db.get(Session, session_id)
    if not sess or sess.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    result = await db.execute(select(TabularDataset).where(...))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # 实际业务逻辑
    service = TabularService(db)
    rows = await service.query_rows(dataset_id, ...)
    return rows
```

**问题：**
- 🔁 代码重复
- 🐛 容易出错（忘记验证或验证逻辑不一致）
- 📝 业务逻辑和验证逻辑混在一起
- 🧪 难以测试

### ✅ 新方式（依赖注入）
```python
@router.get("/{session_id}/datasets/tabular/{dataset_id}/records")
async def query_records(
    limit: int = 100,
    offset: int = 0,
    dataset: TabularDataset = Depends(get_valid_tabular_dataset),
    db: AsyncSession = Depends(get_db)
):
    # 验证已自动完成，直接使用 dataset 对象
    service = TabularService(db)
    rows = await service.query_rows(dataset.id, limit, offset)
    return rows
```

**优势：**
- ✨ 代码简洁
- 🔒 安全性保证（自动验证）
- 🧩 关注点分离
- 🧪 易于测试和复用

## 实现架构

### 1. 中心化的依赖函数 (`app/core/dependencies.py`)

```python
async def get_valid_session(
    session_id: str = Path(...),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Session:
    """验证 session 存在且属于当前用户"""
    session = await db.get(Session, session_id)
    if not session or session.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

async def get_valid_tabular_dataset(
    session_id: str = Path(...),
    dataset_id: str = Path(...),
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> TabularDataset:
    """验证 dataset 存在且属于用户的 session"""
    # 先验证 session
    session = await db.get(Session, session_id)
    if not session or session.user_id != user_id:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # 再验证 dataset
    result = await db.execute(
        select(TabularDataset).where(
            TabularDataset.id == dataset_id,
            TabularDataset.session_id == session_id
        )
    )
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset
```

### 2. 在路由中使用依赖

```python
# 只需要 session 验证
@router.post("/{session_id}/datasets/tabular")
async def create_dataset(
    dataset_in: TabularDatasetCreate,
    session: Session = Depends(get_valid_session),  # 自动验证 + 注入
    db: AsyncSession = Depends(get_db)
):
    new_dataset = TabularDataset(session_id=session.id, ...)
    # ...

# 需要 session + dataset 验证
@router.get("/{session_id}/datasets/tabular/{dataset_id}/records")
async def query_records(
    limit: int = 100,
    dataset: TabularDataset = Depends(get_valid_tabular_dataset),  # 自动验证
    db: AsyncSession = Depends(get_db)
):
    service = TabularService(db)
    return await service.query_rows(dataset.id, limit)
```

## FastAPI 依赖注入的工作原理

1. **请求到达** → FastAPI 检测到 `Depends(get_valid_tabular_dataset)`
2. **递归解析** → 发现它依赖 `session_id`, `dataset_id`, `user_id`, `db`
3. **自动提取** → 从 URL 路径提取 `session_id` 和 `dataset_id`
4. **调用依赖链** → 先调用 `get_current_user_id()`，再调用 `get_db()`
5. **执行验证** → 运行 `get_valid_tabular_dataset()` 中的验证逻辑
6. **注入结果** → 如果验证通过，将 `TabularDataset` 对象注入到路由函数
7. **处理请求** → 路由函数使用已验证的对象执行业务逻辑

## 对比总结

| 方面 | 手动验证 | 依赖注入 |
|------|---------|---------|
| 代码行数 | ~15 行/端点 | ~3 行/端点 |
| 可维护性 | ❌ 低 | ✅ 高 |
| 代码复用 | ❌ 无 | ✅ 完全复用 |
| 测试难度 | ❌ 困难 | ✅ 简单（Mock 依赖） |
| 一致性 | ❌ 易出错 | ✅ 保证一致 |
| 可读性 | ❌ 业务逻辑混杂 | ✅ 清晰分离 |

## 扩展性

如果需要添加新的验证逻辑（例如权限检查、速率限制），只需：

1. 在 `dependencies.py` 中创建新的依赖函数
2. 在需要的路由中添加 `Depends(new_dependency)`

```python
# 添加权限检查
async def require_admin(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> str:
    # 检查用户是否是管理员
    if not is_admin(user_id):
        raise HTTPException(status_code=403, detail="Admin required")
    return user_id

# 在路由中使用
@router.delete("/{session_id}/datasets/{dataset_id}")
async def delete_dataset(
    dataset: TabularDataset = Depends(get_valid_tabular_dataset),
    admin_id: str = Depends(require_admin),  # 额外的权限检查
    db: AsyncSession = Depends(get_db)
):
    # 只有管理员才能删除
    await db.delete(dataset)
    await db.commit()
```

## 最佳实践

1. ✅ **将所有验证逻辑放在 `dependencies.py` 中**
2. ✅ **使用类型注解让 IDE 提供自动补全**
3. ✅ **依赖函数应该返回已验证的对象，而不是 ID**
4. ✅ **使用描述性的函数名（如 `get_valid_*`）**
5. ✅ **在依赖中使用 `Path(...)` 明确参数来源**
6. ❌ **避免在路由函数中进行手动验证**
