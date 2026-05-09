import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { TherapistNote } from "@/components/report/TherapistNote";

describe("TherapistNote", () => {
  it("renders the therapist note text", () => {
    render(
      <TherapistNote
        note="你是一个内向直觉型的人，在与世界互动时倾向于深思熟虑。"
        socialGuide="在社交场合给自己留出独处恢复的时间"
        soulMatch="ENFP — 互补的能量来源"
      />
    );
    expect(screen.getByText("心理医生寄语")).toBeInTheDocument();
    expect(screen.getByText(/内向直觉型/)).toBeInTheDocument();
  });

  it("renders SBTI social guide and soul match", () => {
    render(
      <TherapistNote
        note="测试寄语"
        socialGuide="社交生存指南测试"
        soulMatch="灵魂合拍指数测试"
      />
    );
    expect(screen.getByText("社交生存指南")).toBeInTheDocument();
    expect(screen.getByText("社交生存指南测试")).toBeInTheDocument();
    expect(screen.getByText("灵魂合拍指数")).toBeInTheDocument();
    expect(screen.getByText("灵魂合拍指数测试")).toBeInTheDocument();
  });
});
