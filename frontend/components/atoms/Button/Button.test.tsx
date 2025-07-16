import "@testing-library/jest-dom";

import { Button, ButtonVarinat } from "./Button";
import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";

import React from "react";

describe("Button", () => {
  it("renders children", () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText("Click me")).toBeInTheDocument();
  });

  it("calls onClick when clicked", () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click</Button>);
    fireEvent.click(screen.getByText("Click"));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it("applies primary variant styles by default", () => {
    render(<Button>Primary</Button>);
    const button = screen.getByRole("button");
    expect(button.className).toContain("bg-blue-500");
  });

  it("applies secondary variant styles", () => {
    render(<Button variant={ButtonVarinat.secondary}>Secondary</Button>);
    const button = screen.getByRole("button");
    expect(button.className).toContain("bg-gray-200");
  });

  it("passes additional props", () => {
    render(<Button data-testid="custom-btn">Test</Button>);
    expect(screen.getByTestId("custom-btn")).toBeInTheDocument();
  });
});
