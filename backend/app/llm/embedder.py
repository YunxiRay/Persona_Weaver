"""嵌入引擎 — bge-large-zh-v1.5 单例加载，首次启动自动下载模型"""

import os
import threading
from pathlib import Path

import numpy as np
import structlog

logger = structlog.get_logger(__name__)

MODEL_NAME = "BAAI/bge-large-zh-v1.5"
EXPECTED_DIM = 1024


def _get_model_dir() -> Path:
    data_dir = os.environ.get("PW_DATA_DIR", os.path.join(os.path.expanduser("~"), ".persona-weaver"))
    return Path(data_dir) / "models" / "bge-large-zh-v1.5"


def _download_model(target_dir: Path) -> None:
    """从 HuggingFace 下载模型文件到 target_dir"""
    from huggingface_hub import snapshot_download

    logger.info("model_download_start", model=MODEL_NAME, target=str(target_dir))
    target_dir.mkdir(parents=True, exist_ok=True)
    snapshot_download(repo_id=MODEL_NAME, local_dir=str(target_dir), local_dir_use_symlinks=False)
    logger.info("model_download_done", model=MODEL_NAME)


def _check_model_files(model_dir: Path) -> bool:
    """检查模型目录是否包含必要文件"""
    required = ["config_sentence_transformers.json", "tokenizer.json", "model.safetensors"]
    return all((model_dir / f).exists() for f in required)


class EmbeddingEngine:
    """bge-large-zh-v1.5 嵌入引擎单例"""

    def __init__(self):
        self._model = None
        self._model_path = _get_model_dir()
        self._lock = threading.Lock()
        self._ready = False

    @property
    def is_ready(self) -> bool:
        return self._ready and self._model is not None

    def _ensure_model(self) -> None:
        """确保模型已下载并加载。首次调用可能阻塞（下载1.3GB）"""
        if self._ready:
            return

        with self._lock:
            if self._ready:
                return

            if not _check_model_files(self._model_path):
                logger.info("model_missing, downloading", path=str(self._model_path))
                try:
                    _download_model(self._model_path)
                except Exception as e:
                    logger.error("model_download_failed", error=str(e))
                    return

            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(str(self._model_path))
                self._ready = True
                logger.info("embedder_loaded", model=MODEL_NAME)
            except Exception as e:
                logger.error("embedder_load_failed", error=str(e))

    def encode_single(self, text: str) -> np.ndarray | None:
        """编码单条文本，返回 [1024] L2 归一化向量。模型未就绪返回 None"""
        if not self.is_ready:
            return None
        vec = self._model.encode(text, normalize_embeddings=True)
        return np.asarray(vec, dtype=np.float32)

    def encode(self, texts: list[str]) -> np.ndarray | None:
        """批量编码文本，返回 [N, 1024] L2 归一化向量"""
        if not self.is_ready:
            return None
        vecs = self._model.encode(texts, normalize_embeddings=True)
        return np.asarray(vecs, dtype=np.float32)


_embedder: EmbeddingEngine | None = None


def get_embedder() -> EmbeddingEngine:
    global _embedder
    if _embedder is None:
        _embedder = EmbeddingEngine()
    return _embedder
