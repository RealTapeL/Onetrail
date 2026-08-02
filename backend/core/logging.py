"""集中日志配置：后端、数据库、前端上报的错误统一落到仓库根目录 logs/ 下。"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# 仓库根目录下的 logs/（backend/core/logging.py → 上三级）
LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
BACKEND_LOG = LOG_DIR / "backend.log"
FRONTEND_LOG = LOG_DIR / "frontend.log"

_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
_formatter = logging.Formatter(_FORMAT)

CLIENT_LOGGER_NAME = "onetrail.frontend"


def _file_handler(path: Path) -> RotatingFileHandler:
    handler = RotatingFileHandler(path, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    handler.setFormatter(_formatter)
    return handler


def setup_logging() -> None:
    """配置 root logger：控制台 + backend.log；数据库错误一并收录。幂等。"""
    LOG_DIR.mkdir(exist_ok=True)
    root = logging.getLogger()
    if any(isinstance(h, RotatingFileHandler) for h in root.handlers):
        return  # 已初始化（如测试重复导入）
    root.setLevel(logging.INFO)
    root.addHandler(logging.StreamHandler())
    root.addHandler(_file_handler(BACKEND_LOG))
    root.handlers[0].setFormatter(_formatter)

    # SQLAlchemy 默认只在 echo=True 时输出；WARNING 级别会带上数据库连接/执行错误
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    # 前端上报日志单独一个文件，不混入后端日志流
    client = logging.getLogger(CLIENT_LOGGER_NAME)
    client.setLevel(logging.INFO)
    client.propagate = False
    if not client.handlers:
        client.addHandler(_file_handler(FRONTEND_LOG))


def get_client_logger() -> logging.Logger:
    return logging.getLogger(CLIENT_LOGGER_NAME)
