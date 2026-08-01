import os

# 测试一律使用隔离的 SQLite 文件，并强制外部服务处于未配置状态，
# 保证用例不依赖本机 .env、PostgreSQL 或高德 API。
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ["AMAP_API_KEY"] = ""

import pytest

import app.main  # noqa: F401 - 注册全部 ORM 元数据
from database.base import Base
from database.session import engine


@pytest.fixture(autouse=True)
def _reset_database():
    if engine.url.get_backend_name() != "sqlite":
        pytest.skip("数据库重置仅在隔离的 SQLite 上自动执行，请使用 DATABASE_URL=sqlite:///./test.db 运行测试")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
