import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { PersonalityCard } from "@/components/report/PersonalityCard";
import { CognitiveMap } from "@/components/report/CognitiveMap";
import { WordCloud } from "@/components/report/WordCloud";
import { TherapistNote } from "@/components/report/TherapistNote";
import { api } from "@/lib/api";

interface ReportData {
  personality_skeleton: {
    mbti_type: string;
    dimension_scores: { E_I: number; S_N: number; T_F: number; J_P: number };
    confidence: { E_I: number; S_N: number; T_F: number; J_P: number };
  };
  cognitive_map: {
    work: { E_I: number; S_N: number; T_F: number; J_P: number };
    relationship: { E_I: number; S_N: number; T_F: number; J_P: number };
    crisis: { E_I: number; S_N: number; T_F: number; J_P: number };
  };
  linguistic_sketch: {
    style_label: string;
    top_keywords: string[];
    abstract_ratio: number;
    concrete_ratio: number;
  };
  sbti_label: {
    social_survival_guide: string;
    soul_match_index: string;
  };
  therapist_note: string;
}

export default function Report() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [report, setReport] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    api.get<{ report: ReportData }>(`/report/session/${id}`)
      .then((res) => setReport(res.report))
      .catch(() => setError("报告未找到，请先完成对话"))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-cream-50 gap-4">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 animate-bounce rounded-full bg-warm-400" style={{ animationDelay: "0ms" }} />
          <div className="h-2 w-2 animate-bounce rounded-full bg-warm-400" style={{ animationDelay: "150ms" }} />
          <div className="h-2 w-2 animate-bounce rounded-full bg-warm-400" style={{ animationDelay: "300ms" }} />
        </div>
        <p className="text-sage-500">正在生成人格报告...</p>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-cream-50 px-4">
        <p className="mb-4 text-sage-500">{error || "报告未找到"}</p>
        <button onClick={() => navigate("/chat")} className="rounded-xl bg-warm-500 px-6 py-2 text-white transition-colors hover:bg-warm-600">
          开始对话
        </button>
      </div>
    );
  }

  const sk = report.personality_skeleton;
  const ls = report.linguistic_sketch;
  const sbti = report.sbti_label;

  return (
    <div className="min-h-screen bg-cream-50 px-4 py-8">
      <div className="mx-auto max-w-2xl space-y-6">
        {/* Header */}
        <div className="text-center animate-fade-in">
          <h1 className="text-2xl font-bold text-sage-800">人格分析报告</h1>
          <p className="text-sm text-sage-500">基于深度对话的倾向性分析</p>
        </div>

        {/* Personality Card */}
        <div className="stagger-item" style={{ animationDelay: "0.1s" }}>
          <PersonalityCard
            mbtiType={sk.mbti_type}
            dimensions={sk.dimension_scores}
            confidence={sk.confidence}
          />
        </div>

        {/* Cognitive Map */}
        <div className="stagger-item" style={{ animationDelay: "0.2s" }}>
          <CognitiveMap
            work={report.cognitive_map.work}
            relationship={report.cognitive_map.relationship}
            crisis={report.cognitive_map.crisis}
          />
        </div>

        {/* Word Cloud */}
        <div className="stagger-item" style={{ animationDelay: "0.3s" }}>
          <WordCloud
            keywords={ls.top_keywords}
            styleLabel={ls.style_label}
            abstractRatio={ls.abstract_ratio}
            concreteRatio={ls.concrete_ratio}
          />
        </div>

        {/* Therapist Note + SBTI */}
        <div className="stagger-item" style={{ animationDelay: "0.4s" }}>
          <TherapistNote
            note={report.therapist_note}
            socialGuide={sbti.social_survival_guide}
            soulMatch={sbti.soul_match_index}
          />
        </div>

        {/* Disclaimer */}
        <div className="stagger-item rounded-2xl border border-sage-200 bg-white p-4 text-center text-xs text-sage-400" style={{ animationDelay: "0.5s" }}>
          本报告仅为心理类型倾向参考，不能替代专业心理诊断或治疗。<br />
          如有需要，请拨打心理援助热线：12320（24小时）
        </div>

        {/* Actions */}
        <div className="stagger-item flex justify-center gap-4" style={{ animationDelay: "0.6s" }}>
          <button onClick={() => navigate("/chat")} className="rounded-xl border border-warm-500 px-6 py-2 text-sm text-warm-600 transition-colors hover:bg-warm-50">
            重新对话
          </button>
          <button onClick={() => navigate("/")} className="rounded-xl border border-sage-300 px-6 py-2 text-sm text-sage-600 transition-colors hover:bg-sage-50">
            返回首页
          </button>
        </div>
      </div>
    </div>
  );
}
