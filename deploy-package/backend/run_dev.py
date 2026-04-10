"""
开发启动入口：无论从哪个目录执行，都会把进程工作目录与 sys.path 固定到 backend 根目录，
避免 `ModuleNotFoundError: No module named 'app'`。

用法（任选其一）：
  .venv_cpy313\\Scripts\\python.exe run_dev.py
  python run_dev.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent


def main() -> None:
    os.chdir(BACKEND_ROOT)
    root = str(BACKEND_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(BACKEND_ROOT / "app")],
    )


if __name__ == "__main__":
    main()
