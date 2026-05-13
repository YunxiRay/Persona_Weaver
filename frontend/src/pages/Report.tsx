import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import html2canvas from "html2canvas";
import { jsPDF } from "jspdf";
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
  const [exportToast, setExportToast] = useState("");
  const reportRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!id) return;
    api.get<{ report: ReportData }>(`/report/session/${id}`)
      .then((res) => setReport(res.report))
      .catch(() => setError("报告未找到，请先完成对话"))
      .finally(() => setLoading(false));
  }, [id]);

  const showToast = useCallback((msg: string) => {
    setExportToast(msg);
    setTimeout(() => setExportToast(""), 3000);
  }, []);

  const exportAsPNG = useCallback(async () => {
    if (!reportRef.current || !id || !report) return;
    try {
      const mbti = report.personality_skeleton.mbti_type;
      const canvas = await html2canvas(reportRef.current, { scale: 2, backgroundColor: "#FFFDF7" });
      canvas.toBlob((blob) => {
        if (!blob) return;
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `人格分析报告_${mbti}_${new Date().toISOString().slice(0, 10)}.png`;
        a.click();
        URL.revokeObjectURL(url);
        showToast("报告已导出为 PNG，请查看浏览器下载文件夹");
      }, "image/png");
    } catch {
      showToast("导出失败，请重试");
    }
  }, [id, report, showToast]);

  const exportAsPDF = useCallback(async () => {
    if (!reportRef.current || !id || !report) return;
    try {
      const mbti = report.personality_skeleton.mbti_type;
      const canvas = await html2canvas(reportRef.current, { scale: 2, backgroundColor: "#FFFDF7" });
      const imgData = canvas.toDataURL("image/png");
      const pdf = new jsPDF("p", "mm", "a4");
      const imgWidth = 210;
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      let heightLeft = imgHeight;
      let position = 0;

      pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight);
      heightLeft -= 297;
      while (heightLeft > 0) {
        position = -(imgHeight - heightLeft);
        pdf.addPage();
        pdf.addImage(imgData, "PNG", 0, position, imgWidth, imgHeight);
        heightLeft -= 297;
      }
      pdf.save(`人格分析报告_${mbti}_${new Date().toISOString().slice(0, 10)}.pdf`);
      showToast("报告已导出为 PDF，请查看浏览器下载文件夹");
    } catch {
      showToast("导出失败，请重试");
    }
  }, [id, report, showToast]);

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
      {exportToast && (
        <div className="fixed left-1/2 top-4 z-50 -translate-x-1/2 animate-slide-down rounded-xl bg-green-50 border border-green-200 px-5 py-3 shadow-lg">
          <p className="text-sm text-green-700">{exportToast}</p>
        </div>
      )}
      <div ref={reportRef} className="mx-auto max-w-2xl space-y-6">
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
        <div className="stagger-item flex flex-col items-center gap-3" style={{ animationDelay: "0.6s" }}>
          <div className="flex justify-center gap-4">
            <button onClick={() => navigate("/chat")} className="rounded-xl border border-warm-500 px-6 py-2 text-sm text-warm-600 transition-colors hover:bg-warm-50">
              重新对话
            </button>
            <button
              onClick={exportAsPNG}
              className="rounded-xl bg-warm-500 px-6 py-2 text-sm text-white transition-colors hover:bg-warm-600"
            >
              导出为图片
            </button>
            <button
              onClick={exportAsPDF}
              className="rounded-xl bg-sage-700 px-6 py-2 text-sm text-white transition-colors hover:bg-sage-800"
            >
              导出为 PDF
            </button>
            <button onClick={() => navigate("/")} className="rounded-xl border border-sage-300 px-6 py-2 text-sm text-sage-600 transition-colors hover:bg-sage-50">
              返回首页
            </button>
          </div>
          <p className="text-xs text-sage-400">导出为高清 PNG 图片或 A4 PDF 文件，方便保存和分享</p>
        </div>
      </div>
    </div>
  );
}
