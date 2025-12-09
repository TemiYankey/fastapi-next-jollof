import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import Button from "@/components/ui/Button";

describe("Button", () => {
  describe("rendering", () => {
    it("renders children correctly", () => {
      render(<Button>Click me</Button>);

      expect(screen.getByRole("button")).toHaveTextContent("Click me");
    });

    it("renders with default type button", () => {
      render(<Button>Test</Button>);

      expect(screen.getByRole("button")).toHaveAttribute("type", "button");
    });

    it("renders with submit type when specified", () => {
      render(<Button type="submit">Submit</Button>);

      expect(screen.getByRole("button")).toHaveAttribute("type", "submit");
    });

    it("renders with reset type when specified", () => {
      render(<Button type="reset">Reset</Button>);

      expect(screen.getByRole("button")).toHaveAttribute("type", "reset");
    });
  });

  describe("variants", () => {
    it("applies primary variant styles by default", () => {
      render(<Button>Primary</Button>);

      const button = screen.getByRole("button");
      expect(button.className).toContain("bg-primary");
      expect(button.className).toContain("text-white");
    });

    it("applies secondary variant styles", () => {
      render(<Button variant="secondary">Secondary</Button>);

      const button = screen.getByRole("button");
      expect(button.className).toContain("bg-muted");
      expect(button.className).toContain("text-foreground-primary");
    });

    it("applies outline variant styles", () => {
      render(<Button variant="outline">Outline</Button>);

      const button = screen.getByRole("button");
      expect(button.className).toContain("border");
      expect(button.className).toContain("bg-transparent");
    });
  });

  describe("disabled state", () => {
    it("is not disabled by default", () => {
      render(<Button>Test</Button>);

      expect(screen.getByRole("button")).not.toBeDisabled();
    });

    it("is disabled when disabled prop is true", () => {
      render(<Button disabled>Disabled</Button>);

      expect(screen.getByRole("button")).toBeDisabled();
    });

    it("applies disabled styles", () => {
      render(<Button disabled>Disabled</Button>);

      const button = screen.getByRole("button");
      expect(button.className).toContain("disabled:opacity-50");
      expect(button.className).toContain("disabled:cursor-not-allowed");
    });
  });

  describe("loading state", () => {
    it("shows loading indicator when loading", () => {
      render(<Button loading>Submit</Button>);

      expect(screen.getByRole("button")).toHaveTextContent("Loading...");
    });

    it("is disabled when loading", () => {
      render(<Button loading>Submit</Button>);

      expect(screen.getByRole("button")).toBeDisabled();
    });

    it("shows spinner when loading", () => {
      render(<Button loading>Submit</Button>);

      // Check for spinner element (animate-spin class)
      const button = screen.getByRole("button");
      expect(button.innerHTML).toContain("animate-spin");
    });

    it("hides children content when loading", () => {
      render(<Button loading>Submit Form</Button>);

      expect(screen.getByRole("button")).not.toHaveTextContent("Submit Form");
      expect(screen.getByRole("button")).toHaveTextContent("Loading...");
    });
  });

  describe("click handling", () => {
    it("calls onClick when clicked", () => {
      const handleClick = vi.fn();
      render(<Button onClick={handleClick}>Click me</Button>);

      fireEvent.click(screen.getByRole("button"));

      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it("does not call onClick when disabled", () => {
      const handleClick = vi.fn();
      render(
        <Button onClick={handleClick} disabled>
          Click me
        </Button>
      );

      fireEvent.click(screen.getByRole("button"));

      expect(handleClick).not.toHaveBeenCalled();
    });

    it("does not call onClick when loading", () => {
      const handleClick = vi.fn();
      render(
        <Button onClick={handleClick} loading>
          Click me
        </Button>
      );

      fireEvent.click(screen.getByRole("button"));

      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  describe("custom className", () => {
    it("applies custom className", () => {
      render(<Button className="custom-class">Test</Button>);

      expect(screen.getByRole("button")).toHaveClass("custom-class");
    });

    it("combines custom className with default styles", () => {
      render(<Button className="my-custom-class">Test</Button>);

      const button = screen.getByRole("button");
      expect(button.className).toContain("my-custom-class");
      expect(button.className).toContain("rounded-xl");
    });
  });

  describe("accessibility", () => {
    it("is keyboard accessible", () => {
      const handleClick = vi.fn();
      render(<Button onClick={handleClick}>Test</Button>);

      const button = screen.getByRole("button");
      button.focus();

      expect(document.activeElement).toBe(button);
    });
  });
});
