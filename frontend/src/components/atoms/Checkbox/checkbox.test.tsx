import { Checkbox, CheckboxProps } from "./checkbox";
import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";

import React from "react";

const baseProps: CheckboxProps = {
  name: "test-checkbox",
  label: "Test Label",
  checked: false,
  onChange: vi.fn(),
};

describe("Checkbox", () => {
  it("renders label", () => {
    render(<Checkbox {...baseProps} />);
    expect(screen.getByText("Test Label")).toBeInTheDocument();
  });

  it("renders spanText if provided", () => {
    render(<Checkbox {...baseProps} spanText="Extra" />);
    expect(screen.getByText("Extra")).toBeInTheDocument();
  });

  it("does not render spanText if not provided", () => {
    render(<Checkbox {...baseProps} />);
    expect(screen.queryByText("Extra")).not.toBeInTheDocument();
  });

  it("calls onChange when clicked", () => {
    const onChange = vi.fn();
    render(<Checkbox {...baseProps} onChange={onChange} />);
    const input = screen.getByRole("checkbox");
    fireEvent.click(input);
    expect(onChange).toHaveBeenCalled();
  });

  it("calls onBlur when blurred", () => {
    const onBlur = vi.fn();
    render(<Checkbox {...baseProps} onBlur={onBlur} />);
    const input = screen.getByRole("checkbox");
    fireEvent.blur(input);
    expect(onBlur).toHaveBeenCalled();
  });

  it("shows error message if error prop is provided", () => {
    render(<Checkbox {...baseProps} error="Error!" />);
    expect(screen.getByText("Error!")).toBeInTheDocument();
  });

  it("applies custom className", () => {
    render(<Checkbox {...baseProps} className="custom-class" />);
    const label = screen.getByText("Test Label").closest("label");
    expect(label?.className).toContain("custom-class");
  });
});
