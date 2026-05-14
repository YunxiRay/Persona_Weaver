import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { PhaseIndicator } from "@/components/chat/PhaseIndicator";

describe("PhaseIndicator", () => {
  describe("RAPPORT phase", () => {
    it("shows first phase active", () => {
      render(<PhaseIndicator phase="RAPPORT" phaseLabel="正在建立连接..." turn={5} />);
      expect(screen.getByText("正在建立连接...")).toBeInTheDocument();
      expect(screen.getByText("破冰暖场")).toBeInTheDocument();
    });
  });

  describe("EXPLORATION phase", () => {
    it("shows second phase active", () => {
      render(<PhaseIndicator phase="EXPLORATION" phaseLabel="深入探索中..." turn={10} />);
      expect(screen.getByText("深入探索中...")).toBeInTheDocument();
      expect(screen.getByText("情境隐喻")).toBeInTheDocument();
    });
  });

  describe("CONFRONTATION phase", () => {
    it("shows third phase active", () => {
      render(<PhaseIndicator phase="CONFRONTATION" phaseLabel="核心对峙..." turn={20} />);
      expect(screen.getByText("核心对峙...")).toBeInTheDocument();
      expect(screen.getByText("两难困境")).toBeInTheDocument();
    });
  });

  describe("SYNTHESIS phase", () => {
    it("shows fourth phase active", () => {
      render(<PhaseIndicator phase="SYNTHESIS" phaseLabel="整理画像..." turn={40} />);
      expect(screen.getByText("整理画像...")).toBeInTheDocument();
      expect(screen.getByText("镜像校准")).toBeInTheDocument();
    });
  });

  describe("phase icons", () => {
    it("renders all four phase step numbers", () => {
      render(<PhaseIndicator phase="RAPPORT" phaseLabel="连接中" turn={0} />);
      expect(screen.getByText("1")).toBeInTheDocument();
      expect(screen.getByText("2")).toBeInTheDocument();
      expect(screen.getByText("3")).toBeInTheDocument();
      expect(screen.getByText("4")).toBeInTheDocument();
    });
  });
});
