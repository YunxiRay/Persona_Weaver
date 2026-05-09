"""语义指纹分析 — TF-IDF 关键词提取 + 抽象/具象词分析"""

import math
import re
from collections import Counter

import jieba
import structlog

logger = structlog.get_logger(__name__)

# 中文停用词
STOP_WORDS: set[str] = {
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一",
    "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着",
    "没有", "看", "好", "自己", "这", "他", "她", "它", "们", "那", "些",
    "什么", "怎么", "如果", "因为", "所以", "但是", "然后", "可以", "这个",
    "那个", "还是", "只是", "的话", "吧", "吗", "呢", "啊", "哦", "嗯",
    "可能", "应该", "觉得", "知道", "想", "让", "被", "把", "对", "从",
    "过", "更", "还", "已经", "没", "比较", "非常", "真的", "像", "做",
    "能", "会", "比较", "就是", "其实", "而且", "或者", "虽然", "不过",
}

# 中文抽象词（部分词表）
ABSTRACT_WORDS: set[str] = {
    "自由", "幸福", "意义", "理想", "未来", "梦想", "灵魂", "价值",
    "永恒", "无限", "可能", "希望", "信念", "真理", "本质", "精神",
    "意识", "存在", "人生", "命运", "自我", "内心", "感觉", "感受",
    "情绪", "思维", "思想", "观念", "理念", "哲学", "原则", "信仰",
    "爱", "恨", "美", "善", "真", "和平", "正义", "公平", "平等",
    "智慧", "知识", "力量", "勇气", "坚持", "努力", "成功", "成长",
    "关系", "信任", "尊重", "理解", "包容", "关怀", "温暖", "孤独",
    "焦虑", "恐惧", "期待", "渴望", "追求", "探索", "创造", "改变",
}

# 中文具象词（部分词表）
CONCRETE_WORDS: set[str] = {
    "桌子", "椅子", "电脑", "手机", "汽车", "房子", "门", "窗户",
    "书", "笔", "纸", "杯子", "水", "饭", "菜", "衣服", "鞋子",
    "路", "树", "花", "草", "山", "河", "海", "天空", "太阳",
    "猫", "狗", "鸟", "鱼", "车", "地铁", "公交", "自行车",
    "办公室", "教室", "厨房", "卧室", "客厅", "厕所", "电梯",
    "键盘", "鼠标", "屏幕", "耳机", "充电器", "数据线",
    "咖啡", "茶", "牛奶", "面包", "米饭", "面条", "水果",
    "医生", "老师", "朋友", "父母", "孩子", "同事", "老板",
    "钱", "工资", "房租", "超市", "医院", "学校", "公司",
    "早上", "晚上", "今天", "昨天", "明天", "星期", "月份",
}


def tokenize(text: str) -> list[str]:
    words = jieba.lcut(text)
    return [w.strip() for w in words if len(w.strip()) >= 2 and w.strip() not in STOP_WORDS]


def extract_keywords(messages: list[str], top_n: int = 20) -> list[tuple[str, float]]:
    """TF-IDF 变体提取核心关键词"""
    if not messages:
        return []

    # Tokenize all messages
    doc_tokens: list[list[str]] = [tokenize(m) for m in messages]
    doc_count = len(doc_tokens)

    # Compute document frequencies
    df: dict[str, int] = Counter()
    tf: dict[str, float] = Counter()
    for tokens in doc_tokens:
        unique = set(tokens)
        for w in unique:
            df[w] += 1
        for w in tokens:
            tf[w] += 1

    # TF-IDF scoring
    scores: dict[str, float] = {}
    total_terms = sum(tf.values())
    for word, freq in tf.items():
        if df[word] <= 1:  # 只出现在一个文档中的词权重更低 (IDF effect)
            continue
        tf_score = freq / total_terms
        idf_score = math.log((doc_count + 1) / (df[word] + 1)) + 1
        scores[word] = tf_score * idf_score

    return Counter(scores).most_common(top_n)


def analyze_abstract_concrete_ratio(text: str) -> dict:
    """分析文本的抽象/具象词比例"""
    words = tokenize(text)
    if not words:
        return {"abstract_ratio": 0.5, "concrete_ratio": 0.5, "abstract_count": 0, "concrete_count": 0}

    abstract_count = sum(1 for w in words if w in ABSTRACT_WORDS)
    concrete_count = sum(1 for w in words if w in CONCRETE_WORDS)
    total_classified = abstract_count + concrete_count

    if total_classified == 0:
        return {"abstract_ratio": 0.5, "concrete_ratio": 0.5, "abstract_count": 0, "concrete_count": 0}

    return {
        "abstract_ratio": round(abstract_count / total_classified, 3),
        "concrete_ratio": round(concrete_count / total_classified, 3),
        "abstract_count": abstract_count,
        "concrete_count": concrete_count,
    }


def compute_sn_aux_signal(abstract_ratio: float) -> float:
    """根据抽象词比例计算 S/N 维度辅助信号（>0.5 偏 N 直觉型）"""
    # 抽象词比例越高 → 越偏 N（直觉型）
    signal = (abstract_ratio - 0.5) * 2.0  # 映射到 [-1, 1]
    return max(-1.0, min(1.0, signal))
