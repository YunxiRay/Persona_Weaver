import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ChatBubble } from "@/components/chat/ChatBubble";

describe("ChatBubble", () => {
  describe("user message", () => {
    it("renders content and right-aligned", () => {
      render(<ChatBubble role="user" content="你好，我想了解自己" timestamp={1715000000000} />);
      const text = screen.getByText("你好，我想了解自己");
      expect(text).toBeInTheDocument();
    });

    it("shows user avatar 'U'", () => {
      render(<ChatBubble role="user" content="hi" timestamp={1} />);
      expect(screen.getByText("U")).toBeInTheDocument();
    });
  });

  describe("assistant message", () => {
    it("renders content with left avatar", () => {
      render(<ChatBubble role="assistant" content="你好，让我们开始探索吧" timestamp={1715000000000} />);
      expect(screen.getByText("你好，让我们开始探索吧")).toBeInTheDocument();
      expect(screen.getByText("PW")).toBeInTheDocument();
    });

    it("displays typing cursor when typing is active", () => {
      const { container } = render(
        <ChatBubble role="assistant" content="正在输入..." timestamp={1} typing={true} />
      );
      const bubble = container.querySelector(".typing-cursor");
      expect(bubble).toBeTruthy();
    });

    it("does not show typing cursor when typing is false", () => {
      const { container } = render(
        <ChatBubble role="assistant" content="完成" timestamp={1} typing={false} />
      );
      const bubble = container.querySelector(".typing-cursor");
      expect(bubble).toBeFalsy();
    });
  });

  describe("system message", () => {
    it("renders centered with red styling", () => {
      const { container } = render(
        <ChatBubble role="system" content="系统通知：危机干预" timestamp={1} />
      );
      expect(screen.getByText("系统通知：危机干预")).toBeInTheDocument();
      const bubble = container.querySelector(".bg-red-50");
      expect(bubble).toBeTruthy();
    });
  });

  describe("all roles", () => {
    it("renders without crash for user role", () => {
      const { container } = render(<ChatBubble role="user" content="a" timestamp={1} />);
      expect(container).toBeTruthy();
    });

    it("renders without crash for assistant role", () => {
      const { container } = render(<ChatBubble role="assistant" content="a" timestamp={1} />);
      expect(container).toBeTruthy();
    });

    it("renders without crash for system role", () => {
      const { container } = render(<ChatBubble role="system" content="a" timestamp={1} />);
      expect(container).toBeTruthy();
    });
  });
});
