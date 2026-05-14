import json
import os
import shutil
from pathlib import Path

import structlog

logger = structlog.get_logger()


def get_data_dir() -> Path:
    if env_dir := os.environ.get("PW_DATA_DIR"):
        path = Path(env_dir)
    else:
        path = Path.home() / ".persona-weaver"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_db_path() -> Path:
    return get_data_dir() / "persona_weaver.db"


def _write_json(filename: str, data: dict) -> None:
    path = get_data_dir() / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def _read_json(filename: str) -> dict | None:
    path = get_data_dir() / filename
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Config persistence ──


def save_config(config) -> None:
    if config is None:
        return
    data = {
        "provider": config.provider,
        "api_key": config.api_key,
        "base_url": config.base_url,
        "model": config.model,
    }
    _write_json("config.json", data)
    logger.info("config_saved")


def load_config() -> dict | None:
    return _read_json("config.json")


# ── Reports persistence ──


def save_reports(reports: dict) -> None:
    if not reports:
        return
    _write_json("reports.json", reports)
    logger.info("reports_saved", count=len(reports))


def load_reports() -> dict | None:
    return _read_json("reports.json")


# ── Sessions persistence (best-effort) ──


def save_sessions(sessions: dict) -> None:
    if not sessions:
        return
    serializable = {}
    for sid, state in sessions.items():
        if hasattr(state, "to_dict"):
            serializable[sid] = state.to_dict()
        else:
            serializable[sid] = dict(state)
    _write_json("sessions.json", serializable)
    logger.info("sessions_saved", count=len(serializable))


def load_sessions() -> dict | None:
    return _read_json("sessions.json")


# ── Clear all data ──


def clear_all_data() -> list[str]:
    cleared = []
    data_dir = get_data_dir()

    # Delete JSON files
    for fname in ["config.json", "reports.json", "sessions.json"]:
        fpath = data_dir / fname
        if fpath.exists():
            fpath.unlink()
            cleared.append(fname.replace(".json", ""))

    # Delete SQLite database and WAL/SHM files
    db_path = get_db_path()
    for suffix in ["", "-wal", "-shm"]:
        p = Path(str(db_path) + suffix)
        if p.exists():
            p.unlink()

    if db_path.exists():
        db_path.unlink()
        cleared.append("database")

    logger.info("all_data_cleared", cleared=cleared)
    return cleared
