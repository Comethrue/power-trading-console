from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.core.errors import AppException, ErrorCode
from app.core.middleware import RequestIdMiddleware
from app.core.response import build_response
from app.db.sqlite import init_db

logger = logging.getLogger(__name__)


def _run_seed_data():
    """在应用启动后插入演示数据（幂等插入，不会重复）。"""
    try:
        from scripts.seed_data import run_seed as _run

        _run(clear=False)
    except Exception as e:
        logger.warning("演示数据初始化失败，将继续启动（不影响核心功能）: %s", e)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    _run_seed_data()
    yield

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIdMiddleware)
app.include_router(api_router, prefix="/api/v1")

_project_root = Path(__file__).resolve().parents[2]
_frontend = _project_root / "frontend"
# 必须挂载 dist：源码 index 引用 /src/main.js 会落到站点根路径 404，且未经过 Vite 无法运行
_frontend_dist = _frontend / "dist"
_index_html = _frontend_dist / "index.html"
# 前后端分离部署时，跳过前端静态文件挂载
_mount_console = settings.mount_frontend_dist and _index_html.exists()
if _mount_console:
    try:
        _idx_text = _index_html.read_text(encoding="utf-8", errors="replace")
    except OSError:
        _idx_text = ""
    if "/src/main.js" in _idx_text:
        logger.error(
            "frontend/dist/index.html 仍是开发版（含 /src/main.js），无法在后端托管。"
            "请在 frontend 目录执行: npm run build"
        )
    else:
        app.mount(
            "/console",
            StaticFiles(directory=str(_frontend_dist), html=True),
            name="console",
        )
        logger.info("控制台静态资源已挂载: %s -> /console/", _frontend_dist)
elif _frontend.exists() and not settings.mount_frontend_dist:
    logger.info("前后端分离部署模式，前端托管在 GitHub Pages，跳过后端挂载")
elif _frontend.exists():
    logger.warning(
        "未找到 frontend/dist/index.html，/console 未挂载。请在 frontend 目录执行 npm run build 后再访问；"
        "开发调试请使用 npm run dev（默认 http://localhost:5173/console/）。"
    )


@app.get("/")
def root():
    return {
        "message": f"{settings.app_name} is running",
        "docs": "/docs",
        "console": "/console",
    }


@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    body = build_response(
        request=request,
        success=False,
        code=exc.code,
        message=exc.message,
        data=None,
    )
    return JSONResponse(status_code=exc.status_code, content=body.model_dump())


def _sanitize_validation_errors(errors: list) -> list:
    """Strip non-serializable exception objects from Pydantic v2 error dicts."""
    sanitized = []
    for err in errors:
        clean = {k: v for k, v in err.items() if k != "ctx"}
        ctx = err.get("ctx")
        if ctx and isinstance(ctx, dict):
            clean["ctx"] = {k: str(v) if isinstance(v, Exception) else v for k, v in ctx.items()}
        sanitized.append(clean)
    return sanitized


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    body = build_response(
        request=request,
        success=False,
        code=ErrorCode.VALIDATION_ERROR,
        message="request validation failed",
        data=_sanitize_validation_errors(exc.errors()),
    )
    return JSONResponse(status_code=422, content=body.model_dump())


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    body = build_response(
        request=request,
        success=False,
        code=ErrorCode.INTERNAL_ERROR,
        message="internal server error",
        data=None,
    )
    return JSONResponse(status_code=500, content=body.model_dump())
