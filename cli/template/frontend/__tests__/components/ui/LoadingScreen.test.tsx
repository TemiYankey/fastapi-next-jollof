import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LoadingScreen } from "@/components/ui/LoadingScreen";

// Mock config
vi.mock("@/lib/config", () => ({
  config: {
    appName: "Test App",
  },
}));

describe("LoadingScreen", () => {
  describe("rendering", () => {
    it("renders with default message", () => {
      render(<LoadingScreen />);

      expect(screen.getByText("Loading Test App...")).toBeInTheDocument();
    });

    it("renders with custom message", () => {
      render(<LoadingScreen message="Please wait..." />);

      expect(screen.getByText("Please wait...")).toBeInTheDocument();
    });

    it("does not show default message when custom provided", () => {
      render(<LoadingScreen message="Custom loading" />);

      expect(screen.queryByText("Loading Test App...")).not.toBeInTheDocument();
      expect(screen.getByText("Custom loading")).toBeInTheDocument();
    });
  });

  describe("spinner", () => {
    it("shows loading spinner", () => {
      const { container } = render(<LoadingScreen />);

      const spinner = container.querySelector(".animate-spin");
      expect(spinner).toBeInTheDocument();
    });
  });

  describe("layout", () => {
    it("has fixed positioning", () => {
      const { container } = render(<LoadingScreen />);

      const wrapper = container.firstChild;
      expect(wrapper).toHaveClass("fixed");
      expect(wrapper).toHaveClass("inset-0");
    });

    it("has high z-index", () => {
      const { container } = render(<LoadingScreen />);

      const wrapper = container.firstChild;
      expect(wrapper).toHaveClass("z-50");
    });

    it("centers content", () => {
      const { container } = render(<LoadingScreen />);

      const wrapper = container.firstChild;
      expect(wrapper).toHaveClass("flex");
      expect(wrapper).toHaveClass("items-center");
      expect(wrapper).toHaveClass("justify-center");
    });
  });
});
