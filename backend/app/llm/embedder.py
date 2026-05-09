from sentence_transformers import SentenceTransformer

from app.core.config import settings

_embedder: SentenceTransformer | None = None


def get_embedder() -> SentenceTransformer:
    """单例模式加载 bge-large-zh-v1.5 嵌入模型"""
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    return _embedder


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """将文本列表转换为 1024 维向量"""
    model = get_embedder()
    embeddings = model.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()


async def embed_single(text: str) -> list[float]:
    """将单条文本转换为 1024 维向量"""
    results = await embed_texts([text])
    return results[0]
