"""Persona Weaver 独立桌面启动器

启动 uvicorn 后端 + 原生窗口(pywebview) 或浏览器。
pywebview 不可用时自动降级为浏览器模式。
"""

import argparse
import atexit
import os
import sys
import threading
import time

DATA_DIR = os.path.join(os.path.expanduser("~"), ".persona-weaver")
os.makedirs(DATA_DIR, exist_ok=True)
os.environ["PW_DATA_DIR"] = DATA_DIR


def ensure_single_instance():
    """Windows 文件锁单实例保护"""
    lock_file = os.path.join(DATA_DIR, ".lock")
    try:
        global _lock_fd
        _lock_fd = open(lock_file, "w")
        import msvcrt
        msvcrt.locking(_lock_fd.fileno(), msvcrt.LK_NBLCK, 1)
        return True
    except (IOError, OSError):
        print("Persona Weaver 已在运行中。")
        sys.exit(0)


_lock_fd = None

_webview_available = False
try:
    import webview  # noqa: F401
    _webview_available = True
except ImportError:
    pass


def _emergency_save():
    try:
        from app.core.persistence import save_config, save_reports
        from app.api.routes.config import _config_store
        from app.engine.chat_pipeline import _reports
        save_config(_config_store.get("default"))
        save_reports(_reports)
    except Exception:
        pass


def start_uvicorn(host: str, port: int):
    import uvicorn
    from app.main import app
    uvicorn.run(app, host=host, port=port, log_level="info")


def main():
    parser = argparse.ArgumentParser(description="Persona Weaver (人格织梦者)")
    parser.add_argument("--no-gui", action="store_true", help="强制使用浏览器而非原生窗口")
    parser.add_argument("--host", default="127.0.0.1", help="监听地址")
    parser.add_argument("--port", type=int, default=8000, help="监听端口")
    args = parser.parse_args()

    ensure_single_instance()
    atexit.register(_emergency_save)

    addr = f"http://{args.host}:{args.port}"

    # 启动后端
    server_thread = threading.Thread(target=start_uvicorn, args=(args.host, args.port), daemon=True)
    server_thread.start()

    use_gui = _webview_available and not args.no_gui

    if use_gui:
        time.sleep(2)
        print(f"启动原生窗口: {addr}")
        webview.create_window(
            title="人格织梦者 (Persona Weaver)",
            url=addr,
            width=1280,
            height=800,
            min_size=(960, 600),
            text_select=True,
        )
        webview.start()
    else:
        if args.no_gui or not _webview_available:
            if not _webview_available:
                print("(pywebview 未安装，使用浏览器模式)")
            print(f"后端已启动，即将打开浏览器: {addr}")
            time.sleep(2)
            import webbrowser
            webbrowser.open(addr)
            # 保持运行
            try:
                server_thread.join()
            except KeyboardInterrupt:
                print("\n正在退出...")


if __name__ == "__main__":
    main()
