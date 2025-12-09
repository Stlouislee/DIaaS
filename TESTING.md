# DIaaS Testing Guide

## 🧪 Test Suite Overview

本项目包含全面的测试套件，涵盖单元测试、集成测试和端到端测试。

## 📁 测试结构

```
tests/
├── conftest.py                 # Pytest 配置和共享 fixtures
├── utils.py                    # 测试工具函数
├── unit/                       # 单元测试
│   ├── test_dependencies.py   # 依赖注入测试
│   ├── test_security.py       # 安全模块测试
│   └── test_services.py       # 服务层测试
├── integration/                # 集成测试
│   ├── test_sessions_api.py   # Sessions API 测试
│   ├── test_tabular_api.py    # Tabular API 测试
│   ├── test_graph_api.py      # Graph API 测试
│   ├── test_query_export_api.py  # Query & Export API 测试
│   └── test_users_api.py      # Users API 测试
└── e2e/                        # 端到端测试
    └── test_workflows.py      # 完整工作流测试
```

## 🚀 运行测试

### 安装测试依赖

```bash
pip install -r requirements-dev.txt
```

### 快速开始

```bash
# 运行所有测试
./run_tests.sh all

# 或使用 pytest 直接运行
pytest -v
```

### 按类型运行测试

```bash
# 运行单元测试
./run_tests.sh unit
pytest -v -m unit

# 运行集成测试
./run_tests.sh integration
pytest -v -m integration

# 运行端到端测试
./run_tests.sh e2e
pytest -v -m e2e

# 运行快速测试（单元 + 集成）
./run_tests.sh fast
```

### 生成覆盖率报告

```bash
# 生成 HTML 覆盖率报告
./run_tests.sh coverage

# 查看报告
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### 运行特定测试

```bash
# 运行特定文件
pytest tests/unit/test_security.py -v

# 运行特定测试类
pytest tests/unit/test_dependencies.py::TestGetValidSession -v

# 运行特定测试函数
pytest tests/unit/test_security.py::TestKeyPattern::test_valid_key_matches -v

# 使用关键字过滤
pytest -k "session" -v
pytest -k "create and not delete" -v
```

## 📊 测试标记

测试使用标记（markers）进行分类：

```python
@pytest.mark.unit           # 单元测试
@pytest.mark.integration    # 集成测试
@pytest.mark.e2e            # 端到端测试
@pytest.mark.slow           # 慢速测试
```

按标记运行：
```bash
pytest -m "unit and not slow"
pytest -m "integration or e2e"
```

## 🔧 测试 Fixtures

### 数据库 Fixtures

```python
async def test_example(test_db: AsyncSession):
    """test_db 提供测试数据库会话"""
    # 测试代码
```

### API 客户端 Fixtures

```python
async def test_api(test_client: AsyncClient, auth_headers: dict):
    """test_client 提供已配置的 HTTP 客户端"""
    response = await test_client.get("/api/v1/sessions/", headers=auth_headers)
```

### 测试数据 Fixtures

```python
async def test_with_data(
    test_session: Session,
    test_tabular_dataset: TabularDataset,
    test_graph_dataset: GraphDataset
):
    """自动创建测试数据"""
    # 测试代码
```

## 📝 编写测试的最佳实践

### 1. 测试命名

```python
# ✅ 好的命名
def test_create_session_returns_201()
def test_invalid_api_key_raises_403()
def test_delete_nonexistent_session_returns_404()

# ❌ 不好的命名
def test_1()
def test_session()
def test_api()
```

### 2. 使用 AAA 模式

```python
async def test_example(test_client, auth_headers):
    # Arrange - 准备测试数据
    session_data = {"name": "Test Session"}
    
    # Act - 执行操作
    response = await test_client.post(
        "/api/v1/sessions/",
        json=session_data,
        headers=auth_headers
    )
    
    # Assert - 验证结果
    assert response.status_code == 201
    assert response.json()["name"] == "Test Session"
```

### 3. 测试边界情况

```python
class TestSessionCreation:
    async def test_create_with_valid_data(self):
        """测试正常情况"""
        pass
    
    async def test_create_without_name_fails(self):
        """测试缺少必填字段"""
        pass
    
    async def test_create_with_empty_name_fails(self):
        """测试空值"""
        pass
    
    async def test_create_with_very_long_name(self):
        """测试边界值"""
        pass
```

### 4. 使用参数化测试

```python
@pytest.mark.parametrize("api_key,expected_status", [
    ("valid-key-123", 200),
    ("short", 403),
    ("key with spaces", 403),
    ("", 403),
])
async def test_api_key_validation(test_client, api_key, expected_status):
    response = await test_client.get(
        "/api/v1/sessions/",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == expected_status
```

## 🐛 调试测试

### 运行单个失败的测试

```bash
# 只运行上次失败的测试
pytest --lf

# 先运行失败的测试，然后运行其他测试
pytest --ff
```

### 在第一个失败时停止

```bash
pytest -x
```

### 显示更详细的输出

```bash
pytest -vv
pytest -vv -s  # 显示 print 输出
```

### 使用 pdb 调试

```python
def test_example():
    import pdb; pdb.set_trace()
    # 测试代码
```

或使用 pytest 的内置调试：

```bash
pytest --pdb  # 失败时自动进入调试器
```

## 📈 测试覆盖率目标

| 模块 | 目标覆盖率 | 当前状态 |
|------|-----------|---------|
| `app/core/dependencies.py` | 100% | ✅ |
| `app/core/security.py` | 100% | ✅ |
| `app/services/` | 90%+ | 🟡 |
| `app/api/routes/` | 85%+ | 🟡 |
| `app/models/` | 80%+ | ⚪ |

## 🔄 持续集成

测试应该在 CI/CD 流水线中自动运行：

```yaml
# .github/workflows/test.yml 示例
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Run tests
        run: ./run_tests.sh coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## 🎯 测试检查清单

在提交代码前，确保：

- [ ] 所有测试通过
- [ ] 新功能有对应的测试
- [ ] Bug 修复有回归测试
- [ ] 覆盖率没有下降
- [ ] 没有跳过的测试（除非有充分理由）
- [ ] 测试运行时间合理（< 5 分钟）

## 📚 相关资源

- [Pytest 文档](https://docs.pytest.org/)
- [FastAPI 测试文档](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy 测试](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)

## 🤝 贡献测试

欢迎贡献新的测试！请遵循：

1. 为新功能编写测试
2. 保持测试简单和专注
3. 使用描述性的测试名称
4. 添加必要的文档字符串
5. 确保测试可以独立运行

## 💡 提示

- 使用 `pytest -k "keyword"` 快速运行相关测试
- 使用 `pytest --collect-only` 查看所有测试而不运行
- 使用 `pytest --durations=10` 查看最慢的 10 个测试
- 定期运行完整测试套件，不要只依赖快速测试
