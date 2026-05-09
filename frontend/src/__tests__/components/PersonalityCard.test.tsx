import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { PersonalityCard } from "@/components/report/PersonalityCard";

const sampleDimensions = { E_I: 0.3, S_N: -0.5, T_F: 0.8, J_P: -0.2 };
const sampleConfidence = { E_I: 0.85, S_N: 0.72, T_F: 0.91, J_P: 0.68 };

describe("PersonalityCard", () => {
  it("displays MBTI type prominently", () => {
    render(<PersonalityCard mbtiType="INFJ" dimensions={sampleDimensions} confidence={sampleConfidence} />);
    expect(screen.getByText("INFJ")).toBeInTheDocument();
  });

  it("shows all four dimension labels", () => {
    render(<PersonalityCard mbtiType="ENFP" dimensions={sampleDimensions} confidence={sampleConfidence} />);
    expect(screen.getByText("内向 (I)")).toBeInTheDocument();
    expect(screen.getByText("外向 (E)")).toBeInTheDocument();
    expect(screen.getByText("直觉 (N)")).toBeInTheDocument();
    expect(screen.getByText("实感 (S)")).toBeInTheDocument();
    expect(screen.getByText("思维 (T)")).toBeInTheDocument();
    expect(screen.getByText("情感 (F)")).toBeInTheDocument();
    expect(screen.getByText("感知 (P)")).toBeInTheDocument();
    expect(screen.getByText("判断 (J)")).toBeInTheDocument();
  });

  it("shows confidence percentages", () => {
    render(<PersonalityCard mbtiType="ISTJ" dimensions={sampleDimensions} confidence={sampleConfidence} />);
    expect(screen.getByText(/85%/)).toBeInTheDocument();
    expect(screen.getByText(/72%/)).toBeInTheDocument();
  });

  it("handles extreme dimension values", () => {
    const extreme = { E_I: 1.0, S_N: -1.0, T_F: 1.0, J_P: -1.0 };
    const highConf = { E_I: 1.0, S_N: 1.0, T_F: 1.0, J_P: 1.0 };
    render(<PersonalityCard mbtiType="ESTJ" dimensions={extreme} confidence={highConf} />);
    expect(screen.getByText("ESTJ")).toBeInTheDocument();
  });
});
