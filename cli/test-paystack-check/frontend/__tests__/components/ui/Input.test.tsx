import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import Input from "@/components/ui/Input";

describe("Input", () => {
  describe("rendering", () => {
    it("renders with label", () => {
      render(
        <Input
          name="email"
          label="Email"
          value=""
          onChange={() => {}}
        />
      );

      expect(screen.getByLabelText("Email")).toBeInTheDocument();
    });

    it("renders with correct input type", () => {
      render(
        <Input
          name="password"
          label="Password"
          type="password"
          value=""
          onChange={() => {}}
        />
      );

      expect(screen.getByLabelText("Password")).toHaveAttribute(
        "type",
        "password"
      );
    });

    it("renders with default type text", () => {
      render(
        <Input
          name="username"
          label="Username"
          value=""
          onChange={() => {}}
        />
      );

      expect(screen.getByLabelText("Username")).toHaveAttribute("type", "text");
    });

    it("renders with placeholder", () => {
      render(
        <Input
          name="email"
          label="Email"
          value=""
          onChange={() => {}}
          placeholder="Enter your email"
        />
      );

      expect(
        screen.getByPlaceholderText("Enter your email")
      ).toBeInTheDocument();
    });

    it("renders with value", () => {
      render(
        <Input
          name="email"
          label="Email"
          value="test@example.com"
          onChange={() => {}}
        />
      );

      expect(screen.getByLabelText("Email")).toHaveValue("test@example.com");
    });
  });

  describe("required field", () => {
    it("shows required indicator when required", () => {
      render(
        <Input
          name="email"
          label="Email"
          value=""
          onChange={() => {}}
          required
        />
      );

      // Check for required asterisk
      expect(screen.getByText("*")).toBeInTheDocument();
    });

    it("sets required attribute on input", () => {
      render(
        <Input
          name="email"
          label="Email"
          value=""
          onChange={() => {}}
          required
        />
      );

      expect(screen.getByLabelText(/Email/)).toBeRequired();
    });

    it("does not show required indicator when not required", () => {
      render(
        <Input
          name="email"
          label="Email"
          value=""
          onChange={() => {}}
        />
      );

      expect(screen.queryByText("*")).not.toBeInTheDocument();
    });
  });

  describe("disabled state", () => {
    it("is not disabled by default", () => {
      render(
        <Input
          name="email"
          label="Email"
          value=""
          onChange={() => {}}
        />
      );

      expect(screen.getByLabelText("Email")).not.toBeDisabled();
    });

    it("is disabled when disabled prop is true", () => {
      render(
        <Input
          name="email"
          label="Email"
          value=""
          onChange={() => {}}
          disabled
        />
      );

      expect(screen.getByLabelText("Email")).toBeDisabled();
    });
  });

  describe("onChange handling", () => {
    it("calls onChange when value changes", () => {
      const handleChange = vi.fn();
      render(
        <Input
          name="email"
          label="Email"
          value=""
          onChange={handleChange}
        />
      );

      fireEvent.change(screen.getByLabelText("Email"), {
        target: { value: "new@example.com" },
      });

      expect(handleChange).toHaveBeenCalledWith("new@example.com");
    });
  });

  describe("error state", () => {
    it("shows error message when error prop is provided", () => {
      render(
        <Input
          name="email"
          label="Email"
          value=""
          onChange={() => {}}
          error="Invalid email address"
        />
      );

      expect(screen.getByText("Invalid email address")).toBeInTheDocument();
    });

    it("applies error styling when error is present", () => {
      render(
        <Input
          name="email"
          label="Email"
          value=""
          onChange={() => {}}
          error="Invalid email"
        />
      );

      const input = screen.getByLabelText("Email");
      expect(input.className).toContain("border-red-500");
    });

    it("does not show error message when no error", () => {
      render(
        <Input
          name="email"
          label="Email"
          value=""
          onChange={() => {}}
        />
      );

      expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    });
  });

  describe("password toggle", () => {
    it("shows password toggle button when showPasswordToggle is true", () => {
      render(
        <Input
          name="password"
          label="Password"
          type="password"
          value=""
          onChange={() => {}}
          showPasswordToggle
        />
      );

      expect(screen.getByRole("button")).toBeInTheDocument();
    });

    it("does not show toggle button by default", () => {
      render(
        <Input
          name="password"
          label="Password"
          type="password"
          value=""
          onChange={() => {}}
        />
      );

      expect(screen.queryByRole("button")).not.toBeInTheDocument();
    });

    it("toggles password visibility on click", () => {
      render(
        <Input
          name="password"
          label="Password"
          type="password"
          value="secret"
          onChange={() => {}}
          showPasswordToggle
        />
      );

      const input = screen.getByLabelText("Password");
      const toggleButton = screen.getByRole("button");

      // Initially password type
      expect(input).toHaveAttribute("type", "password");

      // Click to show password
      fireEvent.click(toggleButton);
      expect(input).toHaveAttribute("type", "text");

      // Click again to hide password
      fireEvent.click(toggleButton);
      expect(input).toHaveAttribute("type", "password");
    });

    it("toggle button does not submit form", () => {
      render(
        <Input
          name="password"
          label="Password"
          type="password"
          value=""
          onChange={() => {}}
          showPasswordToggle
        />
      );

      const toggleButton = screen.getByRole("button");
      expect(toggleButton).toHaveAttribute("type", "button");
    });
  });

  describe("accessibility", () => {
    it("has correct id matching label htmlFor", () => {
      render(
        <Input
          name="test-input"
          label="Test Label"
          value=""
          onChange={() => {}}
        />
      );

      const input = screen.getByLabelText("Test Label");
      expect(input).toHaveAttribute("id", "test-input");
    });

    it("can be focused", () => {
      render(
        <Input
          name="email"
          label="Email"
          value=""
          onChange={() => {}}
        />
      );

      const input = screen.getByLabelText("Email");
      input.focus();

      expect(document.activeElement).toBe(input);
    });
  });
});
