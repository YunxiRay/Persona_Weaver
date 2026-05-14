"""快速推理测试脚本 — 直接调 debug 接口"""
import json, time, requests

API = "http://localhost:8000/api/v1/debug/inference-test"

body = {
    "provider": "deepseek",
    "api_key": "sk-7e8eb5c07a494460a1cb682ccf275428",
    "model": "deepseek-v4-pro",
    "base_url": "https://api.deepseek.com",
    "messages": [
        "我平时比较喜欢一个人待着，周末也不太爱出门",
        "工作的时候我更关注整体方向而不是细节",
        "做决定时我更多靠直觉而不是逻辑分析",
        "我的生活比较随性，不太喜欢做计划",
        "其实我挺感性的，看个电影都能哭",
        "和人相处时我更在意对方的感受",
        "我不喜欢被规则束缚，自由最重要",
        "遇到压力时我倾向于逃避而不是直面",
    ],
}

t0 = time.perf_counter()
resp = requests.post(API, json=body, timeout=300)
data = resp.json()
elapsed = time.perf_counter() - t0

print(f"耗时: {elapsed:.1f}s | 最终MBTI: {data['final_mbti']}")
print(f"MBTI历史: {data['mbti_history']}")
print(f"稳定轮数: {data['mbti_stable_rounds']} | 收敛于: {data['converged_at_round']}")
print()

for r in data["rounds"]:
    llm = r["llm_raw_dimensions"]
    bayes = r["bayesian_scores"]
    std = r["bayesian_std"]
    print(f"轮次{r['turn']:2d} | 阶段:{r['phase']:12s} | LLM原始:[E_I={llm['E_I']:5.2f} S_N={llm['S_N']:5.2f} T_F={llm['T_F']:5.2f} J_P={llm['J_P']:5.2f}]")
    print(f"      | {'':12s} | Bayes: [E_I={bayes['E_I']:5.2f} S_N={bayes['S_N']:5.2f} T_F={bayes['T_F']:5.2f} J_P={bayes['J_P']:5.2f}]")
    print(f"      | {'':12s} | Std:   [E_I={std['E_I']:.4f} S_N={std['S_N']:.4f} T_F={std['T_F']:.4f} J_P={std['J_P']:.4f}]")
    print(f"      | MBTI:{r['mbti']:5s} | 防御:{r['defense_flags']} | 收敛:{r['is_converged']}")
    if r["doctor_reply"]:
        print(f"      | 回复: {r['doctor_reply'][:80]}...")
    print()

print(f"\n认知地图: work={data['cognitive_map']['work']}")
