"""种子数据导入脚本 — 将 patterns.json 导入数据库并计算向量。
运行方式: cd backend && poetry run python scripts/seed_patterns.py
"""

import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


async def seed_patterns():
    from sqlalchemy import func, select

    from app.core.database import get_session_factory
    from app.llm.embedder import get_embedder
    from app.models.psychology_pattern import PsychologyPattern
    from app.services.pattern_service import PatternService, get_retriever

    # 加载种子数据
    seed_path = Path(__file__).resolve().parent.parent / "seed_data" / "patterns.json"
    if not seed_path.exists():
        print(f"种子数据文件不存在: {seed_path}")
        return

    with open(seed_path, "r", encoding="utf-8") as f:
        patterns_data = json.load(f)

    print(f"加载了 {len(patterns_data)} 条种子模式")

    # 加载嵌入模型
    embedder = get_embedder()
    embedder._ensure_model()
    if not embedder.is_ready:
        print("嵌入模型未就绪，将存储不含向量的模式（需后续重新种子）")

    factory = get_session_factory()
    async with factory() as db:
        # 检查是否已有数据（幂等）
        result = await db.execute(select(func.count()).select_from(PsychologyPattern))
        count = result.scalar()
        if count > 0:
            print(f"数据库已有 {count} 条模式，跳过（如需重新导入请先清空表）")
            return

        svc = PatternService(db)
        imported = 0

        for p in patterns_data:
            vector_data = None
            if embedder.is_ready:
                vec = embedder.encode_single(p["pattern_text"])
                if vec is not None:
                    vector_data = vec.tolist()

            try:
                await svc.create(**{**p, "vector_data": vector_data})
                imported += 1
            except Exception as e:
                print(f"  导入失败 [{p['name']}]: {e}")

        print(f"成功导入 {imported}/{len(patterns_data)} 条模式")

        # 构建检索索引
        retriever = get_retriever()
        await retriever.build_index(db)
        print(f"检索索引已构建，共 {len(retriever._patterns)} 条向量")


if __name__ == "__main__":
    asyncio.run(seed_patterns())
